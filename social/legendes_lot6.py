#!/usr/bin/env python3
"""Qosmi — lot n°6 « Le bon parfum pour chaque moment » (29 publications), demandé par Amine le 18/11/2026.

Parfums en stock sur qosmi.be le 18/11/2026, jamais montrés dans les lots 1 à 5. Occasions, saisons, tenue et sillage :
profils Qosmi (config/profils_parfums.json, d'après Fragrance Index et Fragrantica). Un jour sur deux en néerlandais.
Les dates sont posées par scripts/social_planning.py (deux publications par jour).

  python3 social/legendes_lot6.py   → social/lot6/lot6.json ; visuels : social/visuels_lot6.py
"""
import datetime as dt, json, os
import legendes_lot5 as L5

ICI = os.path.dirname(os.path.abspath(__file__))
PROFILS = L5.PROFILS
TAGS_FR = "#parfum #conseilparfum #parfumtiktok #qosmi"
TAGS_NL = "#parfum #parfumtips #parfumtok #qosmi"

P = {
    "profondo": ("giorgio-armani-acqua-di-gio-profondo-eau-de-toilette-pour-homme", "Giorgio Armani", "Acqua di Giò Profondo"),
    "lr-ocean": ("prada-luna-rossa-ocean-eau-de-toilette-pour-homme", "Prada", "Luna Rossa Ocean"),
    "cythere": ("hermes-un-jardin-a-cythere-eau-de-toilette-mixte", "Hermès", "Un Jardin à Cythère"),
    "la-bomba": ("carolina-herrera-la-bomba-eau-de-parfum-pour-femme-2", "Carolina Herrera", "La Bomba"),
    "beau-narcisse": ("jean-paul-gaultier-le-beau-narcisse-eau-de-parfum-pour-homme", "Jean Paul Gaultier", "Le Beau Narcisse"),
    "shinanay": ("nishane-shinanay-extrait-de-parfum-mixte", "Nishane", "Shinanay"),
    "phantom-elixir": ("paco-rabanne-phantom-elixir-parfum-pour-homme", "Paco Rabanne", "Phantom Elixir"),
    "tero": ("nishane-tero-extrait-de-parfum-mixte", "Nishane", "Tero"),
    "9pm-elixir": ("afnan-9pm-elixir-extrait-de-parfum-mixte", "Afnan", "9pm Elixir"),
    "english-pear": ("jo-malone-english-pear-sweet-pea-eau-de-cologne-mixte", "Jo Malone", "English Pear & Sweet Pea"),
    "mandarino": ("acqua-di-parma-blu-mediterraneo-mandarino-di-sicilia-eau-de-toilette-mixte", "Acqua di Parma", "Mandarino di Sicilia"),
    "summer-vibes": ("dolce-gabbana-light-blue-summer-vibes-eau-de-toilette-pour-femme", "Dolce & Gabbana", "Light Blue Summer Vibes"),
    "guilty-absolu": ("gucci-guilty-absolu-de-parfum-parfum-pour-femme", "Gucci", "Guilty Absolu de Parfum"),
    "sapparot": ("montale-oud-sapparot-eau-de-parfum-mixte", "Montale", "Oud Sapparot"),
    "kunafa": ("armaf-kunafa-chocolate-eau-de-parfum-mixte", "Armaf", "Kunafa Chocolate"),
    "idole-power": ("lancome-idole-power-eau-de-parfum-pour-femme", "Lancôme", "Idôle Power"),
    "cobalt-absolute": ("carolina-herrera-bad-boy-cobalt-absolute-eau-de-parfum-pour-homme", "Carolina Herrera", "Bad Boy Cobalt Absolute"),
    "very-floral": ("givenchy-irresistible-very-floral-eau-de-parfum-pour-femme", "Givenchy", "Irresistible Very Floral"),
    "everyone": ("calvin-klein-ck-everyone-eau-de-parfum-mixte", "Calvin Klein", "CK Everyone"),
    "wood-sage": ("jo-malone-wood-sage-sea-salt-eau-de-cologne-mixte", "Jo Malone", "Wood Sage & Sea Salt"),
    "atlas": ("lattafa-atlas-eau-de-parfum-mixte", "Lattafa", "Atlas"),
    "fahrenheit": ("dior-fahrenheit-le-parfum-parfum-pour-homme", "Dior", "Fahrenheit Le Parfum"),
    "oud-greatness": ("initio-black-gold-project-oud-for-greatness-eau-de-parfum-mixte", "Initio", "Oud for Greatness"),
    "nashama": ("lattafa-al-nashama-eau-de-parfum-mixte", "Lattafa", "Al Nashama"),
    "elle": ("yves-saint-laurent-elle-2024-eau-de-parfum-pour-femme", "Yves Saint Laurent", "Elle"),
    "aoud-violet": ("mancera-aoud-violet-eau-de-parfum-pour-femme", "Mancera", "Aoud Violet"),
    "ombre-merveilles": ("hermes-l-ombre-des-merveilles-eau-de-parfum-mixte", "Hermès", "L'Ombre des Merveilles"),
    "orange-blossom": ("jo-malone-orange-blossom-eau-de-cologne-mixte", "Jo Malone", "Orange Blossom"),
    "victoria": ("lattafa-victoria-eau-de-parfum-mixte", "Lattafa", "Victoria"),
    "twilly": ("hermes-twilly-d-hermes-eau-de-parfum-pour-femme", "Hermès", "Twilly d'Hermès"),
    "chance": ("chanel-chance-eau-de-toilette-pour-femme", "Chanel", "Chance"),
    "black-opium": ("yves-saint-laurent-black-opium-eau-de-parfum-pour-femme-2", "Yves Saint Laurent", "Black Opium"),
    "lveb-elixir": ("lancome-la-vie-est-belle-l-elixir-eau-de-parfum-pour-femme", "Lancôme", "La Vie est Belle L'Elixir"),
    "adg": ("giorgio-armani-acqua-di-gio-eau-de-toilette-pour-homme", "Giorgio Armani", "Acqua di Giò"),
    "scandal": ("jean-paul-gaultier-scandal-eau-de-parfum-pour-femme", "Jean Paul Gaultier", "Scandal"),
    "eros": ("versace-eros-eau-de-toilette-pour-homme", "Versace", "Eros"),
    "phantom": ("paco-rabanne-phantom-eau-de-toilette-pour-homme", "Paco Rabanne", "Phantom"),
    "interdit-rouge": ("givenchy-l-interdit-rouge-eau-de-parfum-pour-femme", "Givenchy", "L'Interdit Rouge"),
    "mon-guerlain": ("guerlain-mon-guerlain-eau-de-parfum-pour-femme", "Guerlain", "Mon Guerlain"),
    "allure-blanche": ("chanel-allure-homme-edition-blanche-eau-de-parfum-pour-homme", "Chanel", "Allure Homme Édition Blanche"),
    "fb-nectar": ("viktor-rolf-flowerbomb-nectar-eau-de-parfum-pour-femme", "Viktor & Rolf", "Flowerbomb Nectar"),
    "daisy": ("marc-jacobs-daisy-eau-de-toilette-pour-femme", "Marc Jacobs", "Daisy"),
    "bad-boy": ("carolina-herrera-bad-boy-eau-de-toilette-pour-homme", "Carolina Herrera", "Bad Boy"),
    "pure-crystal": ("lattafa-pure-crystal-eau-de-parfum-mixte", "Lattafa", "Pure Crystal"),
}

