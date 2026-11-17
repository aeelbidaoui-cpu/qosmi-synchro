#!/usr/bin/env python3
"""Black Friday Qosmi (17/11/2026, demande d'Amine).

Règle : une remise automatique de X % sur une sélection de parfums, du vendredi 27/11/2026 00:00 au lundi 30/11/2026
23:59 (heure de Bruxelles), sans jamais passer sous 5 € de bénéfice net par format (règle de la boutique).

Bénéfice net d'un format au prix remisé p' = p' / 1,21 − 2 % × p' − 0,25 € − coût HT (achat + envoi + emballage, déjà
enregistré comme « coût par article » dans Shopify par la mise à jour horaire ; + 0,60 € d'emballage pour les Bons plans).
Une fiche entre dans la sélection seulement si TOUS ses formats en stock gardent au moins 5 € net à X %.

La sélection est une collection manuelle « black-friday » (NL « black-friday ») : la mise à jour horaire n'y touche pas.
La remise vise ces fiches une par une (pas d'étiquette, que la mise à jour pourrait réécrire).

Le dépôt est public : le journal n'affiche que des nombres, jamais un coût ni une marge.

Usage :
  --analyse            nombre de fiches possibles à 5, 10, 15, 20 %
  --appliquer PCT      crée ou met à jour la collection et la remise automatique (dates ci-dessous)
  --retirer            supprime la remise (la collection reste, sans effet)
"""
import json, os, sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

DEBUT, FIN = "2026-11-26T23:00:00Z", "2026-11-30T22:59:59Z"  # 27/11 00:00 → 30/11 23:59 Bruxelles
NET_MIN, TVA, PAIEMENT_PCT, PAIEMENT_FIXE, EMBALLAGE = 5.0, 0.21, 0.02, 0.25, 0.6
HANDLE, TITRE, TITRE_NL = "black-friday", "Black Friday", "Black Friday"
TITRE_REMISE = "Black Friday Qosmi"

Q = """query($a: String) { products(first: 100, after: $a, query: "status:active") {
  pageInfo { hasNextPage endCursor }
  nodes { id handle tags productType
    variants(first: 30) { nodes { sku price inventoryQuantity inventoryItem { unitCost { amount } } } } } } }"""


def net(prix, cout, sku):
    emb = EMBALLAGE if (sku or "").startswith(("QS-B", "QS-C", "QS-D")) else 0
    return prix / (1 + TVA) - PAIEMENT_PCT * prix - PAIEMENT_FIXE - cout - emb


def fiches(s):
    out, a = [], None
    while True:
        d = s.gql(Q, {"a": a})["products"]
        for p in d["nodes"]:
            tags = [t.lower() for t in p["tags"]]
            if "coffret" in (p["productType"] or "").lower() or "testeur" in tags:
                continue
            vs = []
            for v in p["variants"]["nodes"]:
                c = ((v.get("inventoryItem") or {}).get("unitCost") or {}).get("amount")
                if int(v.get("inventoryQuantity") or 0) <= 0:
                    continue
                if c is None:
                    vs = None
                    break
                vs.append((float(v["price"]), float(c), v["sku"]))
            if vs:
                out.append((p["id"], p["handle"], vs))
        if not d["pageInfo"]["hasNextPage"]:
            return out
        a = d["pageInfo"]["endCursor"]


def eligibles(liste, pct):
    return [f for f in liste if all(net(p * (1 - pct / 100.0), c, sku) >= NET_MIN for p, c, sku in f[2])]


def analyse():
    from shopify_api import Shopify
    liste = fiches(Shopify())
    print("Fiches en ligne avec au moins un format en stock : %d" % len(liste))
    for pct in (5, 10, 15, 20, 25):
        print("  à -%d %% : %d fiches gardent au moins %.0f € net sur tous leurs formats" % (pct, len(eligibles(liste, pct)), NET_MIN))


