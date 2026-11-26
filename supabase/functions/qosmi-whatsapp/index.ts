// Bot WhatsApp Qosmi (26/11/2026).
// - Meta (WhatsApp Cloud API) appelle cette fonction pour chaque message reçu sur le numéro Qosmi.
// - Le bot répond aux questions courantes (FR/NL/EN) avec un menu.
// - « Parler à quelqu'un » ou une question qu'il ne comprend pas : le message part chez Amine sur Telegram ;
//   Amine répond en « répondant » au message Telegram, et sa réponse repart vers le client sur WhatsApp.
// Secrets (tableau de bord Supabase > Edge Functions > Secrets) : WA_TOKEN, META_APP_SECRET, TELEGRAM_TOKEN.
// Réglages non secrets (table qosmi_wa_reglages) : verify_token, tg_secret, code_appairage, tg_chat, wa_phone_id.
import { createClient } from "jsr:@supabase/supabase-js@2";

const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
const GRAPH = "https://graph.facebook.com/v23.0";
type Lg = "fr" | "nl" | "en";

// ------------------------------------------------------------------ textes
const T: Record<string, Record<Lg, string>> = {
  accueil: {
    fr: "Bonjour ! Ici Qosmi, parfums authentiques à prix justes. Choisis un sujet dans le menu, ou écris ta question.",
    nl: "Hallo! Hier is Qosmi, authentieke parfums tegen eerlijke prijzen. Kies een onderwerp in het menu of stel je vraag.",
    en: "Hello! This is Qosmi, authentic fragrances at fair prices. Pick a topic from the menu or type your question.",
  },
  bouton: { fr: "Voir le menu", nl: "Bekijk het menu", en: "See the menu" },
  section: { fr: "Sujets", nl: "Onderwerpen", en: "Topics" },
  suivi: {
    fr: "📦 Suivre ta commande\nTon lien de suivi est dans l'e-mail « Ta commande est en route ». Tu peux aussi voir tes commandes ici : https://qosmi.be/account\nToujours un souci ? Envoie ton numéro de commande (#1…) et choisis « Parler à quelqu'un ».",
    nl: "📦 Je bestelling volgen\nJe trackinglink staat in de verzendmail. Je bestellingen zie je ook hier: https://qosmi.be/nl/account\nNog een probleem? Stuur je bestelnummer (#1…) en kies « Iemand spreken ».",
    en: "📦 Track your order\nYour tracking link is in the shipping e-mail. You can also see your orders here: https://qosmi.be/en/account\nStill stuck? Send your order number (#1…) and choose « Talk to someone ».",
  },
  livraison: {
    fr: "🚚 Livraison (Mondial Relay)\n• Belgique : 2,95 € en point relais pour 1 article, offert dès 2 articles.\n• Pays-Bas : 3,95 €, offert dès 2 articles.\n• France : 4,95 € en point relais.\nAutres pays d'Europe et livraison à domicile : le prix s'affiche au paiement.",
    nl: "🚚 Levering (Mondial Relay)\n• België: €2,95 naar een afhaalpunt voor 1 artikel, gratis vanaf 2 artikelen.\n• Nederland: €3,95, gratis vanaf 2 artikelen.\n• Frankrijk: €4,95 naar een afhaalpunt.\nAndere Europese landen en levering aan huis: de prijs zie je bij het afrekenen.",
    en: "🚚 Delivery (Mondial Relay)\n• Belgium: €2.95 to a pick-up point for 1 item, free from 2 items.\n• Netherlands: €3.95, free from 2 items.\n• France: €4.95 to a pick-up point.\nOther European countries and home delivery: the price is shown at checkout.",
  },
  retour: {
    fr: "↩️ Retours\nTu as 14 jours après réception pour changer d'avis. Les frais de retour sont à ta charge. Envoie ton numéro de commande et choisis « Parler à quelqu'un » : on t'explique la suite.",
    nl: "↩️ Retourneren\nJe hebt 14 dagen na ontvangst bedenktijd. De retourkosten zijn voor jouw rekening. Stuur je bestelnummer en kies « Iemand spreken »: we leggen uit hoe het verder gaat.",
    en: "↩️ Returns\nYou have 14 days after delivery to change your mind. Return shipping is at your expense. Send your order number and choose « Talk to someone »: we'll explain the next steps.",
  },
  testeur: {
    fr: "🧪 Testeurs\nNos testeurs sont des parfums 100 % authentiques, avec leur bouchon. Seul l'emballage change : une boîte simple au lieu de la boîte de vente. C'est pour ça qu'ils sont moins chers.",
    nl: "🧪 Testers\nOnze testers zijn 100% authentieke parfums, met hun dop. Alleen de verpakking is anders: een eenvoudige doos in plaats van de verkoopdoos. Daarom zijn ze goedkoper.",
    en: "🧪 Testers\nOur testers are 100% authentic fragrances, with their cap. Only the packaging differs: a plain box instead of the retail box. That's why they cost less.",
  },
  authentique: {
    fr: "✅ Authenticité\nTous nos parfums sont authentiques, achetés auprès de distributeurs officiels européens. Plus d'infos : https://qosmi.be/pages/authenticite",
    nl: "✅ Echtheid\nAl onze parfums zijn authentiek en gekocht bij officiële Europese distributeurs. Meer info: https://qosmi.be/nl/pages/echtheid",
    en: "✅ Authenticity\nAll our fragrances are authentic, bought from official European distributors. More info: https://qosmi.be/en/pages/authenticity",
  },
  paiement: {
    fr: "💳 Paiement\nBancontact, cartes Visa et Mastercard, Apple Pay et Google Pay. Le paiement est sécurisé par Shopify.",
    nl: "💳 Betalen\nBancontact, Visa en Mastercard, Apple Pay en Google Pay. De betaling is beveiligd door Shopify.",
    en: "💳 Payment\nBancontact, Visa and Mastercard, Apple Pay and Google Pay. Payment is secured by Shopify.",
  },
  horaires: {
    fr: "🕒 Horaires\nOn répond sur WhatsApp du lundi au vendredi de 18 h à 22 h, et le week-end de 10 h à 20 h. La boutique en ligne est ouverte 24 h/24 : https://qosmi.be",
    nl: "🕒 Openingstijden\nWe antwoorden op WhatsApp van maandag tot vrijdag van 18 tot 22 uur, en in het weekend van 10 tot 20 uur. De webshop is 24/7 open: https://qosmi.be/nl",
    en: "🕒 Opening hours\nWe answer on WhatsApp Monday to Friday 6–10 pm, weekends 10 am–8 pm. The online shop is open 24/7: https://qosmi.be/en",
  },
  humain: {
    fr: "🙋 C'est noté, un membre de l'équipe te répond ici dès que possible (en semaine de 18 h à 22 h, le week-end de 10 h à 20 h). Tu peux déjà écrire ta question.",
    nl: "🙋 Genoteerd, iemand van het team antwoordt je hier zo snel mogelijk (weekdagen 18–22 uur, weekend 10–20 uur). Je kan je vraag alvast typen.",
    en: "🙋 Noted, a team member will reply here as soon as possible (weekdays 6–10 pm, weekends 10 am–8 pm). You can already type your question.",
  },
  transmis: {
    fr: "Merci ! J'ai transmis ton message à l'équipe, on te répond ici dès que possible. Pour revenir au menu, écris « menu ».",
    nl: "Bedankt! Ik heb je bericht aan het team doorgegeven, we antwoorden hier zo snel mogelijk. Typ « menu » om terug te gaan naar het menu.",
    en: "Thanks! I've passed your message to the team, we'll reply here as soon as possible. Type « menu » to go back to the menu.",
  },
  fin: {
    fr: "Écris « menu » pour revoir les sujets.",
    nl: "Typ « menu » om de onderwerpen opnieuw te zien.",
    en: "Type « menu » to see the topics again.",
  },
};