# étiquette sur le visuel (fr, nl) : le moment idéal, d'après le profil
MOMENT = {
    "bureau": ("Idéal au bureau", "Ideaal op kantoor"), "rdv": ("Pour un rendez-vous", "Voor een date"),
    "lendemain": ("Tient jusqu'au lendemain", "Blijft tot de volgende dag"), "discret": ("Sillage discret", "Discrete sillage"),
    "cosy": ("Cosy en hiver", "Cosy in de winter"), "mariage": ("Pour un mariage", "Voor een huwelijk"),
    "sport": ("Frais et énergique", "Fris en energiek"), "soiree": ("Pour sortir le soir", "Om 's avonds uit te gaan"),
    "mystere": ("Mystérieux", "Mysterieus"), "printemps": ("Pour le printemps", "Voor de lente"),
    "jour": ("Pour tous les jours", "Voor elke dag"), "hiver": ("Pour l'hiver", "Voor de winter"),
}
SIG = {}

L = []


def pub(cle_id, type_, titre, titre_nl, txt, txt_nl, **k):
    L.append(dict(id="l6-%02d-%s" % (len(L) + 1, cle_id), type=type_, langue="nl" if len(L) % 2 == 0 else "fr",
                  titre=titre, titre_nl=titre_nl, txt=txt, txt_nl=txt_nl, **k))