def appliquer(pct):
    from shopify_api import Shopify
    from seo_boutique import traduire
    from site_theme import publication_boutique
    s = Shopify()
    choix = eligibles(fiches(s), pct)
    ids = [f[0] for f in choix]
    texte = ("<p>Black Friday chez Qosmi : -%d %% sur une sélection de parfums authentiques, du vendredi 27 au lundi "
             "30 novembre. La remise s'applique automatiquement au panier.</p>" % pct)
    texte_nl = ("<p>Black Friday bij Qosmi: -%d %% op een selectie originele parfums, van vrijdag 27 tot maandag "
                "30 november. De korting wordt automatisch toegepast in je winkelmandje.</p>" % pct)
    ex = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": HANDLE}).get("collectionByIdentifier")
    champs = {"title": TITRE, "descriptionHtml": texte, "sortOrder": "BEST_SELLING",
              "seo": {"title": "Black Friday parfums | Qosmi", "description": "Black Friday : -%d %% sur une sélection de parfums authentiques, livrés partout en Belgique." % pct}}
    if ex:
        cid = ex["id"]
        s.gql("mutation($c: CollectionInput!) { collectionUpdate(input: $c) { userErrors { message } } }", {"c": dict(champs, id=cid)})
    else:
        r = s.gql("mutation($c: CollectionInput!) { collectionCreate(input: $c) { collection { id } userErrors { message } } }",
                  {"c": dict(champs, handle=HANDLE)})["collectionCreate"]
        if r["userErrors"]:
            sys.exit("Collection refusée : %s" % r["userErrors"])
        cid = r["collection"]["id"]
    synchroniser(s, cid, ids)
    pub = publication_boutique(s)
    if pub:
        s.gql("mutation($id: ID!, $p: ID!) { publishablePublish(id: $id, input: [{publicationId: $p}]) { userErrors { message } } }", {"id": cid, "p": pub})
    traduire(s, cid, {"title": TITRE_NL, "body_html": texte_nl, "meta_title": "Black Friday parfums | Qosmi",
                      "meta_description": "Black Friday: -%d %% op een selectie originele parfums, geleverd in heel België." % pct})
    # remise automatique sur la collection
    remise = {"title": TITRE_REMISE, "startsAt": DEBUT, "endsAt": FIN,
              "combinesWith": {"shippingDiscounts": True, "orderDiscounts": False, "productDiscounts": False},
              "customerGets": {"value": {"percentage": pct / 100.0}, "items": {"collections": {"add": [cid]}}}}
    d = s.gql('query { automaticDiscountNodes(first: 50, query: "title:\'%s\'") { nodes { id automaticDiscount { ... on DiscountAutomaticBasic { title } } } } }' % TITRE_REMISE)["automaticDiscountNodes"]["nodes"]
    d = [n for n in d if (n.get("automaticDiscount") or {}).get("title") == TITRE_REMISE]
    if d:
        r = s.gql("mutation($id: ID!, $a: DiscountAutomaticBasicInput!) { discountAutomaticBasicUpdate(id: $id, automaticBasicDiscount: $a) { userErrors { field message } } }",
                  {"id": d[0]["id"], "a": remise})["discountAutomaticBasicUpdate"]
    else:
        r = s.gql("mutation($a: DiscountAutomaticBasicInput!) { discountAutomaticBasicCreate(automaticBasicDiscount: $a) { userErrors { field message } } }",
                  {"a": remise})["discountAutomaticBasicCreate"]
    if r["userErrors"]:
        sys.exit("Remise refusée : %s" % r["userErrors"])
    print("OK Black Friday : -%d %% sur %d fiches, du 27/11 00:00 au 30/11 23:59 (Bruxelles) · collection %s" % (pct, len(ids), HANDLE))


def rafraichir(s):
    """Appelé à chaque mise à jour horaire (site_synchro.py) : du 26/11 à la fin du Black Friday, la sélection suit les
    prix du moment, pour qu'aucune fiche remisée ne passe sous 5 € net. Retourne le nombre de fiches, ou None hors période."""
    import datetime
    cfg = json.load(open(os.path.join(os.path.dirname(ICI), "config", "site.json"), encoding="utf-8")).get("black_friday") or {}
    if not cfg.get("actif"):
        return None
    maintenant = datetime.datetime.now(datetime.timezone.utc)
    debut = datetime.datetime.fromisoformat(DEBUT.replace("Z", "+00:00")) - datetime.timedelta(hours=30)
    fin = datetime.datetime.fromisoformat(FIN.replace("Z", "+00:00"))
    if not (debut <= maintenant <= fin):
        return None
    ex = s.gql("query($h: String!) { collectionByIdentifier(identifier: {handle: $h}) { id } }", {"h": HANDLE}).get("collectionByIdentifier")
    if not ex:
        return None
    return synchroniser(s, ex["id"], [f[0] for f in eligibles(fiches(s), int(cfg.get("pct", 10)))])


def synchroniser(s, cid, ids):
    actuels, a = [], None
    while True:
        d = s.gql("query($id: ID!, $a: String) { collection(id: $id) { products(first: 250, after: $a) { pageInfo { hasNextPage endCursor } nodes { id } } } }",
                  {"id": cid, "a": a})["collection"]["products"]
        actuels += [n["id"] for n in d["nodes"]]
        if not d["pageInfo"]["hasNextPage"]:
            break
        a = d["pageInfo"]["endCursor"]
    retirer_ = [i for i in actuels if i not in ids]
    ajouter = [i for i in ids if i not in actuels]
    for i in range(0, len(retirer_), 250):
        s.gql("mutation($id: ID!, $p: [ID!]!) { collectionRemoveProducts(id: $id, productIds: $p) { userErrors { message } } }", {"id": cid, "p": retirer_[i:i + 250]})
    for i in range(0, len(ajouter), 250):
        r = s.gql("mutation($id: ID!, $p: [ID!]!) { collectionAddProducts(id: $id, productIds: $p) { userErrors { message } } }",
                  {"id": cid, "p": ajouter[i:i + 250]})["collectionAddProducts"]
        if r["userErrors"]:
            raise RuntimeError("Ajout refusé : %s" % r["userErrors"])
    return len(ids)


def retirer():
    from shopify_api import Shopify
    s = Shopify()
    d = s.gql('query { automaticDiscountNodes(first: 50) { nodes { id automaticDiscount { ... on DiscountAutomaticBasic { title } } } } }')["automaticDiscountNodes"]["nodes"]
    for n in d:
        if (n.get("automaticDiscount") or {}).get("title") == TITRE_REMISE:
            s.gql("mutation($id: ID!) { discountAutomaticDelete(id: $id) { userErrors { message } } }", {"id": n["id"]})
            print("Remise Black Friday supprimée")


if __name__ == "__main__":
    if "--analyse" in sys.argv:
        analyse()
    elif "--appliquer" in sys.argv:
        appliquer(int(sys.argv[sys.argv.index("--appliquer") + 1]))
    elif "--retirer" in sys.argv:
        retirer()
    else:
        print(__doc__)
