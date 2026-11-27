// Qosmi : tableau de bord (27/11/2026, Amine : « vasy » pour un tableau de bord dans admin.deway.be).
// POST : le robot GitHub (scripts/tableau.py) dépose des instantanés {blocs: {cle: donnees}} dans la table qosmi_tableau.
// Authentification : jeton OIDC de GitHub Actions (dépôt aeelbidaoui-cpu/qosmi-synchro, audience qosmi-tableau) ;
// aucun secret partagé. La lecture se fait depuis admin.deway.be par les comptes connectés (RLS).
import { createClient } from "jsr:@supabase/supabase-js@2";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5.9.6";

const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const DEPOT = "aeelbidaoui-cpu/qosmi-synchro";
const JWKS = createRemoteJWKSet(new URL("https://token.actions.githubusercontent.com/.well-known/jwks"));
const CLES = new Set(["commandes", "ventes", "robots", "alertes"]);

const json = (d: unknown, status = 200) =>
  new Response(JSON.stringify(d), { status, headers: { "content-type": "application/json; charset=utf-8" } });

async function githubOk(req: Request): Promise<string | null> {
  const t = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!t) return "jeton GitHub absent";
  try {
    const { payload } = await jwtVerify(t, JWKS, { issuer: "https://token.actions.githubusercontent.com", audience: "qosmi-tableau" });
    if (payload.repository !== DEPOT) return "dépôt refusé";
    return null;
  } catch (e) {
    return "jeton GitHub invalide : " + (e as Error).message;
  }
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ erreur: "POST seulement" }, 405);
  const refus = await githubOk(req);
  if (refus) return json({ erreur: refus }, 401);
  let corps: { blocs?: Record<string, unknown> };
  try { corps = await req.json(); } catch { return json({ erreur: "JSON illisible" }, 400); }
  const lignes = Object.entries(corps.blocs || {})
    .filter(([cle]) => CLES.has(cle))
    .map(([cle, donnees]) => ({ cle, donnees, maj: new Date().toISOString() }));
  if (!lignes.length) return json({ erreur: "aucun bloc connu" }, 400);
  const { error } = await db.from("qosmi_tableau").upsert(lignes);
  if (error) return json({ erreur: error.message }, 500);
  return json({ ok: lignes.map((l) => l.cle) });
});