def sel(cle_id, moment, titre, titre_nl, couv, couv_nl, cles, txt, txt_nl):
    for c in cles:
        SIG.setdefault((cle_id, c), MOMENT[moment])
    pub(cle_id, "sel", titre, titre_nl, txt, txt_nl, parfums=cles, couv=(couv, couv_nl), moment=moment)


def pdj(cle, moment, txt, txt_nl):
    h, marque, nom = P[cle]
    pub(cle, "pdj", "%s, %s" % (nom, marque), "%s, %s" % (nom, marque), txt, txt_nl, parfums=[cle], moment=moment)


sel("bureau", "bureau", "3 parfums pour le bureau", "3 parfums voor op kantoor", "3 parfums<br>pour le<br>bureau", "3 parfums<br>voor op<br>kantoor",
    ["profondo", "lr-ocean", "cythere"],
    "Au bureau, on veut sentir bon sans envahir l'open space.\n\nAcqua di Giò Profondo (marin et aromatique), Luna Rossa Ocean (lavande, iris et daim) "
    "et Un Jardin à Cythère (agrumes, olivier et pistache) : trois parfums frais au sillage léger. Glisse 👉",
    "Op kantoor wil je lekker ruiken zonder de hele ruimte te vullen.\n\nAcqua di Giò Profondo (marien en aromatisch), Luna Rossa Ocean (lavendel, iris en suède) "
    "en Un Jardin à Cythère (citrus, olijfboom en pistache): drie frisse parfums met een lichte sillage. Swipe 👉")
pdj("chance", "jour",
    "Chance de Chanel, c'est la gaieté en flacon rond.\n\nAnanas, jacinthe et baies roses, un cœur de jasmin et de rose, sur un fond de musc, de patchouli et de vanille. "
    "Floral et pétillant, pour tous les jours.",
    "Chance van Chanel is vrolijkheid in een ronde flacon.\n\nAnanas, hyacint en roze peper, een hart van jasmijn en roos, op een basis van musk, patchouli en vanille. "
    "Bloemig en sprankelend, voor elke dag.")
sel("rdv", "rdv", "3 parfums pour un premier rendez-vous", "3 parfums voor een eerste date", "3 parfums<br>pour un premier<br>rendez-vous", "3 parfums<br>voor een<br>eerste date",
    ["beau-narcisse", "shinanay", "mon-guerlain"],
    "Un premier rendez-vous, c'est aussi une première impression.\n\nLe Beau Narcisse (coco, fleur d'oranger, tonka), Shinanay de Nishane (fleurs blanches et bois) "
    "et Mon Guerlain (lavande, iris, vanille) : trois parfums doux et enveloppants. Glisse 👉",
    "Een eerste date is ook een eerste indruk.\n\nLe Beau Narcisse (kokos, oranjebloesem, tonka), Shinanay van Nishane (witte bloemen en hout) "
    "en Mon Guerlain (lavendel, iris, vanille): drie zachte, omhullende parfums. Swipe 👉")
pdj("black-opium", "soiree",
    "Black Opium d'Yves Saint Laurent : le café rencontre la vanille.\n\nPoire, fleur d'oranger et baies roses, un cœur de café et de jasmin, sur un fond de vanille, "
    "de patchouli et de cèdre. Gourmand et nocturne.",
    "Black Opium van Yves Saint Laurent: koffie ontmoet vanille.\n\nPeer, oranjebloesem en roze peper, een hart van koffie en jasmijn, op een basis van vanille, "
    "patchouli en ceder. Gourmand en nachtelijk.")
