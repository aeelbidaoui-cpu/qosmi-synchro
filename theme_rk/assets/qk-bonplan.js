/* Option « Bon plan » sur les fiches (14/11/2026, demandes d'Amine).
   1. Fiches SoleLuna : certains formats ont une 2e variante « 100 ml · Bon plan » (NL « · Koopje »), même parfum commandé
      spécialement, un peu plus de délai, prix plus bas. Épuisée, elle reste affichée « épuisé » ; une ligne explique
      le délai quand elle est choisie.
   2. Fiches propres au 2e grossiste (étiquette « sur-commande », window.QK_SUR_COMMANDE posé par le layout) : formats
      normaux (« 100 ml »), la ligne « Bon plan » s'affiche en permanence ; un format épuisé reste affiché « épuisé ».
   Le thème Horizon redessine le sélecteur à chaque changement de variante : un MutationObserver refait le travail. */
const NL = document.documentElement.lang.toLowerCase().startsWith('nl');
const MOTS = [' · Bon plan', ' · Koopje', ' · Sur commande', ' · Op bestelling'];
// 20/11/2026 (Amine) : date de livraison réelle selon le jour du visiteur. Le grossiste est commandé une fois par
// semaine, le lundi matin (clôture dimanche minuit) ; le colis arrive le mercredi, il est réexpédié le jour même et
// livré le jeudi (vendredi au plus tard). Heure de Bruxelles.
function livraison() {
  const p = {};
  new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Brussels', year: 'numeric', month: 'numeric', day: 'numeric', weekday: 'short' })
    .formatToParts(new Date()).forEach((x) => { p[x.type] = x.value; });
  const wd = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 7 }[p.weekday] || 1;
  const base = Date.UTC(+p.year, +p.month - 1, +p.day);
  const lundi = base + (8 - wd) * 864e5;
  const f = (t) => new Date(t).toLocaleDateString(NL ? 'nl-BE' : 'fr-BE', { timeZone: 'UTC', weekday: 'long', day: 'numeric', month: 'long' });
  const j = f(lundi + 3 * 864e5), v = f(lundi + 4 * 864e5);
  return NL ? 'bij jou geleverd tussen ' + j + ' en ' + v : 'livré chez toi entre le ' + j + ' et le ' + v;
}
const LIVRE = livraison();
const TEXTE = NL
  ? '<strong>Koopje</strong> — speciaal voor jou besteld, ' + LIVRE + '. Zelfde originele parfum, lagere prijs.'
  : '<strong>Bon plan</strong> — commandé spécialement pour toi, ' + LIVRE + '. Même parfum authentique, prix plus doux.';
const TEXTE_FICHE = NL
  ? '<strong>Koopje</strong> — speciaal voor jou besteld, ' + LIVRE + '. Origineel en nieuw parfum.'
  : '<strong>Bon plan</strong> — commandé spécialement pour toi, ' + LIVRE + '. Parfum authentique et neuf.';
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
