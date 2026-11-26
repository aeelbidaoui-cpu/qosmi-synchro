// Flux produits Qosmi pour un catalogue Meta appartenant à Qosmi (demande d'Amine du 26/11/2026 : boutique Instagram
// avec les Pays-Bas comme marché principal ; le catalogue géré par l'app Shopify est refusé pour les boutiques).
// Lu par Meta (planification quotidienne) : GET → CSV au format Meta (un article par format).
// Données publiques seulement : qosmi.nl/products.json (titres et textes en néerlandais, prix en euros, liens qosmi.nl).
const BOUTIQUE = "https://qosmi.nl";

function texte(html: string): string {
  return (html || "").replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"').replace(/\s+/g, " ").trim();
}

function csv(v: unknown): string {
  const s = String(v ?? "");
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

async function page(n: number): Promise<any[]> {
  for (let essai = 0; essai < 5; essai++) {
    const r = await fetch(`${BOUTIQUE}/products.json?limit=250&page=${n}`, { headers: { "user-agent": "Mozilla/5.0 (qosmi-flux-meta)" } });
    if (r.ok) return (await r.json()).products || [];
    await new Promise((ok) => setTimeout(ok, 3000 * (essai + 1)));
  }
  throw new Error(`qosmi.nl/products.json page ${n} illisible`);
}

Deno.serve(async () => {
  try {
    const lignes = [["id", "item_group_id", "title", "description", "availability", "condition", "price", "link", "image_link",
      "additional_image_link", "brand", "product_type", "size"].join(",")];
    const vus = new Set<string>();
    for (let n = 1; n < 40; n++) {
      const ps = await page(n);
      if (!ps.length) break;
      for (const p of ps) {
        const imgs = (p.images || []).map((i: any) => i.src);
        if (!imgs.length) continue;
        const desc = (texte(p.body_html) || p.title).slice(0, 4900);
        for (const v of p.variants || []) {
          const prix = Number(v.price);
          if (!(prix > 0)) continue;
          let id = v.sku || `qosmi-${v.id}`;
          if (vus.has(id)) id = `qosmi-${v.id}`; // même SKU sur deux fiches : identifiant du format à la place
          vus.add(id);
          const titre = p.variants.length > 1 && v.title !== "Default Title" ? `${p.title} — ${v.title}` : p.title;
          lignes.push([
            id, p.id, titre.slice(0, 200), desc, v.available ? "in stock" : "out of stock", "new",
            `${prix.toFixed(2)} EUR`, `${BOUTIQUE}/products/${p.handle}?variant=${v.id}`, imgs[0], imgs.slice(1, 6).join(","),
            p.vendor || "Qosmi", p.product_type || "", v.title !== "Default Title" ? v.title : "",
          ].map(csv).join(","));
        }
      }
    }
    return new Response(lignes.join("\n") + "\n", {
      headers: { "content-type": "text/csv; charset=utf-8", "cache-control": "public, max-age=3600" },
    });
  } catch (e) {
    return new Response("erreur : " + (e as Error).message, { status: 503 });
  }
});
