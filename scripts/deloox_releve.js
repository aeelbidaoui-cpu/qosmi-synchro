// Relevé des prix Deloox (concurrent de référence, usage INTERNE uniquement), lancé dans un onglet deloox.be du navigateur d'Amine.
// Une recherche par EAN, à rythme humain (2,2 à 3,8 s). S'arrête net si le site affiche une vérification anti-robot (« Client Challenge »).
// Remplacer __EANS__ par la liste JSON des EAN (scripts/deloox_eans.py), puis exécuter dans la page.
// Résultat : window.__dl = {etat: 'en cours' | 'termine' | 'challenge', fait, res: {ean: [gtin trouvé, prix, disponibilité, url]}, err}
(()=>{const E=__EANS__;window.__dl={etat:'en cours',fait:0,total:E.length,res:{},err:0};
(async()=>{for(const e of E){if(window.__dl.stop)break;try{const r=await fetch('https://www.deloox.be/chercher.html?q='+e,{credentials:'include'});const h=await r.text();
if(/Client Challenge/i.test(h)){window.__dl.etat='challenge';break;}
const g=(h.match(/"gtin1?[34]?"\s*:\s*"(\d+)"/)||[])[1]||'';const p=(h.match(/"price"\s*:\s*"?([\d.]+)/)||[])[1]||'';const a=(h.match(/"availability"\s*:\s*"([^"]+)"/)||[])[1]||'';
window.__dl.res[e]=[g,p,a,r.url.includes('/produit/')?r.url.split('/produit/')[1].slice(0,80):''];}catch(x){window.__dl.err++}
window.__dl.fait++;await new Promise(r=>setTimeout(r,2200+Math.random()*1600));}
if(window.__dl.etat==='en cours')window.__dl.etat='termine';})();return 'lancé '+E.length;})()