const MENU: { id: string; titre: Record<Lg, string> }[] = [
  { id: "suivi", titre: { fr: "Suivre ma commande", nl: "Bestelling volgen", en: "Track my order" } },
  { id: "livraison", titre: { fr: "Livraison et prix", nl: "Levering en prijzen", en: "Delivery and prices" } },
  { id: "retour", titre: { fr: "Retours", nl: "Retourneren", en: "Returns" } },
  { id: "testeur", titre: { fr: "Testeurs", nl: "Testers", en: "Testers" } },
  { id: "authentique", titre: { fr: "Authenticité", nl: "Echtheid", en: "Authenticity" } },
  { id: "paiement", titre: { fr: "Paiement", nl: "Betalen", en: "Payment" } },
  { id: "horaires", titre: { fr: "Horaires", nl: "Openingstijden", en: "Opening hours" } },
  { id: "humain", titre: { fr: "Parler à quelqu'un", nl: "Iemand spreken", en: "Talk to someone" } },
];

const MOTS: [string, RegExp][] = [
  ["humain", /\b(humain|quelqu'un|personne|conseill|medewerker|iemand|mens|human|agent|someone|person)\b/i],
  ["suivi", /\b(suivi|suivre|colis|commande|livr[ée]e?\s*quand|track|bestelling|pakket|pakje|order|parcel|where is)\b/i],
  ["retour", /\b(retour|rembours|retourn|terugsturen|refund|return)\b/i],
  ["testeur", /\b(testeurs?|testers?)\b/i],
  ["authentique", /\b(authenti|vrai|faux|fake|contrefa|echt|namaak|original|genuine)\w*/i],
  ["paiement", /\b(paiement|payer|bancontact|carte|betal|payment|pay)\w*/i],
  ["livraison", /\b(livraison|exp[ée]di|envoi|frais de port|levering|verzend|bezorg|delivery|shipping)\w*/i],
  ["horaires", /\b(horaire|heure|ouvert|openingstijd|open|uur|hours|opening)\w*/i],
];

function langueDe(texte: string, actuelle?: string): Lg {
  const t = texte.toLowerCase();
  if (/^\s*(nl|nederlands)\s*$/.test(t)) return "nl";
  if (/^\s*(fr|français|francais)\s*$/.test(t)) return "fr";
  if (/^\s*(en|english)\s*$/.test(t)) return "en";
  if (actuelle === "fr" || actuelle === "nl" || actuelle === "en") return actuelle as Lg;
  if (/\b(hallo|hoi|goedemiddag|goedenavog|goedenavond|goedemorgen|bestelling|ik|jullie|graag|bedankt|dank|wanneer|kan ik)\b/.test(t)) return "nl";
  if (/\b(hello|hi|hey|please|thanks|thank you|my order|when|can i|do you)\b/.test(t) && !/\b(bonjour|merci|salut)\b/.test(t)) return "en";
  return "fr";
}

// ------------------------------------------------------------------ outils
async function reglage(cle: string): Promise<string | null> {
  const { data } = await db.from("qosmi_wa_reglages").select("valeur").eq("cle", cle).maybeSingle();
  return data?.valeur ?? null;
}
async function ecrireReglage(cle: string, valeur: string) {
  await db.from("qosmi_wa_reglages").upsert({ cle, valeur, mis_a_jour: new Date().toISOString() });
}
async function journal(sens: string, wa_id: string | null, contenu: string) {
  await db.from("qosmi_wa_journal").insert({ sens, wa_id, contenu: contenu.slice(0, 2000) });
}
function jetonTelegram(): string {
  const brut = (Deno.env.get("TELEGRAM_TOKEN") || "").replace(/\s+/g, "");
  const m = brut.match(/\d{6,}:[A-Za-z0-9_-]{30,}/);
  return m ? m[0] : brut;
}
async function tg(methode: string, params: Record<string, unknown>) {
  const r = await fetch(`https://api.telegram.org/bot${jetonTelegram()}/${methode}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(params),
  });
  return await r.json();
}
async function wa(corps: Record<string, unknown>) {
  const id = await reglage("wa_phone_id");
  const r = await fetch(`${GRAPH}/${id}/messages`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${(Deno.env.get("WA_TOKEN") || "").trim()}` },
    body: JSON.stringify({ messaging_product: "whatsapp", ...corps }),
  });
  const j = await r.json();
  if (!r.ok) await journal("erreur", String(corps.to ?? ""), JSON.stringify(j));
  return j;
}
const texte = (to: string, body: string) => wa({ to, type: "text", text: { body, preview_url: true } });
function menu(to: string, lg: Lg) {
  return wa({
    to, type: "interactive",
    interactive: {
      type: "list",
      body: { text: T.accueil[lg] },
      action: {
        button: T.bouton[lg],
        sections: [{ title: T.section[lg], rows: MENU.map((m) => ({ id: m.id, title: m.titre[lg] })) }],
      },
    },
  });
}
async function signatureOk(req: Request, brut: string): Promise<boolean> {
  const secret = (Deno.env.get("META_APP_SECRET") || "").trim();
  const sig = req.headers.get("x-hub-signature-256") || "";
  if (!secret || !sig.startsWith("sha256=")) return false;
  const cle = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = new Uint8Array(await crypto.subtle.sign("HMAC", cle, new TextEncoder().encode(brut)));
  const hex = [...mac].map((b) => b.toString(16).padStart(2, "0")).join("");
  return hex === sig.slice(7);
}