pub("conseil-tenue", "conseil", "Tenue et sillage : quelle différence ?", "Houdbaarheid en sillage: wat is het verschil?",
    "On confond souvent les deux. La tenue, c'est combien de temps ton parfum reste sur ta peau. Le sillage, c'est jusqu'où on le sent autour de toi. Glisse 👉",
    "Ze worden vaak verward. Houdbaarheid is hoe lang je parfum op je huid blijft. Sillage is hoe ver men het rond jou ruikt. Swipe 👉",
    couv=("Tenue<br>et sillage :<br>la différence", "Houdbaarheid<br>en sillage:<br>het verschil"),
    slides=[("La tenue", "Le temps pendant lequel le parfum reste perceptible sur ta peau : quelques heures pour une eau de cologne, toute la journée pour un extrait.",
             "Houdbaarheid", "Hoe lang het parfum op je huid te ruiken blijft: een paar uur voor een eau de cologne, de hele dag voor een extrait."),
            ("Le sillage", "La trace que tu laisses quand tu passes. Un parfum peut tenir longtemps tout en restant près de la peau.",
             "Sillage", "Het spoor dat je achterlaat wanneer je voorbijloopt. Een parfum kan lang blijven en toch dicht bij de huid blijven."),
            ("Ce qui joue", "La concentration, les notes (les bois et la vanille durent plus que les agrumes), ta peau et la température.",
             "Wat meespeelt", "De concentratie, de noten (hout en vanille blijven langer dan citrus), je huid en de temperatuur."),
            ("Sur nos fiches", "Chaque parfum Qosmi indique sa tenue et son sillage, pour choisir selon le moment.",
             "Op onze pagina's", "Bij elk parfum op Qosmi staan houdbaarheid en sillage, zodat je kiest volgens het moment.")])
pdj("adg", "jour",
    "Acqua di Giò, le grand classique marin de Giorgio Armani.\n\nCitron, pêche et note aquatique, un cœur floral avec jasmin et muguet, sur un fond de cèdre, de musc et d'ambre. "
    "Frais et lumineux, pour tous les jours.",
    "Acqua di Giò, de grote mariene klassieker van Giorgio Armani.\n\nCitroen, perzik en een waternoot, een bloemig hart met jasmijn en lelietje-van-dalen, op een basis van ceder, musk en amber. "
    "Fris en stralend, voor elke dag.")
sel("beast", "lendemain", "Beast mode : 3 parfums qui tiennent jusqu'au lendemain", "Beast mode: 3 parfums die tot de volgende dag blijven",
    "Beast mode :<br>3 parfums<br>qui tiennent", "Beast mode:<br>3 parfums<br>die blijven", ["phantom-elixir", "tero", "9pm-elixir"],
    "Tu veux un parfum que tu sens encore le lendemain ? Ces trois-là tiennent très longtemps.\n\nPhantom Elixir (lavande, oud, vanille), Tero de Nishane (caramel salé, cannelle, ambre) "
    "et 9pm Elixir (épices, cuir, vanille). Une ou deux pulvérisations suffisent. Glisse 👉",
    "Wil je een parfum dat je de volgende dag nog ruikt? Deze drie blijven heel lang.\n\nPhantom Elixir (lavendel, oud, vanille), Tero van Nishane (gezouten karamel, kaneel, amber) "
    "en 9pm Elixir (kruiden, leer, vanille). Eén of twee sprays zijn genoeg. Swipe 👉")
pdj("scandal", "soiree",
    "Scandal de Jean Paul Gaultier, ou le miel version audacieuse.\n\nOrange sanguine et mandarine, un cœur de miel, de gardénia et de fleur d'oranger, sur un fond de cire d'abeille, "
    "de caramel et de patchouli. Pour les soirées.",
    "Scandal van Jean Paul Gaultier: honing in een gedurfde versie.\n\nBloedsinaasappel en mandarijn, een hart van honing, gardenia en oranjebloesem, op een basis van bijenwas, "
    "karamel en patchouli. Voor avonden uit.")
sel("discret", "discret", "3 parfums discrets", "3 discrete parfums", "3 parfums<br>tout en<br>discrétion", "3 parfums<br>heel<br>discreet",
    ["english-pear", "mandarino", "summer-vibes"],
    "Envie d'un parfum qui reste près de toi ? English Pear & Sweet Pea (poire et pois de senteur), Mandarino di Sicilia (mandarine, petitgrain, menthe) "
    "et Light Blue Summer Vibes (bergamote, pêche, cèdre) : légers et frais. Glisse 👉",
    "Zin in een parfum dat dicht bij je blijft? English Pear & Sweet Pea (peer en lathyrus), Mandarino di Sicilia (mandarijn, petitgrain, munt) "
    "en Light Blue Summer Vibes (bergamot, perzik, ceder): licht en fris. Swipe 👉")
