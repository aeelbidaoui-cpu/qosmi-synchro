/* Recherche par odeurs et parfums aux notes proches (12/11/2026).
   Données : window.QK_ODEURS (assets/qk-odeurs.js, généré par scripts/odeurs.py).
   Les fiches (prix, photo, stock) sont lues en direct sur /products/<handle>.js. */
(function () {
  var D = window.QK_ODEURS;
  if (!D) return;
  var racine = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
  var odeurs = D.odeurs.map(function (o, i) { return { i: i, id: o[0], fam: o[1], fr: o[2], nl: o[3], tout: o[0].indexOf('tout_') === 0 }; });
  var parId = {};
  odeurs.forEach(function (o) { parId[o.id] = o; });
  var P = {};
  Object.keys(D.parfums).forEach(function (h) {
    var x = D.parfums[h].split('|');
    var toutes = x[0] ? x[0].split(',').map(Number) : [], cles = x[1] ? x[1].split(',').map(Number) : [];
    var spec = toutes.filter(function (i) { return !odeurs[i].tout; });
    P[h] = { toutes: toutes, cles: cles, spec: spec };
  });
  var COEUR = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.3-9.2C1.4 8 3.4 4.5 7 4.5c2 0 3.4 1.1 5 3 1.6-1.9 3-3 5-3 3.6 0 5.6 3.5 4.3 6.8-1.8 4.6-9.3 9.2-9.3 9.2z" fill="currentColor" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>';

  function base(h) { return h.replace(/-(eau-de-(parfum|toilette|cologne)|extrait|parfum|cologne|elixir|intense|absolu|le-parfum).*$/, ''); }
  function euros(c) { return (c / 100).toFixed(2).replace('.', ',') + ' €'; }
  /* une seule version d'un même parfum (EDP, EDT, parfum…) : la mieux classée */
  function unique(l) { var vu = {}; return l.filter(function (r) { var b = base(r.h); if (vu[b]) return false; vu[b] = 1; return true; }); }
  var cache = {};
  function produit(h) {
    if (!cache[h]) cache[h] = fetch(racine + 'products/' + h + '.js').then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
    return cache[h];
  }
  function nomOdeur(i, nl) { var o = odeurs[i]; return nl ? o.nl : o.fr; }

  /* Parfums qui ont le plus d'odeurs choisies (indices), notes clés d'abord. */
  function chercher(sel) {
    var res = [];
    Object.keys(P).forEach(function (h) {
      if (h.indexOf('coffret') >= 0) return;
      var p = P[h], m = 0, c = 0, eus = [];
      sel.forEach(function (i) {
        if (p.toutes.indexOf(i) >= 0) { m++; eus.push(i); if (p.cles.indexOf(i) >= 0) c++; }
      });
      if (m) res.push({ h: h, m: m, eus: eus, s: m * 10 + c * 2 - p.spec.length * 0.05 });
    });
    res.sort(function (a, b) { return b.s - a.s; });
    return unique(res);
  }

  /* Parfums aux notes les plus proches d'un parfum. */
  function proches(h) {
    var a = P[h];
    if (!a || a.spec.length < 3) return [];
    var b0 = base(h), res = [];
    Object.keys(P).forEach(function (k) {
      if (k === h || k.indexOf('coffret') >= 0 || base(k) === b0) return;
      var b = P[k], com = [], s = 0;
      a.spec.forEach(function (i) {
        if (b.spec.indexOf(i) >= 0) { com.push(i); s += 1 + (a.cles.indexOf(i) >= 0 ? 1 : 0) + (b.cles.indexOf(i) >= 0 ? 0.5 : 0); }
      });
      if (com.length >= 2) res.push({ h: k, eus: com, s: s / Math.sqrt(a.spec.length * b.spec.length) });
    });
    res.sort(function (x, y) { return y.s - x.s; });
    return unique(res);
  }

  /* Carte produit (même rendu que les cartes du thème). Rien si le parfum n'est plus en vente. */
  function carte(r, nl, total) {
    return produit(r.h).then(function (p) {
      if (!p || !p.available || !p.featured_image) return null;
      var t = (p.title || '').split(' — '), nom = t[0].replace(p.vendor, '').trim() || t[0];
      var a = document.createElement('a');
      a.className = 'qk-carte qk-odeurs__carte';
      a.href = p.url;
      a.innerHTML = '<span class="qk-carte__img"><img loading="lazy" alt="" src="' + p.featured_image + (p.featured_image.indexOf('?') >= 0 ? '&' : '?') + 'width=600">' +
        '<button type="button" class="qk-fav qk-fav--carte" data-qk-fav="' + p.handle + '" aria-pressed="false" aria-label="' +
        (nl ? 'Toevoegen aan favorieten' : 'Ajouter aux favoris') + '">' + COEUR + '</button></span>' +
        '<span class="qk-carte__ligne"><span class="qk-carte__marque"></span><span class="qk-carte__prix">' +
        (p.price_varies ? (nl ? 'vanaf ' : 'dès ') : '') + euros(p.price_min) + '</span></span><span class="qk-carte__nom"></span>' +
        '<span class="qk-odeurs__communes"></span>';
      a.querySelector('.qk-carte__marque').textContent = p.vendor;
      a.querySelector('.qk-carte__nom').textContent = nom;
      var noms = r.eus.filter(function (i) { return !odeurs[i].tout || total; }).slice(0, 4).map(function (i) { return nomOdeur(i, nl); });
      a.querySelector('.qk-odeurs__communes').textContent = (total ? (r.m + '/' + total + ' · ') : '') + noms.join(' · ');
      return a;
    });
  }

  /* Remplit « grille » avec jusqu'à n cartes disponibles, à partir de la position « depart » de la liste ; renvoie la position atteinte. */
  function remplir(grille, liste, depart, n, nl, total) {
    var i = depart, mis = 0;
    function lot() {
      if (mis >= n || i >= liste.length) return Promise.resolve(i);
      var tranche = liste.slice(i, i + Math.max(6, n - mis));
      i += tranche.length;
      return Promise.all(tranche.map(function (r) { return carte(r, nl, total); })).then(function (cartes) {
        cartes.forEach(function (c) { if (c && mis < n) { grille.appendChild(c); mis++; } });
        if (window.qkFavoris) qkFavoris.maj();
        return lot();
      });
    }
    return lot();
  }

  window.qkOdeurs = { odeurs: odeurs, parId: parId, familles: D.familles, chercher: chercher, proches: proches, remplir: remplir, nom: nomOdeur, connu: function (h) { return !!P[h]; } };
  document.dispatchEvent(new CustomEvent('qk:odeurs'));
})();
