/* « Complète ta commande » dans le tiroir panier et la page panier (13/11/2026, demande d'Amine).
   3 parfums en stock aux notes proches de ceux du panier (index des odeurs), ajout en un clic.
   Avec 1 article : rappel « 2e article = livraison offerte ». Repli : recommandations Shopify si le parfum n'a pas de notes connues. */
import { CartLinesUpdateEvent } from '@shopify/events';
import { fetchConfig } from '@theme/utilities';

const C = window.QK_COMPLETE || {};
const NL = (document.documentElement.lang || '').toLowerCase().startsWith('nl');
const RACINE = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
const T = NL
  ? { un: 'Voeg een 2e parfum toe, de verzending is <strong>gratis</strong>', plus: 'Vaak samen gekozen', ajouter: 'Toevoegen', ajoute: 'Toegevoegd ✓', des: 'vanaf ' }
  : { un: 'Ajoute un 2<sup>e</sup> parfum, la livraison est <strong>offerte</strong>', plus: 'Souvent choisis avec ton parfum', ajouter: 'Ajouter', ajoute: 'Ajouté ✓', des: 'dès ' };

let odeursPret = null;
function chargerOdeurs() {
  if (window.qkOdeurs) return Promise.resolve(window.qkOdeurs);
  if (odeursPret) return odeursPret;
  const charge = (src) => new Promise((ok) => {
    if (!src) return ok();
    const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = ok; document.head.appendChild(s);
  });
  odeursPret = (window.QK_ODEURS ? Promise.resolve() : charge(C.odeurs)).then(() => charge(C.outils)).then(() => window.qkOdeurs || null);
  return odeursPret;
}

const cacheP = {};
const produit = (h) => (cacheP[h] ||= fetch(RACINE + 'products/' + h + '.js').then((r) => (r.ok ? r.json() : null)).catch(() => null));
const euros = (c) => (c / 100).toFixed(2).replace('.', ',') + ' €';

async function candidats(panier) {
  const O = await chargerOdeurs();
  const dedans = new Set(panier.items.map((i) => i.handle));
  const bases = new Set(panier.items.map((i) => (O ? O.base(i.handle) : i.handle)));
  const seeds = [...panier.items].sort((a, b) => b.final_price - a.final_price).map((i) => i.handle);
  let liste = [];
  if (O) seeds.forEach((h) => { O.proches(h).slice(0, 24).forEach((r) => liste.push(r.h)); });
  if (!liste.length) {
    const id = panier.items[0] && panier.items[0].product_id;
    if (id) {
      const r = await fetch(RACINE + 'recommendations/products.json?product_id=' + id + '&intent=related&limit=10').then((x) => x.json()).catch(() => ({}));
      liste = (r.products || []).map((p) => p.handle);
    }
  }
  const prixRef = Math.max(...panier.items.map((i) => i.final_price), 0);
  const plafond = Math.max(9000, prixRef);  /* pas plus cher que le parfum du panier (ou 90 €) */
  const vus = new Set(), out = [];
  for (const h of liste) {
    if (out.length >= 3) break;
    const b = O ? O.base(h) : h;
    if (dedans.has(h) || bases.has(b) || vus.has(b) || h.includes('coffret')) continue;
    vus.add(b);
    const p = await produit(h);
    if (!p || !p.available || !p.featured_image) continue;
    const v = p.variants.filter((x) => x.available).sort((x, y) => x.price - y.price)[0];
    if (!v || v.price > plafond) continue;
    out.push({ p, v });
  }
  return out;
}

