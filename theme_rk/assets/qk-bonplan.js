/* Option « Bon plan » sur les fiches (14/11/2026, demandes d'Amine).
   1. Fiches SoleLuna : certains formats ont une 2e variante « 100 ml · Bon plan » (NL « · Koopje »), même parfum commandé
      spécialement, un peu plus de délai, prix plus bas. Épuisée, elle reste affichée « épuisé » ; une ligne explique
      le délai quand elle est choisie.
   2. Fiches propres au 2e grossiste (étiquette « sur-commande », window.QK_SUR_COMMANDE posé par le layout) : formats
      normaux (« 100 ml »), la ligne « Bon plan » s'affiche en permanence ; un format épuisé reste affiché « épuisé ».
   Le thème Horizon redessine le sélecteur à chaque changement de variante : un MutationObserver refait le travail. */
const NL = document.documentElement.lang.toLowerCase().startsWith('nl');
const MOTS = [' · Bon plan', ' · Koopje', ' · Sur commande', ' · Op bestelling'];
const DELAI = NL ? '5 tot 10 werkdagen' : '5 à 10 jours ouvrables';
const TEXTE = NL
  ? '<strong>Koopje</strong> — speciaal voor jou besteld, verzonden binnen ' + DELAI + '. Zelfde originele parfum, lagere prijs.'
  : '<strong>Bon plan</strong> — commandé spécialement pour toi, expédié sous ' + DELAI + '. Même parfum authentique, prix plus doux.';
const TEXTE_FICHE = NL
  ? '<strong>Koopje</strong> — speciaal voor jou besteld, verzonden binnen ' + DELAI + '. Origineel en nieuw parfum.'
  : '<strong>Bon plan</strong> — commandé spécialement pour toi, expédié sous ' + DELAI + '. Parfum authentique et neuf.';
const estBonPlan = (v) => MOTS.some((m) => (v || '').includes(m));

function poserNote(apres, texte, genre) {
  const parent = apres.parentElement;
  let note = parent && parent.querySelector(':scope > .qk-bonplan-note');
  if (!note) {
    note = document.createElement('p');
    note.className = 'qk-bonplan-note';
    apres.after(note);
  }
  if (note.dataset.genre !== genre) {
    note.innerHTML = texte;
    note.dataset.genre = genre;
  }
}

function traiter() {
  const fiche = window.QK_SUR_COMMANDE === true;
  const pickers = document.querySelectorAll('variant-picker, .variant-picker');
  pickers.forEach((picker) => {
    let choisi = false;
    // 14/11/2026 (Amine) : rien n'est caché ; un format épuisé, « Bon plan » compris, reste affiché barré « épuisé »
    picker.querySelectorAll('input[type="radio"]').forEach((i) => {
      if (estBonPlan(i.value) && i.checked) choisi = true;
    });
    picker.querySelectorAll('select option').forEach((o) => {
      if (estBonPlan(o.value) && o.selected) choisi = true;
    });
    if (fiche) {
      poserNote(picker, TEXTE_FICHE, 'f');
    } else if (choisi) {
      poserNote(picker, TEXTE, 'b');
    } else {
      const note = picker.parentElement && picker.parentElement.querySelector(':scope > .qk-bonplan-note');
      if (note) note.remove();
    }
  });
  if (fiche && !pickers.length) {  // un seul format : pas de sélecteur, la note va au-dessus du bouton d'achat
    const form = document.querySelector('product-form-component, product-form, form[action*="/cart/add"]');
    if (form && !document.querySelector('.qk-bonplan-note')) {
      const note = document.createElement('p');
      note.className = 'qk-bonplan-note';
      note.dataset.genre = 'f';
      note.innerHTML = TEXTE_FICHE;
      form.before(note);
    }
  }
}

let minuteur = null;
new MutationObserver(() => { clearTimeout(minuteur); minuteur = setTimeout(traiter, 60); })
  .observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['checked', 'data-option-available'] });
document.addEventListener('change', () => setTimeout(traiter, 30));
traiter();
