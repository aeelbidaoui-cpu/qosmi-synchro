"""Version anglaise (23/11/2026) : noms des filtres de la boutique (odeurs, saisons, occasions = métaobjets « nom »)."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
EN = {
    "Bergamote": "Bergamot", "Citron": "Lemon", "Orange & mandarine": "Orange & mandarin", "Pamplemousse": "Grapefruit",
    "Rose": "Rose", "Jasmin": "Jasmine", "Fleur d'oranger & néroli": "Orange blossom & neroli", "Iris": "Iris",
    "Violette": "Violet", "Tubéreuse": "Tuberose", "Ylang-ylang": "Ylang-ylang", "Muguet": "Lily of the valley",
    "Pivoine": "Peony", "Fleurs blanches": "White flowers", "Géranium": "Geranium", "Héliotrope & poudré": "Heliotrope & powdery",
    "Orchidée": "Orchid", "Osmanthus": "Osmanthus", "Pomme": "Apple", "Poire": "Pear", "Pêche & abricot": "Peach & apricot",
    "Fruits rouges": "Red berries", "Cassis": "Blackcurrant", "Fruits exotiques": "Tropical fruits",
    "Prune & fruits secs": "Plum & dried fruits", "Figue": "Fig", "Melon & pastèque": "Melon & watermelon", "Vanille": "Vanilla",
    "Fève tonka": "Tonka bean", "Caramel & praliné": "Caramel & praline", "Chocolat & cacao": "Chocolate & cocoa", "Café": "Coffee",
    "Miel": "Honey", "Amande & noisette": "Almond & hazelnut", "Noix de coco": "Coconut", "Lait & crème": "Milk & cream",
    "Rhum & cognac": "Rum & cognac", "Cannelle": "Cinnamon", "Cardamome": "Cardamom", "Safran": "Saffron",
    "Poivre & baies roses": "Pepper & pink pepper", "Gingembre": "Ginger", "Muscade & clou de girofle": "Nutmeg & clove",
    "Santal": "Sandalwood", "Cèdre": "Cedar", "Vétiver": "Vetiver", "Patchouli": "Patchouli", "Oud": "Oud",
    "Bois fumés": "Smoky woods", "Mousse de chêne": "Oakmoss", "Ambre": "Amber", "Ambre gris": "Ambergris",
    "Encens & myrrhe": "Incense & myrrh", "Benjoin & baumes": "Benzoin & balsams", "Musc": "Musk", "Cuir": "Leather",
    "Tabac": "Tobacco", "Lavande": "Lavender", "Menthe": "Mint", "Sauge": "Sage", "Romarin & herbes": "Rosemary & herbs",
    "Marin & salé": "Marine & salty", "Notes vertes": "Green notes", "Thé": "Tea", "Pin & genièvre": "Pine & juniper",
    "Printemps": "Spring", "Été": "Summer", "Automne": "Autumn", "Hiver": "Winter",
    "Tous les jours": "Every day", "Bureau": "Office", "Rendez-vous": "Date", "Dîner": "Dinner", "Soirée": "Night out",
    "Mariage": "Wedding", "Sport": "Sport", "Vacances": "Holidays", "Événement chic": "Formal event", "Détente": "Relaxing",
}
Q = """query($a: String) { translatableResources(first: 100, after: $a, resourceType: METAOBJECT) {
  pageInfo { hasNextPage endCursor } nodes { resourceId translatableContent { key value digest } } } }"""
M = """mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }"""


def main():
    from shopify_api import Shopify
    s = Shopify()
    apres, ok, inconnus = None, 0, []
    while True:
        d = s.gql(Q, {"a": apres})["translatableResources"]
        for n in d["nodes"]:
            for c in n["translatableContent"]:
                if c["key"] != "nom":
                    continue
                en = EN.get(c["value"])
                if not en:
                    inconnus.append(c["value"])
                    continue
                r = s.gql(M, {"id": n["resourceId"], "t": [{"locale": "en", "key": "nom", "value": en,
                                                            "translatableContentDigest": c["digest"]}]})["translationsRegister"]
                ok += 0 if r["userErrors"] else 1
        if not d["pageInfo"]["hasNextPage"]:
            break
        apres = d["pageInfo"]["endCursor"]
    print("Filtres en anglais : %d traduits ; sans traduction : %s" % (ok, inconnus or "aucun"))


if __name__ == "__main__":
    main()
