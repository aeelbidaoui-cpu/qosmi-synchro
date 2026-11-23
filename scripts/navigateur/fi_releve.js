// Relevé Fragrance Index (fragranceindex.ai, accord d'Amine du 13/11/2026), à lancer dans un onglet https://fragranceindex.ai/
// Avant : window.fiQ = [[handle, marque, nom, conc, genre], ...] (sortie de scripts/notes_a_relever.py).
// Résultat : window.fiRes (aussi dans localStorage « fiRes »), au format des relevés qosmi-fi-*.json.
window.fiExtraire = async (slug) => {
  const f = document.createElement('iframe'); f.style.cssText='position:fixed;left:-3000px;top:0;width:1200px;height:900px';
  f.src = '/perfumes/' + slug; document.body.appendChild(f);
  await new Promise((ok) => { f.onload = ok; setTimeout(ok, 15000); });
  await new Promise(r => setTimeout(r, 1500));
  let tx = '';
  try { const m = f.contentDocument.querySelector('main'); tx = m ? m.innerText : ''; } catch (e) {}
  f.remove();
  if (!tx) return {err: 'vide'};
  const L = tx.split('\n').map(s => s.trim()).filter(Boolean);
  const apres = (k) => { const i = L.indexOf(k); return i >= 0 ? L[i + 1] : ''; };
  const d = {slug, conc: apres('CONCENTRATION'), annee: apres('RELEASED'), genre: apres('GENDER'),
             parfumeur: [apres('PERFUMER') || apres('PERFUMERS') || apres('NOSE')].filter(x => x && x !== '—'),
             tenue: (apres('LONGEVITY') || '').toLowerCase(), sillage: (apres('SILLAGE') || '').toLowerCase()};
  const bs = L.indexOf('Best season'); if (bs >= 0) { d.saison = (L[bs + 1] || '').toLowerCase(); d.saison_com = d.saison; }
  // accords (Nom / NN%) puis vibes (Nom / NN) entre « Tap any accord » et « Scent profiles use »
  const a0 = L.findIndex(s => s.startsWith('Tap any accord')), a1 = L.findIndex(s => s.startsWith('Scent profiles use'));
  d.accords = {}; d.vibes = {};
  if (a0 >= 0 && a1 > a0) for (let i = a0 + 1; i < a1 - 1; i++) {
    const v = L[i + 1];
    if (/^\d+(\.\d+)?%$/.test(v)) { d.accords[L[i].toLowerCase()] = parseFloat(v); i++; }
    else if (/^\d+$/.test(v) && !/^\d+$/.test(L[i])) { d.vibes[L[i].toLowerCase()] = parseInt(v); i++; }
  }
  // notes
  const n0 = L.indexOf('Olfactive Notes'), n1 = L.indexOf('Where to wear');
  const blocs = {}; let cur = null;
  if (n0 >= 0) for (let i = n0 + 1; i < (n1 > n0 ? n1 : L.length); i++) {
    const s = L[i];
    if (/^(TOP NOTES|TOP|HEART NOTES|HEART|MIDDLE NOTES|BASE NOTES|BASE|NOTES)$/.test(s)) { cur = s.split(' ')[0]; blocs[cur] = []; continue; }
    if (cur) blocs[cur].push(s);
  }
  d.tete = (blocs.TOP || []).join(', '); d.coeur = (blocs.HEART || blocs.MIDDLE || []).join(', '); d.fond = (blocs.BASE || []).join(', ');
  d.notes = (blocs.NOTES || []).join(', ');
  // occasions : NOM EN MAJUSCULES / nombre entre « Best for » et « EXPLORE MORE OCCASIONS »
  const o0 = L.indexOf('Best for'), o1 = L.findIndex(s => s.startsWith('EXPLORE MORE OCCASIONS'));
  d.occasions = {};
  if (o0 >= 0 && o1 > o0) for (let i = o0 + 1; i < o1 - 1; i++) if (/^\d+$/.test(L[i + 1]) && L[i] === L[i].toUpperCase()) { d.occasions[L[i].toLowerCase()] = parseInt(L[i + 1]); i++; }
  return d;
};
window.fiNorm = s => (s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[´'’`]/g,'').replace(/&/g,' and ').replace(/[^a-z0-9]+/g,' ').trim();
window.fiMarque = (a,b) => { a=fiNorm(a).replace(/\b(parfums?|paris|perfumes?)\b/g,'').trim(); b=fiNorm(b).replace(/\b(parfums?|paris|perfumes?)\b/g,'').trim(); return a===b || a.startsWith(b) || b.startsWith(a) || a.replace(/ /g,'')===b.replace(/ /g,''); };
window.fiConc = c => ({'EDP':'edp','EDT':'edt','Extrait':'extrait','Parfum':'parfum','EDC':'edc'})[c]||'';
window.fiRes = [];
window.fiStop = false;
window.fiTourne = (async () => {
  const fait = new Set(fiRes.map(r=>r.h[0]));
  for (const [h,m,n,c,g] of fiQ) {
    if (fiStop) break; if (fait.has(h)) continue;
    const rec = {h:[h], m, n, c, g, ok:0};
    try {
      const j = await (await fetch('/api/public/search-suggest?q='+encodeURIComponent(m+' '+n))).json();
      const nn = fiNorm(n);
      const strip = s => fiNorm(s).replace(/\b(collection|refillable|limited edition|casamorati 1888)\b/g,'').replace(/\s+/g,' ').trim();
      const cands = (j.perfumes||[]).filter(p => fiMarque(p.brand, m));
      let best = cands.find(p => fiNorm(p.name)===nn), sur = !!best;
      if (!best) best = cands.find(p => strip(p.name)===strip(n));
      rec.cands = (j.perfumes||[]).slice(0,5).map(p=>p.brand+' | '+p.name+' | '+p.slug);
      if (best) {
        await new Promise(r=>setTimeout(r,1800));
        const d = await fiExtraire(best.slug);
        if (!d.err) {
          rec.d = d;
          const cp = fiNorm(d.conc), cq = fiConc(c);
          rec.ok = (sur && (!cp || !cq || cp===cq)) ? 2 : 1;
        }
      }
    } catch(e) { rec.err = String(e); }
    fiRes.push(rec);
    try { localStorage.setItem('fiRes', JSON.stringify(fiRes)); } catch(e) {}
    await new Promise(r=>setTimeout(r,2200));
  }
  return 'fini';
})();
