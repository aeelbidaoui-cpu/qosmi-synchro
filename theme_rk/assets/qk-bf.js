/* Black Friday Qosmi (17/11/2026) : -10 % automatique au panier du 27 au 30 novembre 2026 sur la sélection « black-friday »
   (scripts/black_friday.py). Sur une fiche de la sélection (window.QK_BF = date du jour AAAAMMJJ, posé par le layout),
   une ligne sous le bouton d'achat l'annonce : avant le 27/11 « dès vendredi », pendant « appliqué au panier ». Rien après le 30/11. */
const JOUR = window.QK_BF;
const NL = document.documentElement.lang.toLowerCase().startsWith('nl');
function texte() {
  if (!JOUR || JOUR > 20261130) return null;
  if (JOUR < 20261127) {
    return NL ? '<strong>Black Friday</strong> — -10 % op dit parfum van vrijdag 27 tot maandag 30 november, automatisch in je winkelmandje.'
              : '<strong>Black Friday</strong> — -10 % sur ce parfum du vendredi 27 au lundi 30 novembre, automatiquement au panier.';
  }
  return NL ? '<strong>Black Friday</strong> — -10 % op dit parfum, automatisch toegepast in je winkelmandje (t/m maandag 30 november).'
            : '<strong>Black Friday</strong> — -10 % sur ce parfum, appliqué automatiquement au panier (jusqu\'au lundi 30 novembre).';
}
function poser() {
  const t = texte();
  if (!t || document.querySelector('.qk-bf-note')) return;
  const form = document.querySelector('product-form-component, product-form, form[action*="/cart/add"]');
  if (!form) return;
  const p = document.createElement('p');
  p.className = 'qk-bf-note';
  p.innerHTML = t;
  form.after(p);
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', poser); else poser();

// 20/11/2026 (Amine) : sur la diapositive Black Friday de l'accueil, les parfums affichés changent : tirage au hasard à
// chaque visite, puis 4 nouveaux (2 sur téléphone) toutes les 6 s, avec un fondu. Pas de rotation si le visiteur a
// demandé moins d'animations.
function rotation() {
  const box = document.querySelector('[data-qk-bf-rotation]');
  if (!box || box.dataset.qkPret) return;
  box.dataset.qkPret = '1';
  const cartes = [...box.querySelectorAll('.qk-bf__carte')];
  for (let i = cartes.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [cartes[i], cartes[j]] = [cartes[j], cartes[i]]; }
  const mobile = window.matchMedia('(max-width: 749px)');
  let debut = 0;
  const montrer = () => {
    const n = mobile.matches ? 2 : 4;
    cartes.forEach((c) => c.classList.add('qk-bf__carte--off'));
    for (let k = 0; k < Math.min(n, cartes.length); k++) {
      const c = cartes[(debut + k) % cartes.length];
      c.classList.remove('qk-bf__carte--off');
      box.appendChild(c);
    }
  };
  montrer();
  if (cartes.length <= 4 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  setInterval(() => {
    if (document.hidden) return;
    const vis = cartes.filter((c) => !c.classList.contains('qk-bf__carte--off'));
    vis.forEach((c) => c.classList.add('qk-bf__carte--fondu'));
    setTimeout(() => {
      debut = (debut + (mobile.matches ? 2 : 4)) % cartes.length;
      montrer();
      cartes.forEach((c) => c.classList.add('qk-bf__carte--fondu'));
      requestAnimationFrame(() => requestAnimationFrame(() => cartes.forEach((c) => c.classList.remove('qk-bf__carte--fondu'))));
    }, 450);
  }, 6000);
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', rotation); else rotation();