pdj("eros", "soiree",
    "Eros de Versace : menthe et vanille, un duo qui a fait sa réputation.\n\nMenthe, pomme verte et citron, fève tonka et géranium, sur un fond de vanille, de vétiver et de cèdre. "
    "Frais et sucré, pour sortir.",
    "Eros van Versace: munt en vanille, een duo dat zijn reputatie maakte.\n\nMunt, groene appel en citroen, tonkaboon en geranium, op een basis van vanille, vetiver en ceder. "
    "Fris en zoet, om uit te gaan.")
sel("cosy", "cosy", "3 parfums cosy pour l'hiver", "3 cosy parfums voor de winter", "3 parfums<br>cosy pour<br>l'hiver", "3 cosy<br>parfums voor<br>de winter",
    ["guilty-absolu", "sapparot", "kunafa"],
    "Plaid, chocolat chaud… et parfum gourmand. Guilty Absolu de Parfum (amande, amaretto, café), Oud Sapparot de Montale (ananas, oud, coco) "
    "et Kunafa Chocolate d'Armaf (cacao, pistache, caramel). Glisse 👉",
    "Dekentje, warme chocolade… en een gourmand parfum. Guilty Absolu de Parfum (amandel, amaretto, koffie), Oud Sapparot van Montale (ananas, oud, kokos) "
    "en Kunafa Chocolate van Armaf (cacao, pistache, karamel). Swipe 👉")
pdj("phantom", "jour",
    "Phantom de Paco Rabanne, le flacon robot.\n\nLavande et citron, pomme et notes fumées, sur un fond de vanille et de vétiver. Frais, léger, facile à porter.",
    "Phantom van Paco Rabanne, de robotflacon.\n\nLavendel en citroen, appel en rokerige noten, op een basis van vanille en vetiver. Fris, licht, makkelijk te dragen.")
pub("conseil-vaporiser", "conseil", "Où vaporiser son parfum ?", "Waar spray je je parfum?",
    "Poignets, cou, vêtements ? Quatre gestes simples pour profiter de ton parfum toute la journée. Glisse 👉",
    "Polsen, hals, kleding? Vier eenvoudige gebaren om de hele dag van je parfum te genieten. Swipe 👉",
    couv=("Où vaporiser<br>son parfum ?", "Waar spray<br>je je<br>parfum?"),
    slides=[("Les points chauds", "Cou, nuque, intérieur des poignets : la chaleur de la peau aide le parfum à se diffuser.",
             "Warme plekken", "Hals, nek, binnenkant van de polsen: de warmte van de huid helpt het parfum zich te verspreiden."),
            ("Sans frotter", "Ne frotte pas tes poignets : laisse le parfum sécher tout seul.",
             "Niet wrijven", "Wrijf je polsen niet tegen elkaar: laat het parfum vanzelf drogen."),
            ("À 15 cm", "Garde le flacon à une quinzaine de centimètres de la peau pour bien répartir le parfum.",
             "Op 15 cm", "Houd de flacon op een vijftiental centimeter van je huid om het parfum goed te verdelen."),
            ("Les cheveux", "Une pulvérisation sur la brosse, puis dans les cheveux : ton parfum te suit à chaque mouvement.",
             "Je haar", "Eén spray op je borstel, dan door je haar: je parfum volgt je bij elke beweging.")])
pdj("interdit-rouge", "soiree",
    "L'Interdit Rouge de Givenchy : la version épicée du célèbre Interdit.\n\nOrange sanguine et gingembre, jasmin et tubéreuse, sur un fond de patchouli, de santal et de vétiver. "
    "Intense et floral, pour le soir.",
    "L'Interdit Rouge van Givenchy: de kruidige versie van de bekende Interdit.\n\nBloedsinaasappel en gember, jasmijn en tuberoos, op een basis van patchouli, sandelhout en vetiver. "
    "Intens en bloemig, voor de avond.")
sel("mariage", "mariage", "3 parfums pour un mariage", "3 parfums voor een huwelijk", "3 parfums<br>pour un<br>mariage", "3 parfums<br>voor een<br>huwelijk",
    ["idole-power", "cobalt-absolute", "very-floral"],
    "Invité(e) à un mariage ? Il te faut un parfum élégant qui tienne toute la journée.\n\nIdôle Power (pomme, rose de mai, santal), Bad Boy Cobalt Absolute (lavande, géranium, vétiver) "
    "et Irresistible Very Floral (rose, iris, jasmin). Glisse 👉",
    "Uitgenodigd op een huwelijk? Dan heb je een elegant parfum nodig dat de hele dag blijft.\n\nIdôle Power (appel, meiroos, sandelhout), Bad Boy Cobalt Absolute (lavendel, geranium, vetiver) "
    "en Irresistible Very Floral (roos, iris, jasmijn). Swipe 👉")