// ------------------------------------------------------------------ vers Amine (Telegram)
async function versAmine(wa_id: string, nom: string, contenu: string) {
  const chat = await reglage("tg_chat");
  if (!chat) { await journal("erreur", wa_id, "tg_chat manquant : " + contenu); return; }
  const r = await tg("sendMessage", {
    chat_id: chat,
    text: `💬 WhatsApp · ${nom || "client"} (+${wa_id})\n\n${contenu}\n\n↩️ Réponds à ce message pour répondre au client. « /bot » en réponse = rendre la main au bot.`,
  });
  const mid = r?.result?.message_id;
  if (mid) await db.from("qosmi_wa_relais").insert({ tg_message_id: mid, wa_id });
  await journal("relais", wa_id, contenu);
}

// ------------------------------------------------------------------ messages WhatsApp
async function surMessageWhatsApp(m: any, contacts: any[]) {
  const wa_id: string = m.from;
  const nom: string = contacts?.find((c: any) => c.wa_id === wa_id)?.profile?.name || "";
  const { data: client } = await db.from("qosmi_wa_clients").select("*").eq("wa_id", wa_id).maybeSingle();

  let contenu = "";
  let choix = "";
  if (m.type === "text") contenu = m.text?.body || "";
  else if (m.type === "interactive") {
    choix = m.interactive?.list_reply?.id || m.interactive?.button_reply?.id || "";
    contenu = m.interactive?.list_reply?.title || m.interactive?.button_reply?.title || choix;
  } else if (m.type === "button") contenu = m.button?.text || "";
  else contenu = `[${m.type}] ${m[m.type]?.caption || ""}`.trim();

  const lg = langueDe(contenu, client?.langue);
  const maintenant = new Date().toISOString();
  await db.from("qosmi_wa_clients").upsert({
    wa_id, nom: nom || client?.nom || null, langue: lg, mode: client?.mode || "bot",
    dernier_message_client: maintenant, mis_a_jour: client?.mis_a_jour || maintenant,
  });
  await journal("entrant", wa_id, contenu);
  await wa({ status: "read", message_id: m.id });

  const t = contenu.trim().toLowerCase();
  // le client veut revenir au menu
  if (/^(menu|start|début|debut|begin|home)$/.test(t)) {
    await db.from("qosmi_wa_clients").update({ mode: "bot", mis_a_jour: maintenant }).eq("wa_id", wa_id);
    return menu(wa_id, lg);
  }
  // conversation déjà confiée à Amine (moins de 12 h) : on transmet sans répondre
  const recent = client?.mode === "humain" && Date.now() - new Date(client.mis_a_jour).getTime() < 12 * 3600e3;
  if (recent) return versAmine(wa_id, nom, contenu);

  if (/^(nl|nederlands|fr|français|francais|en|english)$/.test(t)) return menu(wa_id, lg);

  let sujet = choix;
  if (!sujet) for (const [id, re] of MOTS) if (re.test(contenu)) { sujet = id; break; }

  if (sujet === "humain") {
    await db.from("qosmi_wa_clients").update({ mode: "humain", mis_a_jour: maintenant }).eq("wa_id", wa_id);
    await texte(wa_id, T.humain[lg]);
    return versAmine(wa_id, nom, `(demande à parler à quelqu'un) ${contenu}`);
  }
  if (sujet && T[sujet]) {
    await texte(wa_id, T[sujet][lg]);
    return texte(wa_id, T.fin[lg]);
  }
  // premier message, salutation ou message court : le menu
  if (!client || t.length < 25 || /^(bonjour|salut|hello|hi|hey|hallo|hoi|goedendag|bonsoir)\b/.test(t)) return menu(wa_id, lg);
  // question libre non reconnue : on la confie à Amine
  await db.from("qosmi_wa_clients").update({ mode: "humain", mis_a_jour: maintenant }).eq("wa_id", wa_id);
  await texte(wa_id, T.transmis[lg]);
  return versAmine(wa_id, nom, contenu);
}

