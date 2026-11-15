/* Bancontact d'abord (15/11/2026, demande d'Amine).
   Dans le panier (tiroir et page), sous le bouton « Payer » : une ligne qui met Bancontact en avant (le moins cher pour nous :
   0,39 € par paiement) et un bouton « Plus de moyens de paiement » ; les boutons rapides (Apple Pay, Google Pay, Shop Pay)
   restent cachés tant que le client n'a pas cliqué dessus. Le checkout Shopify lui-même ne peut pas être modifié (forfait Basic).
   Horizon redessine le panier à chaque changement : un MutationObserver remet le bloc en place. */
const NL = document.documentElement.lang.toLowerCase().startsWith('nl');
const T = NL
  ? { txt: '<strong>Betaal met Bancontact</strong> — snel, veilig en zonder kosten voor jou. Kies Bancontact bij het afrekenen.', plus: 'Meer betaalmethoden', moins: 'Minder betaalmethoden' }
  : { txt: '<strong>Paie avec Bancontact</strong> — rapide, sécurisé et sans frais pour toi. Choisis Bancontact au moment de payer.', plus: 'Plus de moyens de paiement', moins: 'Moins de moyens de paiement' };
let ouvert = false;

function logo() {
  const t = document.getElementById('qk-bancontact-logo');
  return t ? t.innerHTML : '';
}

function bloc() {
  const d = document.createElement('div');
  d.className = 'qk-paiement';
  d.innerHTML = '<p class="qk-paiement__bc">' + logo() + '<span>' + T.txt + '</span></p>' +
    '<button type="button" class="qk-paiement__plus" aria-expanded="false">' + T.plus + '</button>';
  d.querySelector('button').addEventListener('click', () => { ouvert = !ouvert; appliquer(); });
  return d;
}

function appliquer() {
  document.documentElement.classList.toggle('qk-paiements-ouverts', ouvert);
  document.querySelectorAll('.qk-paiement__plus').forEach((b) => {
    b.textContent = ouvert ? T.moins : T.plus;
    b.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
  });
}

function placer() {
  document.querySelectorAll('.cart__ctas').forEach((ctas) => {
    const bouton = ctas.querySelector('.cart__checkout-button');
    if (!bouton || ctas.querySelector('.qk-paiement')) return;
    bouton.after(bloc());
  });
  appliquer();
}

let minuteur = null;
new MutationObserver(() => { clearTimeout(minuteur); minuteur = setTimeout(placer, 150); })
  .observe(document.body, { childList: true, subtree: true });
placer();