sel("energie", "sport", "3 parfums frais et énergiques", "3 frisse, energieke parfums", "3 parfums<br>frais et<br>énergiques", "3 frisse,<br>energieke<br>parfums",
    ["everyone", "wood-sage", "atlas"],
    "Pour le sport, une balade ou les journées actives : CK Everyone (orange, thé noir, vétiver), Wood Sage & Sea Salt (sauge, sel marin, ambrette) "
    "et Atlas de Lattafa (notes marines, citron, iris). Glisse 👉",
    "Voor sport, een wandeling of actieve dagen: CK Everyone (sinaasappel, zwarte thee, vetiver), Wood Sage & Sea Salt (salie, zeezout, ambrette) "
    "en Atlas van Lattafa (mariene noten, citroen, iris). Swipe 👉")
pdj("allure-blanche", "jour",
    "Allure Homme Édition Blanche : la fraîcheur selon Chanel.\n\nCitron et bergamote, gingembre et cèdre, sur un fond de santal, de vétiver, de vanille et de muscs blancs. "
    "Net et lumineux.",
    "Allure Homme Édition Blanche: frisheid volgens Chanel.\n\nCitroen en bergamot, gember en ceder, op een basis van sandelhout, vetiver, vanille en witte musk. "
    "Strak en stralend.")
pub("conseil-jour-soir", "conseil", "Parfum de jour, parfum de soir", "Dagparfum, avondparfum",
    "Faut-il un parfum différent le soir ? Pas obligatoire, mais quelques repères aident à choisir. Glisse 👉",
    "Heb je 's avonds een ander parfum nodig? Niet verplicht, maar enkele tips helpen bij het kiezen. Swipe 👉",
    couv=("Parfum<br>de jour,<br>parfum de soir", "Dagparfum,<br>avond-<br>parfum"),
    slides=[("Le jour", "Agrumes, notes vertes, fleurs légères, musc : des parfums frais qui restent près de la peau.",
             "Overdag", "Citrus, groene noten, lichte bloemen, musk: frisse parfums die dicht bij de huid blijven."),
            ("Le soir", "Vanille, ambre, bois, épices, cuir : des notes plus chaudes, avec plus de présence.",
             "'s Avonds", "Vanille, amber, hout, kruiden, leer: warmere noten met meer aanwezigheid."),
            ("La dose", "Le jour, une ou deux pulvérisations. Le soir, tu peux en mettre un peu plus, sans exagérer.",
             "De dosis", "Overdag één of twee sprays. 's Avonds mag het iets meer, zonder te overdrijven."),
            ("Ta règle", "Le meilleur parfum, c'est celui dans lequel tu te sens bien, à toute heure.",
             "Jouw regel", "Het beste parfum is dat waarin je je goed voelt, op elk uur.")])
pdj("fb-nectar", "rdv",
    "Flowerbomb Nectar de Viktor & Rolf : la bombe florale dans sa version la plus gourmande.\n\nBergamote et cassis, jasmin sambac, fleur d'oranger et osmanthus, sur un fond de benjoin, "
    "de fève tonka et de vanille.",
    "Flowerbomb Nectar van Viktor & Rolf: de bloemenbom in haar meest gourmande versie.\n\nBergamot en zwarte bes, sambac-jasmijn, oranjebloesem en osmanthus, op een basis van benzoë, "
    "tonkaboon en vanille.")
sel("soiree", "soiree", "3 parfums pour sortir le soir", "3 parfums om 's avonds uit te gaan", "3 parfums<br>pour sortir<br>le soir", "3 parfums<br>voor een<br>avond uit",
    ["fahrenheit", "oud-greatness", "nashama"],
    "Pour les sorties, on peut oser plus fort. Fahrenheit Le Parfum (réglisse, daim, vanille), Oud for Greatness d'Initio (safran, oud, lavande) "
    "et Al Nashama de Lattafa (prune, cuir, ambre). Glisse 👉",
    "Voor een avond uit mag het wat sterker. Fahrenheit Le Parfum (zoethout, suède, vanille), Oud for Greatness van Initio (saffraan, oud, lavendel) "
    "en Al Nashama van Lattafa (pruim, leer, amber). Swipe 👉")