// ------------------------------------------------------------------ messages Telegram (Amine)
async function surMessageTelegram(u: any) {
  const m = u.message;
  if (!m?.chat) return;
  const chat = String(m.chat.id);
  const attendu = await reglage("tg_chat");
  const texteTg: string = (m.text || "").trim();

  if (!attendu) {
    const code = await reglage("code_appairage");
    if (code && texteTg.includes(code)) {
      await ecrireReglage("tg_chat", chat);
      await tg("sendMessage", { chat_id: chat, text: "✅ Conversation reliée au bot WhatsApp Qosmi. Les messages des clients arriveront ici." });
    }
    return;
  }
  if (chat !== attendu) return; // personne d'autre ne peut répondre aux clients

  const ref = m.reply_to_message?.message_id;
  if (!ref) {
    if (texteTg) await tg("sendMessage", { chat_id: chat, text: "Pour répondre à un client, utilise « Répondre » sur son message WhatsApp transmis ici." });
    return;
  }
  const { data: relais } = await db.from("qosmi_wa_relais").select("wa_id").eq("tg_message_id", ref).maybeSingle();
  if (!relais) { await tg("sendMessage", { chat_id: chat, text: "Je ne retrouve pas le client de ce message." }); return; }
  const wa_id = relais.wa_id;
  const maintenant = new Date().toISOString();

  if (/^\/bot\b/i.test(texteTg)) {
    await db.from("qosmi_wa_clients").update({ mode: "bot", mis_a_jour: maintenant }).eq("wa_id", wa_id);
    await tg("sendMessage", { chat_id: chat, text: "🤖 Le bot reprend la main pour ce client.", reply_to_message_id: m.message_id });
    return;
  }
  if (!texteTg) { await tg("sendMessage", { chat_id: chat, text: "Seul le texte est transmis pour l'instant." }); return; }

  const r = await texte(wa_id, texteTg);
  await db.from("qosmi_wa_clients").update({ mode: "humain", mis_a_jour: maintenant }).eq("wa_id", wa_id);
  await db.from("qosmi_wa_relais").insert({ tg_message_id: m.message_id, wa_id }).select();
  await journal("sortant", wa_id, texteTg);
  const ok = r?.messages?.[0]?.id;
  await tg("sendMessage", {
    chat_id: chat, reply_to_message_id: m.message_id,
    text: ok ? "✓ envoyé" : "⚠️ Pas envoyé. Si le client a écrit il y a plus de 24 h, WhatsApp bloque les messages libres : il doit réécrire d'abord.",
  });
}

