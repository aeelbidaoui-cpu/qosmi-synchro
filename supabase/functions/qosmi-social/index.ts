// Qosmi : publication Facebook + Instagram directement chez Meta (gratuit), à l'heure exacte.
// Demande d'Amine du 26/11/2026 : « tout automatiser via Meta ce qui est possible gratuitement », Zernio gardé pour TikTok.
//
// - POST ?action=ajouter : les robots GitHub (scripts/social_publier.py, scripts/social_stories.py) déposent les
//   publications et stories à venir dans la file (table qosmi_social_file). Authentification : jeton OIDC de GitHub
//   Actions, vérifié ici (dépôt aeelbidaoui-cpu/qosmi-synchro, audience qosmi-social) : aucun secret partagé.
// - POST ?action=publier : appelé toutes les 5 minutes par pg_cron (en-tête x-cle = réglage social_cle) ; publie ce qui
//   est échu : Instagram (photo, carrousel, story) et Facebook (photo(s), story photo).
// - GET ?action=etat (en-tête x-cle) : vérifie le jeton Meta (page, Instagram) et montre la file.
// Jeton Meta : secret Supabase META_TOKEN (utilisateur système qosmi-bot, page Qosmi + compte Instagram qosmi.be).
import { createClient } from "jsr:@supabase/supabase-js@2";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5.9.6";

const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const GRAPH = "https://graph.facebook.com/v23.0";
const DEPOT = "aeelbidaoui-cpu/qosmi-synchro";
const JWKS = createRemoteJWKSet(new URL("https://token.actions.githubusercontent.com/.well-known/jwks"));
const MAX_ESSAIS = 4;

const json = (d: unknown, status = 200) =>
  new Response(JSON.stringify(d, null, 1), { status, headers: { "content-type": "application/json; charset=utf-8" } });

function jeton(): string {
  return (Deno.env.get("META_TOKEN") || Deno.env.get("WA_TOKEN") || "").replace(/\s+/g, "");
}

async function reglage(cle: string): Promise<string | null> {
  const { data } = await db.from("qosmi_wa_reglages").select("valeur").eq("cle", cle).maybeSingle();
  return data?.valeur ?? null;
}

async function cleOk(req: Request): Promise<boolean> {
  const attendue = await reglage("social_cle");
  return !!attendue && req.headers.get("x-cle") === attendue;
}

async function githubOk(req: Request): Promise<string | null> {
  const t = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!t) return "jeton GitHub absent";
  try {
    const { payload } = await jwtVerify(t, JWKS, { issuer: "https://token.actions.githubusercontent.com", audience: "qosmi-social" });
    if (payload.repository !== DEPOT) return "dépôt refusé";
    return null;
  } catch (e) {
    return "jeton GitHub invalide : " + (e as Error).message;
  }
}

async function graph(methode: "GET" | "POST", chemin: string, tok: string, params: Record<string, string> = {}) {
  const corps = new URLSearchParams({ ...params, access_token: tok });
  for (let essai = 0; essai < 4; essai++) {
    const r = methode === "GET"
      ? await fetch(`${GRAPH}${chemin}?${corps}`)
      : await fetch(`${GRAPH}${chemin}`, { method: "POST", body: corps });
    const d = await r.json().catch(() => ({}));
    if (r.ok) return d;
    const transitoire = r.status >= 500 || d?.error?.is_transient;
    if (!transitoire || essai === 3) throw new Error(`Meta ${methode} ${chemin} → ${r.status} ${JSON.stringify(d?.error || d).slice(0, 400)}`);
    await new Promise((s) => setTimeout(s, 4000 * (essai + 1)));
  }
  throw new Error("Meta : échec");
}

type Comptes = { page: string; jetonPage: string; ig: string | null; nom: string; igNom?: string };

async function comptes(tok: string): Promise<Comptes> {
  const d = await graph("GET", "/me/accounts", tok, { fields: "id,name,access_token,instagram_business_account{id,username}" });
  const p = (d.data || []).find((x: any) => String(x.name).trim().toLowerCase() === "qosmi") || (d.data || [])[0];
  if (!p) throw new Error("Aucune page Facebook pour ce jeton (page Qosmi à affecter à l'utilisateur système qosmi-bot)");
  return { page: p.id, jetonPage: p.access_token, ig: p.instagram_business_account?.id || null, nom: p.name, igNom: p.instagram_business_account?.username };
}

