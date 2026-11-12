#!/usr/bin/env python3
"""Alertes « de retour en stock » (12/11/2026, demande d'Amine). Lancé après chaque mise à jour du site.

Le formulaire des fiches épuisées (theme_rk/sections/qk-alerte.liquid) crée un contact Shopify avec les étiquettes
  alerte-stock · langue:fr|nl · attend:<id du format>:<AAAAMMJJ>
Ce script :
  1. format revenu en stock → code personnel : 5 % du prix, plafonné à 3 € (montant fixe, 1 usage, ce client, ce parfum,
     7 jours) ; étiquettes retour:<handle> + code:<CODE> + alerte-pret ;
  2. format toujours épuisé après 30 jours → 3 parfums aux notes proches en stock ; étiquettes propose:<handle> + alerte-pret.
Shopify Flow (déclencheur « étiquettes client ajoutées » = alerte-pret) envoie l'e-mail de la messagerie Shopify,
qui lit ces étiquettes, puis retire alerte-pret.

  python3 scripts/alertes_stock.py           # traite les alertes
  python3 scripts/alertes_stock.py --essai   # montre ce qui serait fait, sans rien changer
"""
import datetime as dt, json, math, os, random, re, string, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TAUX, PLAFOND, MINIMUM = 0.05, 3.00, 0.50
JOURS_CODE, JOURS_ATTENTE = 7, 30
ESSAI = "--essai" in sys.argv
# Test de bout en bout (accord d'Amine) : --simuler retour|perdu avec ALERTE_CLIENT = identifiant numérique du client test
SIMULER = sys.argv[sys.argv.index("--simuler") + 1] if "--simuler" in sys.argv else ""
SIMULER_CLIENT = os.environ.get("ALERTE_CLIENT", "").strip()
if SIMULER and not SIMULER_CLIENT:
    raise SystemExit("--simuler : identifiant du client test manquant (ALERTE_CLIENT)")


def log(*a):
    print(*a, flush=True)


def clients_en_attente(s):
    res, apres = [], None
    while True:
        r = s.gql("""query($a: String) { customers(first: 100, after: $a, query: "tag:alerte-stock") {
            nodes { id tags } pageInfo { hasNextPage endCursor } } }""", {"a": apres})["customers"]
        res += r["nodes"]
        if not r["pageInfo"]["hasNextPage"]:
            return res
        apres = r["pageInfo"]["endCursor"]


def formats(s, ids):
    out, ids = {}, list(ids)
    for i in range(0, len(ids), 100):
        r = s.gql("""query($ids: [ID!]!) { nodes(ids: $ids) { ... on ProductVariant { id availableForSale price
            product { id handle title status } } } }""", {"ids": ["gid://shopify/ProductVariant/%s" % x for x in ids[i:i + 100]]})
        for n in r["nodes"]:
            if n:
                out[n["id"].rsplit("/", 1)[1]] = n
    return out


def nouveau_code():
    return "QOSMI-" + "".join(random.choice(string.ascii_uppercase.replace("O", "").replace("I", "") + "23456789") for _ in range(6))


def creer_code(s, client_id, produits, montant):
    code = nouveau_code()
    debut = dt.datetime.now(dt.timezone.utc)
    entree = {"title": "Retour en stock %s" % code, "code": code, "startsAt": debut.isoformat(),
              "endsAt": (debut + dt.timedelta(days=JOURS_CODE)).isoformat(),
              "customerGets": {"value": {"discountAmount": {"amount": "%.2f" % montant, "appliesOnEachItem": False}},
                               "items": {"products": {"productsToAdd": produits}}},
              "usageLimit": 1, "appliesOncePerCustomer": True,
              "combinesWith": {"orderDiscounts": False, "productDiscounts": False, "shippingDiscounts": True}}
    for forme in ({"context": {"customers": {"add": [client_id]}}}, {"customerSelection": {"customers": {"add": [client_id]}}}):
        r = s.gql("""mutation($d: DiscountCodeBasicInput!) { discountCodeBasicCreate(basicCodeDiscount: $d) {
            codeDiscountNode { id } userErrors { field message } } }""", {"d": dict(entree, **forme)})["discountCodeBasicCreate"]
        if not r["userErrors"]:
            return code
        dernier = r["userErrors"]
    raise RuntimeError("code refusé : %s" % dernier)


def proches(handle, disponible, n=3):
    """Parfums aux notes proches (même calcul que la fiche), limités à ceux en stock."""
    import odeurs
    idx, _ = odeurs.construire_index()
    tout = [o[0].startswith("tout_") for o in idx["odeurs"]]
    P = {}
    for h, v in idx["parfums"].items():
        a, c = v.split("|")
        toutes = [int(x) for x in a.split(",") if x]
        P[h] = ({i for i in toutes if not tout[i]}, {int(x) for x in c.split(",") if x})
    if handle not in P or len(P[handle][0]) < 3:
        return []
    base = lambda h: re.sub(r"-(eau-de-(parfum|toilette|cologne)|extrait|parfum|cologne|elixir|intense|absolu|le-parfum).*$", "", h)
    sa, ca = P[handle]
    res = []
    for k, (sb, cb) in P.items():
        if k == handle or "coffret" in k or base(k) == base(handle):
            continue
        com = sa & sb
        if len(com) >= 2:
            sc = sum(1 + (i in ca) + 0.5 * (i in cb) for i in com) / math.sqrt(len(sa) * len(sb))
            res.append((sc, k))
    vu, choix = set(), []
    for _, k in sorted(res, reverse=True):
        if base(k) in vu:
            continue
        vu.add(base(k))
        if disponible(k):
            choix.append(k)
            if len(choix) == n:
                break
    return choix