// ------------------------------------------------------------------ point d'entrée
Deno.serve(async (req) => {
  const url = new URL(req.url);

  // 1. Vérification du webhook par Meta
  if (req.method === "GET" && url.searchParams.get("hub.mode") === "subscribe") {
    const ok = url.searchParams.get("hub.verify_token") === (await reglage("verify_token"));
    return new Response(ok ? url.searchParams.get("hub.challenge") ?? "" : "refusé", { status: ok ? 200 : 403 });
  }

  // 2. Installation du webhook Telegram (à appeler une fois, avec le secret)
  if (req.method === "GET" && url.searchParams.get("installer") === "telegram") {
    const secret = await reglage("tg_secret");
    if (url.searchParams.get("cle") !== secret) return new Response("refusé", { status: 403 });
    const base = `https://${url.host}${url.pathname}`.replace("http://", "https://");
    const r = await tg("setWebhook", { url: `${base}?source=telegram`, secret_token: secret, allowed_updates: ["message"] });
    return new Response(JSON.stringify({ ok: r?.ok, description: r?.description }), { headers: { "content-type": "application/json" } });
  }

  if (req.method !== "POST") return new Response("ok");
  const brut = await req.text();

  // 3. Messages d'Amine sur Telegram
  if (url.searchParams.get("source") === "telegram") {
    if (req.headers.get("x-telegram-bot-api-secret-token") !== (await reglage("tg_secret"))) return new Response("refusé", { status: 403 });
    try { await surMessageTelegram(JSON.parse(brut)); } catch (e) { await journal("erreur", null, "telegram : " + String(e)); }
    return new Response("ok");
  }

  // 4. Messages WhatsApp (Meta)
  if (!(await signatureOk(req, brut))) return new Response("signature", { status: 401 });
  try {
    const corps = JSON.parse(brut);
    for (const e of corps.entry || []) for (const ch of e.changes || []) {
      const v = ch.value || {};
      for (const m of v.messages || []) await surMessageWhatsApp(m, v.contacts || []);
    }
  } catch (e) { await journal("erreur", null, "whatsapp : " + String(e)); }
  return new Response("ok");
});