function carte({ p, v }) {
  const t = (p.title || '').split(' — '), nom = t[0].replace(p.vendor, '').trim() || t[0];
  const el = document.createElement('div');
  el.className = 'qk-complete__item';
  el.innerHTML = '<a class="qk-complete__img" href="' + p.url + '"><img loading="lazy" alt="" src="' + p.featured_image +
    (p.featured_image.includes('?') ? '&' : '?') + 'width=200"></a><div class="qk-complete__txt"><span class="qk-complete__marque"></span>' +
    '<a class="qk-complete__nom" href="' + p.url + '"></a><span class="qk-complete__prix">' + (p.variants.length > 1 ? T.des : '') + euros(v.price) +
    (v.title && v.title !== 'Default Title' ? ' · ' + v.title.replace(/</g, '') : '') + '</span></div>' +
    '<button type="button" class="qk-complete__btn" data-id="' + v.id + '">' + T.ajouter + '</button>';
  el.querySelector('.qk-complete__marque').textContent = p.vendor;
  el.querySelector('.qk-complete__nom').textContent = nom;
  return el;
}

async function ajouter(btn) {
  btn.disabled = true;
  const id = btn.getAttribute('data-id');
  const fd = new FormData();
  fd.set('id', id); fd.set('quantity', '1');
  const ids = [...document.querySelectorAll('cart-items-component')].map((c) => c.dataset.sectionId).filter(Boolean);
  if (ids.length) fd.append('sections', ids.join(','));
  const attente = CartLinesUpdateEvent.createPromise();
  btn.dispatchEvent(new CartLinesUpdateEvent({ action: 'add', context: 'product', lines: [{ merchandiseId: id, quantity: 1 }], promise: attente.promise }));
  try {
    const cfg = fetchConfig('javascript', { body: fd });
    const rep = await fetch((window.Theme && Theme.routes && Theme.routes.cart_add_url) || RACINE + 'cart/add.js',
      { ...cfg, headers: { ...cfg.headers, Accept: 'text/html' } }).then((r) => r.json());
    const panier = await fetch(RACINE + 'cart.js').then((r) => r.json());
    attente.resolve({ cart: CartLinesUpdateEvent.createCartFromAjaxResponse(panier),
      detail: { items: panier.items, source: 'qk-complete', itemCount: 1, sections: rep.sections, didError: !!rep.status } });
    btn.textContent = rep.status ? (rep.message || '×') : T.ajoute;
  } catch (e) {
    attente.reject(e); btn.disabled = false;
  }
}

let cle = '', rendu = null, enCours = false;
async function maj() {
  if (enCours) return;
  const cibles = [...document.querySelectorAll('cart-items-component')];
  if (!cibles.length) return;
  enCours = true;
  try {
    const panier = await fetch(RACINE + 'cart.js').then((r) => r.json());
    const k = panier.items.map((i) => i.variant_id + ':' + i.quantity).join(',');
    if (k !== cle) {
      cle = k;
      rendu = null;
      if (panier.item_count > 0) {
        const liste = await candidats(panier);
        if (liste.length) {
          rendu = document.createElement('div');
          rendu.className = 'qk-complete';
          rendu.innerHTML = '<p class="qk-complete__titre">' + (panier.item_count === 1 ? T.un : T.plus) + '</p><div class="qk-complete__liste"></div>';
          liste.forEach((x) => rendu.querySelector('.qk-complete__liste').appendChild(carte(x)));
        }
      }
    }
    cibles.forEach((c) => {
      let bloc = c.nextElementSibling && c.nextElementSibling.classList.contains('qk-complete') ? c.nextElementSibling : null;
      if (!rendu) { if (bloc) bloc.remove(); return; }
      if (bloc && bloc.getAttribute('data-cle') === cle) return;
      const neuf = rendu.cloneNode(true); neuf.setAttribute('data-cle', cle);
      if (bloc) bloc.replaceWith(neuf); else c.after(neuf);
    });
  } finally { enCours = false; }
}

document.addEventListener('click', (e) => {
  const b = e.target.closest('.qk-complete__btn');
  if (b) { e.preventDefault(); ajouter(b); }
});
let minuteur = null;
const relancer = () => { clearTimeout(minuteur); minuteur = setTimeout(maj, 350); };
new MutationObserver(relancer).observe(document.body, { childList: true, subtree: true });
document.addEventListener('cart:update', relancer);
relancer();