async function attendreConteneur(id: string, tok: string) {
  for (let i = 0; i < 24; i++) {
    const s = (await graph("GET", `/${id}`, tok, { fields: "status_code" })).status_code;
    if (s === "FINISHED") return;
    if (s === "ERROR" || s === "EXPIRED") throw new Error(`Instagram a refusé le visuel (${s})`);
    await new Promise((r) => setTimeout(r, 3000));
  }
  throw new Error("Instagram : préparation trop longue");
}

async function instagram(c: Comptes, tok: string, it: any): Promise<string> {
  if (!c.ig) throw new Error("Aucun compte Instagram relié à la page");
  const imgs: string[] = it.images || [];
  let cont: string;
  if (it.type === "story") {
    cont = (await graph("POST", `/${c.ig}/media`, tok, { image_url: imgs[0], media_type: "STORIES" })).id;
  } else if (imgs.length === 1) {
    cont = (await graph("POST", `/${c.ig}/media`, tok, { image_url: imgs[0], caption: it.legende_ig || "" })).id;
  } else {
    const enfants: string[] = [];
    for (const u of imgs.slice(0, 10)) {
      const e = (await graph("POST", `/${c.ig}/media`, tok, { image_url: u, is_carousel_item: "true" })).id;
      await attendreConteneur(e, tok);
      enfants.push(e);
    }
    cont = (await graph("POST", `/${c.ig}/media`, tok, { media_type: "CAROUSEL", children: enfants.join(","), caption: it.legende_ig || "" })).id;
  }
  await attendreConteneur(cont, tok);
  return (await graph("POST", `/${c.ig}/media_publish`, tok, { creation_id: cont })).id;
}

async function facebook(c: Comptes, it: any): Promise<string> {
  const imgs: string[] = it.images || [];
  const t = c.jetonPage;
  if (it.type === "story") {
    const photo = (await graph("POST", `/${c.page}/photos`, t, { url: imgs[0], published: "false" })).id;
    const r = await graph("POST", `/${c.page}/photo_stories`, t, { photo_id: photo });
    return r.post_id || r.id || "ok";
  }
  if (imgs.length === 1) {
    const r = await graph("POST", `/${c.page}/photos`, t, { url: imgs[0], caption: it.legende_fb || "" });
    return r.post_id || r.id;
  }
  const pieces: Record<string, string> = {};
  for (let i = 0; i < imgs.length && i < 10; i++) {
    const f = (await graph("POST", `/${c.page}/photos`, t, { url: imgs[i], published: "false" })).id;
    pieces[`attached_media[${i}]`] = JSON.stringify({ media_fbid: f });
  }
  return (await graph("POST", `/${c.page}/feed`, t, { message: it.legende_fb || "", ...pieces })).id;
}

async function publier(): Promise<unknown[]> {
  const tok = jeton();
  if (!tok) return [{ erreur: "aucun jeton Meta" }];
  // un passage interrompu (délai dépassé) laisse « en_cours » : on le reprend 15 min plus tard, sans republier
  // les plateformes déjà notées comme parues
  await db.from("qosmi_social_file").update({ statut: "attente" }).eq("statut", "en_cours")
    .lt("mis_a_jour", new Date(Date.now() - 15 * 60000).toISOString());
  // trop en retard (jeton absent, panne) : on ne publie pas une story de la veille ni un post de 18 h 30 à 3 h du matin
  const { data: vieux } = await db.from("qosmi_social_file").update({ statut: "perime", mis_a_jour: new Date().toISOString() })
    .eq("statut", "attente").lt("publier_a", new Date(Date.now() - 3 * 3600000).toISOString()).select("cle");
  if (vieux?.length) await alerter(`⚠️ Qosmi réseaux : pas publié (plus de 3 h de retard) : ${vieux.map((v) => v.cle).join(", ")}`);
  const { data: dues } = await db.from("qosmi_social_file").select("*")
    .eq("statut", "attente").lte("publier_a", new Date().toISOString()).order("publier_a").limit(4);
  if (!dues?.length) return [];
  let c: Comptes;
  try {
    c = await comptes(tok);
  } catch (e) {
    return [{ erreur: (e as Error).message }];
  }
  const sortie: unknown[] = [];
  for (const it of dues) {
    // réservation atomique : un seul passage publie chaque élément
    const { data: pris } = await db.from("qosmi_social_file").update({ statut: "en_cours", mis_a_jour: new Date().toISOString() })
      .eq("id", it.id).eq("statut", "attente").select("id");
    if (!pris?.length) continue;
    const res = { ...(it.resultat || {}) } as Record<string, any>;
    for (const pl of it.plateformes as string[]) {
      if (res[pl]?.id) continue; // déjà parue sur cette plateforme (essai précédent)
      try {
        const id = pl === "instagram" ? await instagram(c, tok, it) : await facebook(c, it);
        res[pl] = { id, a: new Date().toISOString() };
        await db.from("qosmi_social_file").update({ resultat: res, mis_a_jour: new Date().toISOString() }).eq("id", it.id);
      } catch (e) {
        res[pl] = { erreur: (e as Error).message.slice(0, 500), a: new Date().toISOString() };
      }
    }
    const toutes = (it.plateformes as string[]).every((pl) => res[pl]?.id);
    const essais = it.essais + 1;
    const statut = toutes ? "publie" : essais >= MAX_ESSAIS ? ((it.plateformes as string[]).some((pl) => res[pl]?.id) ? "partiel" : "erreur") : "attente";
    await db.from("qosmi_social_file").update({ statut, resultat: res, essais, mis_a_jour: new Date().toISOString() }).eq("id", it.id);
    sortie.push({ cle: it.cle, statut, resultat: res });
    if (statut !== "publie" && statut !== "attente") await alerter(`⚠️ Qosmi réseaux : « ${it.cle} » ${statut}\n${JSON.stringify(res).slice(0, 600)}`);
  }
  return sortie;
}

