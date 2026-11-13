/* Message cadeau dans le panier (13/11/2026, demande d'Amine).
   Case « C'est un cadeau » + petit mot (200 caractères) juste au-dessus du bouton de paiement, dans le tiroir et sur la
   page panier. Enregistré en attributs du panier (« Cadeau », « Message cadeau ») : visibles sur la commande dans
   l'admin (Détails supplémentaires), pour la préparation du colis. Le thème Horizon redessine le résumé à chaque
   changement du panier : un MutationObserver remet le bloc en place. */
const NL = document.documentElement.lang.toLowerCase().startsWith('nl');
const RACINE = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
const T = NL
  ? { case: 'Het is een cadeau', aide: 'Een woordje voor de ontvanger? We stoppen het in het pakje.', place: 'Jouw boodschap (optioneel)', ok: 'Opgeslagen' }
  : { case: "C'est un cadeau", aide: 'Un petit mot pour la personne ? On le glisse dans le colis.', place: 'Ton message (facultatif)', ok: 'Enregistré' };
const MAX = 200;
let etat = { cadeau: false, message: '' }, charge = false, envoi = null;

async function lire() {
  try {
    const a = (await fetch(RACINE + 'cart.js').then((r) => r.json())).attributes || {};
    etat = { cadeau: !!a['Cadeau'], message: a['Message cadeau'] || '' };
  } catch (e) {}
  charge = true;
}

function enregistrer(bloc) {
  clearTimeout(envoi);
  envoi = setTimeout(async () => {
    try {
      await fetch(RACINE + 'cart/update.js', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ attributes: { 'Cadeau': etat.cadeau ? (NL ? 'Ja' : 'Oui') : '', 'Message cadeau': etat.cadeau ? etat.message : '' } })
      });
      document.querySelectorAll('.qk-cadeau__ok').forEach((o) => { o.hidden = false; setTimeout(() => { o.hidden = true; }, 1500); });
    } catch (e) {}
  }, 500);
}

function bloc() {
  const d = document.createElement('div');
  d.className = 'qk-cadeau';
  d.innerHTML =
    '<label class="qk-cadeau__case"><input type="checkbox"> <span>' + T.case + '</span></label>' +
    '<div class="qk-cadeau__zone" hidden><p class="qk-cadeau__aide">' + T.aide + '</p>' +
    '<textarea maxlength="' + MAX + '" rows="3" placeholder="' + T.place + '" aria-label="' + T.place + '"></textarea>' +
    '<p class="qk-cadeau__pied"><span class="qk-cadeau__ok" hidden>' + T.ok + '</span><span class="qk-cadeau__compte"></span></p></div>';
  const c = d.querySelector('input'), z = d.querySelector('.qk-cadeau__zone'), t = d.querySelector('textarea'), n = d.querySelector('.qk-cadeau__compte');
  const afficher = () => { c.checked = etat.cadeau; z.hidden = !etat.cadeau; if (document.activeElement !== t) t.value = etat.message; n.textContent = t.value.length + '/' + MAX; };
  c.addEventListener('change', () => { etat.cadeau = c.checked; afficher(); enregistrer(); syncAutres(d); });
  t.addEventListener('input', () => { etat.message = t.value.slice(0, MAX); n.textContent = t.value.length + '/' + MAX; enregistrer(); syncAutres(d); });
  d._afficher = afficher;
  afficher();
  return d;
}

function syncAutres(source) {
  document.querySelectorAll('.qk-cadeau').forEach((b) => { if (b !== source && b._afficher) b._afficher(); });
}

function placer() {
  if (!charge) return;
  document.querySelectorAll('.cart__ctas').forEach((ctas) => {
    const prec = ctas.previousElementSibling;
    if (prec && prec.classList.contains('qk-cadeau')) return;
    ctas.before(bloc());
  });
}

let minuteur = null;
new MutationObserver(() => { clearTimeout(minuteur); minuteur = setTimeout(placer, 200); }).observe(document.body, { childList: true, subtree: true });
lire().then(placer);
