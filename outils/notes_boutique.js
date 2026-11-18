// Relevé des notes de parfum d'une boutique Shopify publique (18/11/2026), exécuté dans le navigateur sur le site visité.
// Lit /products.json (public), repère « Top/Heart/Base notes » (ou « Notes de tête/cœur/fond ») dans les descriptions,
// puis rapproche des parfums Qosmi encore sans notes. Aucune donnée n'est envoyée nulle part.
window.parseNotes = function (html) {
  const d = html.replace(/<br\s*\/?>/gi, '\n').replace(/<\/(p|li|div|h\d|strong|b|span)>/gi, '\n').replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ').replace(/[ \t]+/g, ' ');
  const lab = {
    t: /(?:top|head|opening)\s*notes?|notes?\s+de\s+t[eê]te|t[eê]te\s*:/i,
    c: /(?:heart|middle|mid)\s*notes?|notes?\s+de\s+c(?:oe|œ)ur|c(?:oe|œ)ur\s*:/i,
    f: /(?:base|bottom|dry[- ]?down)\s*notes?|notes?\s+de\s+fond|fond\s*:/i,
  };
  const out = {};
  for (const [k, re] of Object.entries(lab)) {
    const m = d.match(new RegExp('(?:' + re.source + ')\\s*(?:[:\\-–]|\\s(?:is|are|include|includes|of)\\s)?\\s*([^\\n;]{2,220})', 'i'));
    if (m) {
      let s = m[1].split(/(?:top|head|heart|middle|mid|base|bottom|dry[- ]?down)\s*notes?|notes?\s+de\s+(?:t[eê]te|c(?:oe|œ)ur|fond)/i)[0];
      s = s.split(/\.\s/)[0];
      out[k] = s.replace(/\.$/, '').trim();
    }
  }
  return out;
};
window.scanStore = async function (prefixe) {
  const all = [];
  for (let p = 1; p < 80; p++) {
    const r = await fetch((prefixe || '') + '/products.json?limit=250&page=' + p);
    if (r.status !== 200) { all.err = 'status ' + r.status; break; }
    const j = await r.json();
    if (!j.products.length) break;
    for (const x of j.products) {
      const n = parseNotes(x.body_html || '');
      if (n.t || n.c || n.f) all.push({ v: x.vendor, ti: x.title, h: x.handle, nt: n.t || '', nc: n.c || '', nf: n.f || '' });
    }
    await new Promise(z => setTimeout(z, 500));
  }
  return all;
};
window.matchStore = function (store, L, marque) {
  const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/['’´`]/g, '').replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ').trim();
  const STOP = new Set('eau de parfum toilette extrait cologne edp edt spray ml oz the le la les collection by for unisex perfume perfumes and of pour homme femme men women man woman him her'.split(' '));
  const toks = s => norm(s).split(' ').filter(w => w && !STOP.has(w) && !/^\d+(ml|oz)?$/.test(w));
  const conc = s => { s = norm(s); if (/extrait/.test(s)) return 'x'; if (/eau de toilette|\bedt\b/.test(s)) return 't'; if (/eau de cologne/.test(s)) return 'k'; if (/eau de parfum|\bedp\b/.test(s)) return 'p'; if (/\bparfum\b/.test(s)) return 'P'; return null; };
  const gen = s => { s = norm(s); if (/\b(pour femme|women|woman|for her|femme|her)\b/.test(s)) return 'F'; if (/\b(pour homme|men|man|for him|homme|him)\b/.test(s)) return 'H'; return null; };
  const cut = s => (s || '').split(/\s[–—-]\s/)[0].replace(/\s+/g, ' ').trim();
  const res = {};
  for (const [h, v, n, g] of L) {
    if (marque && norm(v) !== norm(marque)) continue;
    const vt = toks(v); const nt = toks(n).filter(w => !vt.includes(w)); if (!nt.length) continue;
    const c1 = conc(h.replace(/-/g, ' '));
    let best = null;
    for (const x of store) {
      const tt = toks(x.ti); const set = new Set(tt); if (!nt.every(w => set.has(w))) continue;
      if (!marque) { const vx = norm(x.v + ' ' + x.ti); if (!vt.some(w => vx.includes(w))) continue; }
      const c2 = conc(x.ti); if (c2 && c1 && c2 !== c1 && !(c1 === 'P' && c2 === 'x') && !(c1 === 'x' && c2 === 'P')) continue;
      const g2 = gen(x.ti); if (g2 && g !== 'M' && g2 !== g) continue;
      const extra = tt.filter(w => !nt.includes(w) && !vt.includes(w)).length; if (extra > 2) continue;
      if (!best || extra < best.extra) best = { extra, x };
    }
    if (best) res[h] = [best.x.h, best.x.ti, best.extra, cut(best.x.nt), cut(best.x.nc), cut(best.x.nf)];
  }
  return res;
};