async function alerter(texte: string) {
  try {
    const tg = (Deno.env.get("TELEGRAM_TOKEN") || "").replace(/\s+/g, "");
    const chat = await reglage("tg_chat");
    if (tg && chat) {
      await fetch(`https://api.telegram.org/bot${tg}/sendMessage`, {
        method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ chat_id: chat, text: texte }),
      });
    }
  } catch (_) { /* rien */ }
}

async function ajouter(req: Request) {
  const refus = await githubOk(req);
  if (refus) return json({ erreur: refus }, 401);
  const { items } = await req.json();
  const sortie = [];
  for (const it of items || []) {
    if (!it.cle || !["post", "story"].includes(it.type) || !it.publier_a || !Array.isArray(it.images) || !it.images.length) {
      sortie.push({ cle: it.cle, erreur: "élément incomplet" });
      continue;
    }
    const ligne = {
      cle: it.cle, type: it.type, publier_a: it.publier_a, legende_ig: it.legende_ig ?? null, legende_fb: it.legende_fb ?? null,
      images: it.images, plateformes: it.plateformes || ["instagram", "facebook"], mis_a_jour: new Date().toISOString(),
    };
    const { data: deja } = await db.from("qosmi_social_file").select("id,statut").eq("cle", it.cle).maybeSingle();
    if (deja && deja.statut !== "attente") {
      sortie.push({ cle: it.cle, id: deja.id, statut: deja.statut, note: "déjà traité, inchangé" });
      continue;
    }
    const { data, error } = deja
      ? await db.from("qosmi_social_file").update(ligne).eq("id", deja.id).select("id").single()
      : await db.from("qosmi_social_file").insert(ligne).select("id").single();
    sortie.push(error ? { cle: it.cle, erreur: error.message } : { cle: it.cle, id: data.id, statut: "attente" });
  }
  return json({ ok: true, items: sortie });
}

async function etat() {
  const tok = jeton();
  const out: Record<string, unknown> = { secret: Deno.env.get("META_TOKEN") ? "META_TOKEN" : Deno.env.get("WA_TOKEN") ? "WA_TOKEN (repli)" : "aucun" };
  try {
    const dbg = await graph("GET", "/debug_token", tok, { input_token: tok });
    out.scopes = dbg?.data?.scopes;
    out.expire = dbg?.data?.expires_at;
  } catch (e) {
    out.scopes = "illisible : " + (e as Error).message.slice(0, 200);
  }
  try {
    const c = await comptes(tok);
    out.page = { id: c.page, nom: c.nom };
    out.instagram = c.ig ? { id: c.ig, nom: c.igNom } : null;
  } catch (e) {
    out.comptes = (e as Error).message;
  }
  const { data } = await db.from("qosmi_social_file").select("cle,type,publier_a,statut,essais,resultat").order("publier_a", { ascending: false }).limit(12);
  out.file = data;
  return json(out);
}

Deno.serve(async (req) => {
  const action = new URL(req.url).searchParams.get("action");
  try {
    if (action === "ajouter" && req.method === "POST") return await ajouter(req);
    if (!(await cleOk(req))) return json({ erreur: "clé refusée" }, 401);
    if (action === "publier") return json({ ok: true, publie: await publier() });
    if (action === "etat") return await etat();
    return json({ erreur: "action inconnue" }, 400);
  } catch (e) {
    return json({ erreur: (e as Error).message }, 500);
  }
});
