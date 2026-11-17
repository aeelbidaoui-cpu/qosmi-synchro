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
