/* Point relais Mondial Relay dans le tiroir du panier (19/11/2026, demande d'Amine : « pq y a pas la carte ? »).
   Même carte officielle et gratuite que sur la page panier (section qk-point-relais, code enseigne public CC245ET3),
   au-dessus du bouton « Payer ». Le point choisi va dans l'attribut du panier « Point relais Mondial Relay ».
   Les scripts de la carte ne se chargent qu'au clic. Horizon redessine le tiroir à chaque changement : un
   MutationObserver remet le bloc en place. Sur la page /cart, la section qk-point-relais fait déjà le travail. */
const NL = document.documentElement.lang.toLowerCase().startsWith('nl');
const CLE = 'Point relais Mondial Relay';
const T = NL
  ? { titre: 'Levering in een afhaalpunt?', aide: 'Kies je Mondial Relay-afhaalpunt op de kaart en neem daarna « Mondial Relay-afhaalpunt » bij het afrekenen.',
      choisir: 'Kies mijn afhaalpunt', changer: 'Ander afhaalpunt kiezen', choisi: '✓ Gekozen afhaalpunt:',
      erreur: 'De kaart kon niet laden. Geen probleem: we kiezen het afhaalpunt het dichtst bij je adres.' }
  : { titre: 'Livraison en point relais ?', aide: 'Choisis ton point relais Mondial Relay sur la carte, puis prends « Point relais Mondial Relay » au paiement.',
      choisir: 'Choisir mon point relais', changer: 'Changer de point relais', choisi: '✓ Point relais choisi :',
      erreur: "La carte n'a pas pu se charger. Pas de souci : on prendra le point relais le plus proche de ton adresse." };
let actuel = null;
let scripts = null;

function charger(src) {
  return new Promise((ok, ko) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = ko; document.head.appendChild(s); });
}

function librairies() {
  if (scripts) return scripts;
  const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'; document.head.appendChild(l);
  scripts = (window.jQuery ? Promise.resolve() : charger('https://code.jquery.com/jquery-3.7.1.min.js'))
    .then(() => charger('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'))
    .then(() => charger('https://widget.mondialrelay.com/parcelshop-picker/jquery.plugin.mondialrelay.parcelshoppicker.min.js'));
  return scripts;
}

function maj(bloc) {
  const p = bloc.querySelector('.qk-prt__choisi');
  p.hidden = !actuel;
  p.querySelector('strong').textContent = actuel || '';
  bloc.querySelector('.qk-prt__bouton').textContent = actuel ? T.changer : T.choisir;
}

function enregistrer(d, bloc) {
  const texte = [d.ID, d.Nom, [d.Adresse1, d.Adresse2].filter(Boolean).join(' '), d.CP + ' ' + d.Ville].filter(Boolean).join(' · ');
  fetch('/cart/update.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ attributes: { [CLE]: texte } }) })
    .then(() => {
      actuel = texte;
      document.querySelectorAll('.qk-prt').forEach(maj);
      bloc.querySelector('.qk-prt__zone').hidden = true;
    });
}

function bloc() {
  const d = document.createElement('div');
  d.className = 'qk-prt';
  const id = 'qk-prt-' + Math.random().toString(36).slice(2, 8);
  d.innerHTML = '<p class="qk-prt__titre"></p><p class="qk-prt__choisi" hidden><span></span> <strong></strong></p>' +
    '<p class="qk-prt__aide"></p><button type="button" class="qk-prt__bouton"></button>' +
    '<div class="qk-prt__zone" id="' + id + '" hidden></div><input type="hidden" id="' + id + '-cible">';
  d.querySelector('.qk-prt__titre').textContent = T.titre;
  d.querySelector('.qk-prt__choisi span').textContent = T.choisi;
  d.querySelector('.qk-prt__aide').textContent = T.aide;
  const zone = d.querySelector('.qk-prt__zone');
  const btn = d.querySelector('.qk-prt__bouton');
  btn.addEventListener('click', () => {
    zone.hidden = false;
    if (zone.dataset.pret) return;
    zone.dataset.pret = '1';
    btn.disabled = true;
    librairies().then(() => {
      btn.disabled = false;
      window.jQuery('#' + id).MR_ParcelShopPicker({
        Target: '#' + id + '-cible', Brand: 'CC245ET3', Country: 'BE', AllowedCountries: 'BE', ColLivMod: '24R',
        NbResults: '7', Responsive: true, ShowResultsOnMap: true, EnableGeolocalisatedSearch: false,
        OnParcelShopSelected: (x) => enregistrer(x, d)
      });
    }).catch(() => { btn.disabled = false; zone.textContent = T.erreur; });
  });
  maj(d);
  return d;
}

function placer() {
  if (/\/cart\/?$/.test(location.pathname)) return;
  document.querySelectorAll('.cart__ctas').forEach((ctas) => {
    if (ctas.parentElement.querySelector('.qk-prt')) return;
    ctas.before(bloc());
  });
}

fetch('/cart.js').then((r) => r.json()).then((c) => {
  actuel = (c.attributes && c.attributes[CLE]) || null;
  document.querySelectorAll('.qk-prt').forEach(maj);
}).catch(() => {});

let minuteur = null;
new MutationObserver(() => { clearTimeout(minuteur); minuteur = setTimeout(placer, 150); })
  .observe(document.body, { childList: true, subtree: true });
placer();
