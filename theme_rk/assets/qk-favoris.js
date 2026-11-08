/* Favoris Qosmi (08/11/2026) : liste de parfums gardée dans le navigateur (localStorage), sans compte client. */
(function () {
  var CLE = 'qk_favoris';
  var racine = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
  var nl = (document.documentElement.lang || '').indexOf('nl') === 0;
  function lire() { try { return JSON.parse(localStorage.getItem(CLE)) || []; } catch (e) { return []; } }
  function ecrire(l) { try { localStorage.setItem(CLE, JSON.stringify(l.slice(0, 100))); } catch (e) {} }
  var COEUR = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.3-9.2C1.4 8 3.4 4.5 7 4.5c2 0 3.4 1.1 5 3 1.6-1.9 3-3 5-3 3.6 0 5.6 3.5 4.3 6.8-1.8 4.6-9.3 9.2-9.3 9.2z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>';
  function maj() {
    var l = lire();
    document.querySelectorAll('[data-qk-fav]').forEach(function (b) {
      var on = l.indexOf(b.getAttribute('data-qk-fav')) >= 0;
      b.classList.toggle('is-on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    document.querySelectorAll('[data-qk-fav-compte]').forEach(function (c) { c.textContent = l.length || ''; c.hidden = !l.length; });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-qk-fav]');
    if (!b) return;
    e.preventDefault(); e.stopPropagation();
    var h = b.getAttribute('data-qk-fav'), l = lire(), i = l.indexOf(h);
    if (i >= 0) l.splice(i, 1); else l.unshift(h);
    ecrire(l); maj();
    document.dispatchEvent(new CustomEvent('qk:favoris'));
  }, true);
  function entete() {
    var zone = document.querySelector('header-actions');
    if (!zone || zone.querySelector('.qk-fav-entete')) return;
    var a = document.createElement('a');
    a.href = racine + 'pages/favoris';
    a.className = 'qk-fav-entete header-actions__action';
    a.setAttribute('aria-label', nl ? 'Mijn favorieten' : 'Mes favoris');
    a.innerHTML = COEUR + '<span class="qk-fav-compte" data-qk-fav-compte hidden></span>';
    zone.insertBefore(a, zone.firstChild);
  }
  function demarrer() { entete(); maj(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', demarrer); else demarrer();
  // cartes chargées plus tard (filtres, recherche, onglets)
  new MutationObserver(function () { clearTimeout(window.__qkFavT); window.__qkFavT = setTimeout(maj, 150); })
    .observe(document.documentElement, { childList: true, subtree: true });
  window.qkFavoris = { lire: lire, ecrire: ecrire, maj: maj };
})();
