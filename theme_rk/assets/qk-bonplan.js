/* Option « Bon plan » sur les fiches (14/11/2026, demande d'Amine).
   Pour certains formats, une 2e variante « 100 ml · Bon plan » (NL « · Koopje ») : même parfum, commandé spécialement,
   un peu plus de délai, prix plus bas. Ce script :
   - cache l'option « Bon plan » quand elle est épuisée (elle « disparaît » au lieu d'apparaître barrée) ;
   - affiche sous le choix du format une ligne qui explique le délai quand l'option « Bon plan » est choisie.
   Le thème Horizon redessine le sélecteur à chaque changement de variante : un MutationObserver refait le travail. */
const NL = document.documentElement.lang.toLowerCase().startsWith('nl');
const MOTS = [' · Bon plan', ' · Koopje', ' · Sur commande', ' · Op bestelling'];
const COMMANDE = [' · Sur commande', ' · Op bestelling'];
const DELAI = NL ? '5 tot 10 werkdagen' : '5 à 10 jours ouvrables';
const TEXTE = NL
  ? '<strong>Koopje</strong> — speciaal voor jou besteld, verzonden binnen ' + DELAI + '. Zelfde originele parfum, lagere prijs.'
  : '<strong>Bon plan</strong> — commandé spécialement pour toi, expédié sous ' + DELAI + '. Même parfum authentique, prix plus doux.';

const TEXTE_COMMANDE = NL
  ? '<strong>Op bestelling</strong> — speciaal voor jou besteld, verzonden binnen ' + DELAI + '. Origineel en nieuw parfum.'
  : '<strong>Sur commande</strong> — commandé spécialement pour toi, expédié sous ' + DELAI + '. Parfum authentique et neuf.';
const estBonPlan = (v) => MOTS.some((m) => (v || '').includes(m));
const estCommande = (v) => COMMANDE.some((m) => (v || '').includes(m));

function traiter() {
  document.querySelectorAll('variant-picker, .variant-picker').forEach((picker) => {
    let choisi = false, commande = false;
    picker.querySelectorAll('input[type="radio"]').forEach((i) => {
      if (!estBonPlan(i.value)) return;
      const label = i.closest('label') || i.parentElement;
      const epuise = i.getAttribute('data-option-available') === 'false';
      if (label) label.hidden = epuise && !i.checked;
      if (i.checked) { choisi = true; commande = estCommande(i.value); }
    });
    picker.querySelectorAll('select option').forEach((o) => {
      if (!estBonPlan(o.value)) return;
      const epuise = o.getAttribute('data-option-available') === 'false' || /épuisé|uitverkocht|sold out/i.test(o.textContent);
      o.hidden = epuise && !o.selected;
      if (o.selected) { choisi = true; commande = estCommande(o.value); }
    });
    let note = picker.parentElement && picker.parentElement.querySelector(':scope > .qk-bonplan-note');
    const texte = commande ? TEXTE_COMMANDE : TEXTE;
    if (choisi && !note) {
      note = document.createElement('p');
      note.className = 'qk-bonplan-note';
      note.innerHTML = texte;
      note.dataset.genre = commande ? 'c' : 'b';
      picker.after(note);
    } else if (choisi && note && note.dataset.genre !== (commande ? 'c' : 'b')) {
      note.innerHTML = texte;
      note.dataset.genre = commande ? 'c' : 'b';
    } else if (!choisi && note) {
      note.remove();
    }
  });
}

let minuteur = null;
new MutationObserver(() => { clearTimeout(minuteur); minuteur = setTimeout(traiter, 60); })
  .observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['checked', 'data-option-available'] });
document.addEventListener('change', () => setTimeout(traiter, 30));
traiter();