pdj("daisy", "printemps",
    "Daisy de Marc Jacobs, le flacon aux marguerites.\n\nFraise des bois, feuille de violette et pamplemousse, un cœur de violette, de jasmin et de gardénia, sur un fond de vanille, "
    "de muscs et de bois blancs. Frais et fruité.",
    "Daisy van Marc Jacobs, de flacon met madeliefjes.\n\nBosaardbei, violetblad en grapefruit, een hart van viooltje, jasmijn en gardenia, op een basis van vanille, "
    "musk en wit hout. Fris en fruitig.")
sel("mystere", "mystere", "3 parfums mystérieux", "3 mysterieuze parfums", "3 parfums<br>mystérieux", "3 mysterieuze<br>parfums",
    ["elle", "aoud-violet", "ombre-merveilles"],
    "Des parfums qui intriguent : Elle d'Yves Saint Laurent (baies roses, pivoine, patchouli), Aoud Violet de Mancera (violette, oud, vétiver) "
    "et L'Ombre des Merveilles d'Hermès (thé noir, encens, fève tonka). Glisse 👉",
    "Parfums die intrigeren: Elle van Yves Saint Laurent (roze peper, pioen, patchouli), Aoud Violet van Mancera (viooltje, oud, vetiver) "
    "en L'Ombre des Merveilles van Hermès (zwarte thee, wierook, tonkaboon). Swipe 👉")
pdj("bad-boy", "soiree",
    "Bad Boy de Carolina Herrera, le flacon en forme d'éclair.\n\nPoivre blanc, poivre rose et bergamote, cèdre et sauge, sur un fond de fève tonka et de cacao. Épicé et gourmand.",
    "Bad Boy van Carolina Herrera, de flacon in de vorm van een bliksemschicht.\n\nWitte peper, roze peper en bergamot, ceder en salie, op een basis van tonkaboon en cacao. Kruidig en gourmand.")
pub("conseil-genre", "conseil", "Parfum pour homme ou pour femme ?", "Parfum voor mannen of voor vrouwen?",
    "« Pour homme », « pour femme »… et si on choisissait surtout avec le nez ? Glisse 👉",
    "« Voor mannen », « voor vrouwen »… en als we vooral met onze neus kozen? Swipe 👉",
    couv=("Pour homme<br>ou pour<br>femme ?", "Voor mannen<br>of voor<br>vrouwen?"),
    slides=[("Une étiquette", "« Pour homme » ou « pour femme », c'est surtout un choix de la marque pour présenter son parfum.",
             "Een etiket", "« Voor mannen » of « voor vrouwen » is vooral een keuze van het merk om zijn parfum voor te stellen."),
            ("Les mixtes", "De nombreux parfums sont pensés pour tout le monde : on les appelle mixtes.",
             "Unisex", "Veel parfums zijn voor iedereen gemaakt: dat noemen we unisex."),
            ("Ton nez décide", "Une vanille, un bois, une fleur n'ont pas de genre. Si tu aimes, c'est pour toi.",
             "Je neus beslist", "Vanille, hout of een bloem hebben geen gender. Als je het lekker vindt, is het voor jou."),
            ("Sur Qosmi", "Tu peux filtrer par famille, par note ou par ambiance, sans te limiter à une catégorie.",
             "Op Qosmi", "Je kunt filteren op familie, noot of sfeer, zonder je tot één categorie te beperken.")])
pdj("lveb-elixir", "rdv",
    "La Vie est Belle L'Elixir de Lancôme.\n\nBergamote de Calabre, framboise et une touche de liqueur, rose et feuille de violette, sur un fond de beurre de cacao, de cèdre et de cuir. "
    "Gourmand et fruité.",
    "La Vie est Belle L'Elixir van Lancôme.\n\nCalabrische bergamot, framboos en een vleugje likeur, roos en violetblad, op een basis van cacaoboter, ceder en leer. "
    "Gourmand en fruitig.")
