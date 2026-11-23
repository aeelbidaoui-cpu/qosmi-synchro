// Relevé Fragrantica (accord d'Amine du 10/11/2026) pour les parfums que Fragrance Index ne connaît pas.
// À lancer dans un onglet https://www.fragrantica.com/ (navigateur intégré de l'app Claude).
// 1. window.fgCibles = {"<handle Qosmi>": "<Maison>/<Nom>-<id>.html", ...}  (adresses vérifiées à la main :
//    page /designers/<Maison>.html → liens /perfume/… ; même parfum ET même concentration, sinon on laisse de côté)
// 2. coller ce script : il relève une page toutes les ~1,5 s et range le résultat dans window.fgRes et
//    localStorage « fgRes », au format des relevés qosmi-fi-*.json (ok = 2) → scripts/fi_fusion.py.
window.fgParse = function (html) {
  const d = new DOMParser().parseFromString(html, 'text/html'); const res = {};
  for (const lv of d.querySelectorAll('pyramid-level-new')) {
    res[lv.getAttribute('notes')] = [...new Set([...lv.querySelectorAll('a.pyramid-note-link')]
      .map(a => a.textContent.replace(/\s+/g, ' ').trim()).filter(Boolean))];
  }
  const h6 = [...d.querySelectorAll('h6')].find(e => e.textContent.trim() === 'main accords');
  res.accords = h6 ? [...h6.parentElement.querySelectorAll('div[style*="background"]')]
    .map(e => e.textContent.replace(/\s+/g, ' ').trim().toLowerCase()).filter(Boolean) : [];
  const og = (d.querySelector('meta[property="og:description"]') || {}).content || '';
  const y = og.match(/launched in (\d{4})/); if (y) res.annee = y[1];
  const nose = og.match(/The noses? behind this fragrance (?:is|are) ([^.]+)\./); if (nose) res.parfumeur = [nose[1]];
  res.title = d.title; return res;
};
window.fgRes = [];
window.fgTourne = (async () => {
  for (const [h, u] of Object.entries(window.fgCibles || {})) {
    try {
      const r = await fetch('/perfume/' + u); const p = fgParse(await r.text());
      const d = {slug: u, accords: p.accords || []};
      if (p.annee) d.annee = p.annee;
      if (p.parfumeur) d.parfumeur = p.parfumeur;
      if ((p.top || []).length) d.tete = p.top.join(', ');
      if ((p.middle || []).length) d.coeur = p.middle.join(', ');
      if ((p.base || []).length) d.fond = p.base.join(', ');
      const plat = Object.entries(p).filter(([k, v]) => !['top', 'middle', 'base', 'accords', 'parfumeur'].includes(k) && Array.isArray(v)).flatMap(([, v]) => v);
      if (plat.length) d.notes = plat.join(', ');
      fgRes.push({h: [h], ok: (d.accords.length || d.tete || d.notes) ? 2 : 0, src: 'fragrantica', titre: p.title, d});
    } catch (e) { fgRes.push({h: [h], ok: 0, err: String(e)}); }
    try { localStorage.setItem('fgRes', JSON.stringify(fgRes)); } catch (e) {}
    await new Promise(r => setTimeout(r, 1500));
  }
  return 'fini';
})();
'lancé'