def main():
    from shopify_api import Shopify
    s = Shopify()
    clients = clients_en_attente(s)
    attentes = {}
    for c in clients:
        for t in c["tags"]:
            m = re.match(r"attend:(\d+):(\d{8})$", t)
            if m:
                attentes.setdefault(c["id"], []).append((t, m.group(1), dt.datetime.strptime(m.group(2), "%Y%m%d").date()))
    log("Alertes : %d client(s), %d attente(s)" % (len(attentes), sum(len(v) for v in attentes.values())))
    if ESSAI:
        for cid, v in attentes.items():
            log("  client %s : %s" % (cid.rsplit("/", 1)[1], ", ".join(a[0] for a in v)))
    if not attentes:
        return
    F = formats(s, {a[1] for v in attentes.values() for a in v})
    cache = {}

    def disponible(h):
        if h not in cache:
            p = s.gql("query($h: String!) { productByIdentifier(identifier: {handle: $h}) { status totalInventory "
                      "variants(first: 10) { nodes { availableForSale } } } }", {"h": h})["productByIdentifier"]
            cache[h] = bool(p and p["status"] == "ACTIVE" and any(v["availableForSale"] for v in p["variants"]["nodes"]))
        return cache[h]

    aujourdhui, n_retour, n_propose = dt.date.today(), 0, 0
    for c in clients:
        if c["id"] not in attentes:
            continue
        retours, perdus, a_retirer = [], [], []
        for tag, vid, depuis in attentes[c["id"]]:
            v = F.get(vid)
            simule = SIMULER and c["id"].rsplit("/", 1)[1] == SIMULER_CLIENT
            if simule and SIMULER == "perdu" and v:
                perdus.append(v["product"]["handle"]); a_retirer.append(tag)
            elif (simule and v) or (v and v["availableForSale"] and v["product"]["status"] == "ACTIVE"):
                retours.append(v); a_retirer.append(tag)
            elif (aujourdhui - depuis).days >= JOURS_ATTENTE:
                perdus.append(v["product"]["handle"] if v else None); a_retirer.append(tag)
        if not retours and not perdus:
            continue
        ajout = []
        anciens = [t for t in c["tags"] if t.startswith(("retour:", "code:", "propose:"))]
        if retours:
            prix = min(float(v["price"]) for v in retours)
            montant = max(MINIMUM, min(round(prix * TAUX, 2), PLAFOND))
            produits = sorted({v["product"]["id"] for v in retours})
            code = "ESSAI" if ESSAI else creer_code(s, c["id"], produits, montant)
            ajout += ["retour:" + v["product"]["handle"] for v in retours] + ["code:" + code, "remise:%.2f" % montant]
            n_retour += 1
            log("  retour en stock : %s → %s (code %s, %.2f €)" % (c["id"].rsplit("/", 1)[1], ", ".join(v["product"]["title"] for v in retours), code, montant))
        elif perdus:
            props = []
            for h in perdus:
                if h:
                    props += [p for p in proches(h, disponible) if p not in props]
            if props:
                ajout += ["propose:" + h for h in props[:3]]
                n_propose += 1
                log("  pas revenu en 30 jours : %s → %s" % (c["id"].rsplit("/", 1)[1], ", ".join(props[:3])))
            else:
                log("  pas revenu en 30 jours, rien de proche en stock : %s (alerte close)" % c["id"].rsplit("/", 1)[1])
        if ESSAI:
            continue
        # « alerte-pret » resté d'un envoi précédent (si Flow ne l'a pas retiré) : on l'enlève, sinon le nouvel ajout ne déclencherait rien
        retirer = a_retirer + anciens + [t for t in c["tags"] if t.startswith("remise:") or t == "alerte-pret"]
        if retirer:
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsRemove(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": retirer})
        if ajout:
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsAdd(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": ajout})
            # « alerte-pret » en dernier : c'est lui qui déclenche l'e-mail dans Shopify Flow
            s.gql("mutation($id: ID!, $t: [String!]!) { tagsAdd(id: $id, tags: $t) { userErrors { message } } }", {"id": c["id"], "t": ["alerte-pret"]})
    log("OK alertes : %d e-mail(s) « de retour » et %d « parfums proches » déclenchés%s" % (n_retour, n_propose, " (essai, rien changé)" if ESSAI else ""))


if __name__ == "__main__":
    main()