sel("printemps", "printemps", "3 parfums qui sentent le printemps", "3 parfums die naar de lente ruiken", "3 parfums<br>qui sentent<br>le printemps", "3 parfums<br>die naar de<br>lente ruiken",
    ["orange-blossom", "victoria", "twilly"],
    "Le printemps arrive bientôt : Orange Blossom de Jo Malone (clémentine, fleur d'oranger), Victoria de Lattafa (tarte au citron, néroli, vanille) "
    "et Twilly d'Hermès (gingembre, tubéreuse, santal). Glisse 👉",
    "De lente komt eraan: Orange Blossom van Jo Malone (clementine, oranjebloesem), Victoria van Lattafa (citroentaart, neroli, vanille) "
    "en Twilly van Hermès (gember, tuberoos, sandelhout). Swipe 👉")
pdj("pure-crystal", "hiver",
    "Pure Crystal de Lattafa : un parfum chaleureux pour les jours froids.\n\nFruits rouges, cannelle et orange amère, cognac et gingembre, sur un fond d'ambre, de vanille et de santal.",
    "Pure Crystal van Lattafa: een warm parfum voor koude dagen.\n\nRode vruchten, kaneel en bittere sinaasappel, cognac en gember, op een basis van amber, vanille en sandelhout.")
pub("conseil-saisons", "conseil", "Un parfum pour chaque saison", "Een parfum voor elk seizoen",
    "Ton parfum préféré n'a pas la même allure en janvier et en juillet. Quelques repères pour suivre les saisons. Glisse 👉",
    "Je favoriete parfum gedraagt zich anders in januari dan in juli. Enkele tips om de seizoenen te volgen. Swipe 👉",
    couv=("Un parfum<br>pour chaque<br>saison", "Een parfum<br>voor elk<br>seizoen"),
    slides=[("L'hiver", "Le froid freine le parfum : place aux notes chaudes, vanille, ambre, épices, bois.",
             "Winter", "Kou remt het parfum af: tijd voor warme noten, vanille, amber, kruiden, hout."),
            ("Le printemps", "Fleurs, notes vertes, fruits : des parfums qui s'éveillent avec la nature.",
             "Lente", "Bloemen, groene noten, fruit: parfums die ontwaken met de natuur."),
            ("L'été", "La chaleur amplifie tout : agrumes, notes marines, muscs légers, et la main légère.",
             "Zomer", "Warmte versterkt alles: citrus, mariene noten, lichte musk, en spaarzaam doseren."),
            ("L'automne", "Retour des bois, du cuir, du tabac et des fruits mûrs.",
             "Herfst", "Hout, leer, tabak en rijp fruit komen terug.")])

TAGS = (TAGS_FR, TAGS_NL)
SUR = {"pdj": ("Le bon moment", "Het juiste moment"), "sel": ("Carrousel · le bon moment", "Carrousel · het juiste moment"),
       "conseil": ("Carrousel · le conseil", "Carrousel · het advies")}
NB_SLIDES = {"pdj": lambda p: 1, "sel": lambda p: len(p["parfums"]) + 2, "conseil": lambda p: len(p["slides"]) + 2}


def construire(n0=136):
    out = []
    for i, p in enumerate(L):
        q = dict(p)
        q["n"] = n0 + i
        q["iso"], q["date"] = "2027-12-31", ""  # posées par scripts/social_planning.py
        q["sur"] = SUR[p["type"]][0]
        q["produits"] = [P[c][0] for c in p.get("parfums", [])]
        q["src"] = ["Profils Qosmi (Fragrance Index, Fragrantica)", "Visuels : photos des fiches Qosmi"]
        q["tags"], q["tags_nl"] = TAGS
        q["img"] = ["%s-%d" % (q["id"], k + 1) for k in range(NB_SLIDES[p["type"]](p))]
        out.append(q)
    return out


if __name__ == "__main__":
    lot = construire()
    chemin = os.path.join(ICI, "lot6", "lot6.json")
    ancien = {}
    if os.path.exists(chemin):  # garder les dates déjà posées par le planning
        ancien = {p["id"]: p for p in json.load(open(chemin, encoding="utf-8"))}
    for q in lot:
        if q["id"] in ancien:
            for k in ("iso", "date", "heure"):
                if k in ancien[q["id"]]:
                    q[k] = ancien[q["id"]][k]
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    json.dump(lot, open(chemin, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%d publications, %d visuels" % (len(lot), sum(len(q["img"]) for q in lot)))
