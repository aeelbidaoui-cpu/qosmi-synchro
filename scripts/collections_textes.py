# 26/11/2026 (#131) : texte long de la page « Parfums de niche » (cible : « parfum de niche Belgique »), FR / NL / EN.
# Faits repris des pages marques déjà vérifiées (Xerjoff, Parfums de Marly, MFK, Kilian, Initio, Le Labo).
MARQUES_NICHE = [("xerjoff", "Xerjoff"), ("nishane", "Nishane"), ("creed", "Creed"), ("montale", "Montale"), ("mancera", "Mancera"),
                 ("tiziana-terenzi", "Tiziana Terenzi"), ("sospiro", "Sospiro"), ("frederic-malle", "Frederic Malle"), ("le-labo", "Le Labo")]


def _l(p, h, t):
    return '<a href="%s/collections/%s">%s</a>' % (p, h, t)


def _autres(p, et):
    m = [_l(p, h, t) for h, t in MARQUES_NICHE[1:]]
    return ", ".join(m[:-1]) + " " + et + " " + m[-1]


def suite_niche(langue):
    p = {"fr": "", "nl": "/nl", "en": "/en"}[langue]
    if langue == "fr":
        return ('<div class="qk-suite">\n'
                "<h2>Qu'est-ce qu'un parfum de niche ?</h2>\n"
                "<p>Un parfum de niche vient d'une maison dont le parfum est le métier principal, et non d'une marque de mode ou de cosmétique. "
                "Ces maisons diffusent leurs créations de façon plus sélective et se donnent souvent plus de liberté : accords inattendus, "
                "matières mises en avant, concentrations élevées comme l'extrait de parfum. Le résultat est souvent plus personnel et moins répandu "
                "que les grands succès de parfumerie.</p>\n"
                "<h2>Les maisons de niche chez Qosmi</h2>\n"
                "<p>%s, fondée à Turin par Sergio Momo, soigne autant ses matières que ses flacons. %s, fondée en 2009 par Julien Sprecher, "
                "s'inspire de la cour de Louis XV. %s est née à Paris en 2009, %s en 2007 et %s en 2015. Tu trouveras aussi %s.</p>\n"
                "<h2>Comment choisir un parfum de niche</h2>\n"
                "<p>Pars des odeurs que tu aimes déjà. Chaque fiche détaille la pyramide olfactive, la famille, les saisons, les occasions, "
                'la tenue et le sillage. La <a href="/pages/odeurs">recherche par odeurs</a> et le <a href="/pages/quiz">quiz « Trouve ton parfum »</a> '
                "t'aident à repérer des parfums proches de tes préférés. Pour payer moins cher le même jus, regarde le format testeur quand il existe : "
                "même parfum, avec son bouchon, dans un emballage plus simple.</p>\n"
                "<h2>Authentiques, au juste prix</h2>\n"
                "<p>Tous nos parfums de niche sont des originaux neufs, achetés auprès de distributeurs établis dans l'Union européenne, avec facture "
                '(voir <a href="/pages/authenticite">notre page Authenticité</a>). Nos prix sont justes toute l\'année, sans fausses promotions, '
                "et la livraison en point relais est offerte dès 2 articles en Belgique, aux Pays-Bas et au Luxembourg.</p>\n</div>"
                % (_l(p, "xerjoff", "Xerjoff"), _l(p, "parfums-de-marly", "Parfums de Marly"), _l(p, "maison-francis-kurkdjian", "Maison Francis Kurkdjian"),
                   _l(p, "by-kilian", "Kilian"), _l(p, "initio", "Initio"), _autres(p, "ou")))
    if langue == "nl":
        return ('<div class="qk-suite">\n'
                "<h2>Wat is een nicheparfum?</h2>\n"
                "<p>Een nicheparfum komt van een huis waarvoor parfum het hoofdvak is, en niet van een mode- of cosmeticamerk. "
                "Die huizen verdelen hun creaties selectiever en nemen vaak meer vrijheid: verrassende akkoorden, uitgesproken grondstoffen, "
                "hoge concentraties zoals extrait de parfum. Het resultaat is vaak persoonlijker en minder alomtegenwoordig dan de grote parfumsuccessen.</p>\n"
                "<h2>De nichehuizen bij Qosmi</h2>\n"
                "<p>%s, in Turijn opgericht door Sergio Momo, verzorgt zijn grondstoffen even goed als zijn flessen. %s, in 2009 opgericht door "
                "Julien Sprecher, haalt zijn inspiratie uit het hof van Lodewijk XV. %s ontstond in 2009 in Parijs, %s in 2007 en %s in 2015. "
                "Je vindt er ook %s.</p>\n"
                "<h2>Hoe kies je een nicheparfum?</h2>\n"
                "<p>Vertrek van de geuren die je al lekker vindt. Elke productpagina toont de geurpiramide, de familie, de seizoenen, de gelegenheden, "
                'de houdbaarheid en de sillage. Met <a href="/nl/pages/odeurs">zoeken op geur</a> en de <a href="/nl/pages/quiz">quiz</a> '
                "vind je parfums die op je favorieten lijken. Wil je minder betalen voor hetzelfde sap? Kijk dan naar de tester, als die bestaat: "
                "hetzelfde parfum, met dop, in een eenvoudigere verpakking.</p>\n"
                "<h2>Origineel, aan een eerlijke prijs</h2>\n"
                "<p>Al onze nicheparfums zijn nieuwe originelen, aangekocht bij gevestigde verdelers in de Europese Unie, met factuur "
                '(zie <a href="/nl/pages/authenticite">onze pagina over echtheid</a>). Onze prijzen zijn het hele jaar eerlijk, zonder nepkortingen, '
                "en levering in een afhaalpunt is gratis vanaf 2 artikelen in België, Nederland en Luxemburg.</p>\n</div>"
                % (_l(p, "xerjoff", "Xerjoff"), _l(p, "parfums-de-marly", "Parfums de Marly"), _l(p, "maison-francis-kurkdjian", "Maison Francis Kurkdjian"),
                   _l(p, "by-kilian", "Kilian"), _l(p, "initio", "Initio"), _autres(p, "of")))
    return ('<div class="qk-suite">\n'
            "<h2>What is a niche fragrance?</h2>\n"
            "<p>A niche fragrance comes from a house whose main craft is perfume, rather than from a fashion or cosmetics brand. "
            "These houses distribute their creations more selectively and often allow themselves more freedom: unexpected accords, "
            "standout raw materials, high concentrations such as extrait de parfum. The result is often more personal and less common "
            "than the big perfume bestsellers.</p>\n"
            "<h2>The niche houses at Qosmi</h2>\n"
            "<p>%s, founded in Turin by Sergio Momo, cares as much about its materials as its bottles. %s, founded in 2009 by Julien Sprecher, "
            "draws on the court of Louis XV. %s was born in Paris in 2009, %s in 2007 and %s in 2015. You will also find %s.</p>\n"
            "<h2>How to choose a niche fragrance</h2>\n"
            "<p>Start from the scents you already like. Every product page details the olfactory pyramid, the family, the seasons, the occasions, "
            'the longevity and the sillage. <a href="/en/pages/odeurs">Search by scent</a> and the <a href="/en/pages/quiz">quiz</a> '
            "help you spot fragrances close to your favourites. To pay less for the same juice, look at the tester when there is one: "
            "the same fragrance, with its cap, in simpler packaging.</p>\n"
            "<h2>Genuine, at a fair price</h2>\n"
            "<p>All our niche fragrances are brand-new originals, bought from established distributors in the European Union, with an invoice "
            '(see <a href="/en/pages/authenticite">our Authenticity page</a>). Our prices are fair all year round, with no fake discounts, '
            "and pick-up point delivery is free from 2 items in Belgium, the Netherlands and Luxembourg.</p>\n</div>"
            % (_l(p, "xerjoff", "Xerjoff"), _l(p, "parfums-de-marly", "Parfums de Marly"), _l(p, "maison-francis-kurkdjian", "Maison Francis Kurkdjian"),
               _l(p, "by-kilian", "Kilian"), _l(p, "initio", "Initio"), _autres(p, "and")))


# ---------------------------------------------------------------------------------------------------------------------
# 26/11/2026 (#131, suite) : textes longs des pages Parfums arabes, Testeurs, Femme, Homme, Mixtes (FR / NL / EN).
# Liens : [[handle|Texte]] → collection de la marque ; [[/pages/x|Texte]] → page. Faits repris des pages marques vérifiées.
import re as _re

_FIN = {
    "fr": ("Authentiques, au juste prix",
           "Tous nos parfums sont des originaux neufs, achetés auprès de distributeurs établis dans l'Union européenne, avec facture "
           "(voir [[/pages/authenticite|notre page Authenticité]]). Nos prix sont justes toute l'année, sans fausses promotions, "
           "et la livraison en point relais est offerte dès 2 articles en Belgique, aux Pays-Bas et au Luxembourg."),
    "nl": ("Origineel, aan een eerlijke prijs",
           "Al onze parfums zijn nieuwe originelen, aangekocht bij gevestigde verdelers in de Europese Unie, met factuur "
           "(zie [[/pages/authenticite|onze pagina over echtheid]]). Onze prijzen zijn het hele jaar eerlijk, zonder nepkortingen, "
           "en levering in een afhaalpunt is gratis vanaf 2 artikelen in België, Nederland en Luxemburg."),
    "en": ("Genuine, at a fair price",
           "All our fragrances are brand-new originals, bought from established distributors in the European Union, with an invoice "
           "(see [[/pages/authenticite|our Authenticity page]]). Our prices are fair all year round, with no fake discounts, "
           "and pick-up point delivery is free from 2 items in Belgium, the Netherlands and Luxembourg."),
}

TEXTES = {
    "parfums-arabes": {
        "fr": [
            ("Qu'est-ce qu'un parfum arabe ?",
             "On appelle parfums arabes, ou parfums orientaux, les créations des maisons du Golfe, des Émirats arabes unis à l'Arabie saoudite. "
             "Elles s'appuient sur une longue tradition où le oud, l'ambre, la rose, le musc, le safran et l'encens tiennent une place centrale. "
             "Leurs parfums sont souvent concentrés et généreux, avec une bonne tenue et un sillage présent."),
            ("Les maisons chez Qosmi",
             "[[lattafa|Lattafa]], maison des Émirats arabes unis, est devenue en quelques années l'une des marques de parfumerie orientale "
             "les plus connues au monde. [[armaf|Armaf]], du groupe Sterling Parfums, propose des parfums modernes et puissants. "
             "[[al-haramain|Al Haramain]] est née en 1970 à La Mecque et est aujourd'hui basée aux Émirats. Tu trouveras aussi "
             "[[afnan|Afnan]], [[rasasi|Rasasi]], [[ajmal|Ajmal]], [[french-avenue|French Avenue]], [[maison-alhambra|Maison Alhambra]], "
             "[[khadlaj|Khadlaj]] ou [[swiss-arabian|Swiss Arabian]]."),
            ("Comment choisir un parfum arabe",
             "Les familles les plus recherchées sont l'ambré vanillé, le oud boisé, le gourmand (café, caramel, praliné) et le floral rosé. "
             "Pars d'une famille que tu aimes déjà : chaque fiche détaille la pyramide olfactive, la tenue et le sillage, et la "
             "[[/pages/odeurs|recherche par odeurs]] t'aide à comparer. Ces parfums sont souvent intenses : une ou deux pulvérisations suffisent."),
        ],
        "nl": [
            ("Wat is een Arabisch parfum?",
             "Arabische of oosterse parfums zijn de creaties van huizen uit de Golfregio, van de Verenigde Arabische Emiraten tot Saoedi-Arabië. "
             "Ze steunen op een lange traditie waarin oud, amber, roos, musk, saffraan en wierook centraal staan. "
             "Hun parfums zijn vaak geconcentreerd en royaal, met een goede houdbaarheid en een duidelijke sillage."),
            ("De huizen bij Qosmi",
             "[[lattafa|Lattafa]], een huis uit de Verenigde Arabische Emiraten, werd in enkele jaren een van de bekendste oosterse "
             "parfummerken ter wereld. [[armaf|Armaf]], van de groep Sterling Parfums, brengt moderne en krachtige parfums. "
             "[[al-haramain|Al Haramain]] ontstond in 1970 in Mekka en is vandaag gevestigd in de Emiraten. Je vindt er ook "
             "[[afnan|Afnan]], [[rasasi|Rasasi]], [[ajmal|Ajmal]], [[french-avenue|French Avenue]], [[maison-alhambra|Maison Alhambra]], "
             "[[khadlaj|Khadlaj]] of [[swiss-arabian|Swiss Arabian]]."),
            ("Hoe kies je een Arabisch parfum?",
             "De meest gezochte families zijn amber-vanille, houtige oud, gourmand (koffie, karamel, praline) en bloemig met roos. "
             "Vertrek van een familie die je al lekker vindt: elke productpagina toont de geurpiramide, de houdbaarheid en de sillage, en met "
             "[[/pages/odeurs|zoeken op geur]] vergelijk je makkelijk. Deze parfums zijn vaak intens: een of twee verstuivingen volstaan."),
        ],
        "en": [
            ("What is an Arabian fragrance?",
             "Arabian, or oriental, fragrances are the creations of houses from the Gulf, from the United Arab Emirates to Saudi Arabia. "
             "They draw on a long tradition in which oud, amber, rose, musk, saffron and incense play a central role. "
             "Their fragrances are often concentrated and generous, with good longevity and a noticeable sillage."),
            ("The houses at Qosmi",
             "[[lattafa|Lattafa]], a house from the United Arab Emirates, has become in just a few years one of the best-known oriental "
             "perfume brands in the world. [[armaf|Armaf]], part of the Sterling Parfums group, offers modern, powerful fragrances. "
             "[[al-haramain|Al Haramain]] was founded in 1970 in Mecca and is now based in the Emirates. You will also find "
             "[[afnan|Afnan]], [[rasasi|Rasasi]], [[ajmal|Ajmal]], [[french-avenue|French Avenue]], [[maison-alhambra|Maison Alhambra]], "
             "[[khadlaj|Khadlaj]] and [[swiss-arabian|Swiss Arabian]]."),
            ("How to choose an Arabian fragrance",
             "The most sought-after families are vanilla amber, woody oud, gourmand (coffee, caramel, praline) and rosy florals. "
             "Start from a family you already like: every product page details the olfactory pyramid, longevity and sillage, and "
             "[[/pages/odeurs|search by scent]] helps you compare. These fragrances are often intense: one or two sprays are enough."),
        ],
    },
    "testeurs": {
        "fr": [
            ("C'est quoi un testeur ?",
             "Un testeur, c'est le même parfum que la version vendue en boîte, dans la même contenance : un flacon original et neuf que les "
             "marques fournissent aux parfumeries. Il arrive avec son bouchon, sans boîte décorée (parfois dans une boîte blanche toute simple). "
             "Le parfum et la quantité sont identiques ; seul l'emballage change."),
            ("Pourquoi c'est moins cher ?",
             "Sans boîte décorée ni présentation de vitrine, le testeur revient moins cher. Tu paies le parfum, pas l'emballage. "
             "C'est un bon choix pour toi-même ; pour offrir, la version en boîte reste plus présentable."),
            ("Acheter un testeur chez Qosmi",
             "Sur chaque fiche, le testeur est un format au choix, à côté des versions en boîte (par exemple « 100 ml » ou « 100 ml testeur »). "
             "Il est toujours indiqué comme tel avant l'achat. Tu peux comparer les prix des formats d'un coup d'œil, et la "
             "[[/pages/odeurs|recherche par odeurs]] t'aide à trouver un parfum qui te ressemble."),
        ],
        "nl": [
            ("Wat is een tester?",
             "Een tester is hetzelfde parfum als de versie in doos, in dezelfde inhoud: een origineel, nieuw flesje dat merken aan "
             "parfumerieën geven. Het komt met zijn dop, zonder sierdoos (soms in een eenvoudige witte doos). "
             "Het parfum en de hoeveelheid zijn identiek; alleen de verpakking verschilt."),
            ("Waarom is het goedkoper?",
             "Zonder sierdoos of etalagepresentatie is een tester goedkoper. Je betaalt voor het parfum, niet voor de verpakking. "
             "Een goede keuze voor jezelf; om cadeau te geven blijft de versie in doos mooier."),
            ("Een tester kopen bij Qosmi",
             "Op elke productpagina is de tester een formaat naar keuze, naast de versies in doos (bijvoorbeeld „100 ml” of „100 ml tester”). "
             "Hij staat altijd als tester vermeld vóór je koopt. Je vergelijkt de prijzen van de formaten in één oogopslag, en met "
             "[[/pages/odeurs|zoeken op geur]] vind je een parfum dat bij je past."),
        ],
        "en": [
            ("What is a tester?",
             "A tester is the same fragrance as the boxed version, in the same size: an original, brand-new bottle that brands supply to "
             "perfumeries. It comes with its cap, without a decorated box (sometimes in a plain white box). "
             "The fragrance and the quantity are identical; only the packaging changes."),
            ("Why is it cheaper?",
             "Without a decorated box or shop-window presentation, a tester costs less. You pay for the fragrance, not the packaging. "
             "A good choice for yourself; as a gift, the boxed version looks nicer."),
            ("Buying a tester at Qosmi",
             "On every product page, the tester is one of the sizes to choose from, next to the boxed versions (for example “100 ml” or "
             "“100 ml tester”). It is always labelled as such before you buy. You can compare the prices of each size at a glance, and "
             "[[/pages/odeurs|search by scent]] helps you find a fragrance that suits you."),
        ],
    },
    "parfums-femme": {
        "fr": [
            ("Choisir un parfum pour femme",
             "Un parfum se choisit d'abord par famille olfactive : floral (rose, jasmin, fleur d'oranger), fruité, gourmand (vanille, praliné), "
             "boisé ou ambré. Les familles se mélangent souvent : un floral peut être poudré, un gourmand peut cacher un cœur de fleurs blanches. "
             "Chaque fiche détaille la pyramide, la famille, les saisons, les occasions, la tenue et le sillage."),
            ("Les grandes maisons",
             "[[chanel|Chanel]] lance N°5 en 1921, composé par Ernest Beaux. [[dior|Dior]] présente Miss Dior en 1947, l'année du premier "
             "défilé de Christian Dior. [[guerlain|Guerlain]], fondée à Paris en 1828, est à l'origine de Shalimar (1925). Tu trouveras aussi "
             "[[yves-saint-laurent|Yves Saint Laurent]], [[lancome|Lancôme]], [[carolina-herrera|Carolina Herrera]], [[givenchy|Givenchy]], "
             "[[paco-rabanne|Rabanne]] et [[narciso-rodriguez|Narciso Rodriguez]]."),
            ("Envie d'un parfum moins répandu ?",
             "Regarde aussi nos [[niche|parfums de niche]] (Xerjoff, Parfums de Marly, Kilian…) et nos [[parfums-arabes|parfums arabes]], "
             "souvent gourmands et ambrés. Le [[/pages/quiz|quiz « Trouve ton parfum »]] te guide en quelques questions."),
            ("Eau de parfum ou eau de toilette ?",
             "L'eau de parfum est plus concentrée que l'eau de toilette et tient en général plus longtemps. L'eau de toilette est plus légère, "
             "agréable en journée et aux beaux jours. Quand il existe, le format testeur te permet de payer moins cher le même parfum."),
        ],
        "nl": [
            ("Een damesparfum kiezen",
             "Een parfum kies je eerst op geurfamilie: bloemig (roos, jasmijn, oranjebloesem), fruitig, gourmand (vanille, praline), "
             "houtig of amberachtig. Families lopen vaak in elkaar over: een bloemige geur kan poederig zijn, een gourmand kan een hart van "
             "witte bloemen hebben. Elke productpagina toont de piramide, de familie, de seizoenen, de gelegenheden, de houdbaarheid en de sillage."),
            ("De grote huizen",
             "[[chanel|Chanel]] lanceerde N°5 in 1921, gecomponeerd door Ernest Beaux. [[dior|Dior]] stelde Miss Dior voor in 1947, het jaar "
             "van de eerste modeshow van Christian Dior. [[guerlain|Guerlain]], in 1828 in Parijs opgericht, creëerde Shalimar (1925). "
             "Je vindt er ook [[yves-saint-laurent|Yves Saint Laurent]], [[lancome|Lancôme]], [[carolina-herrera|Carolina Herrera]], "
             "[[givenchy|Givenchy]], [[paco-rabanne|Rabanne]] en [[narciso-rodriguez|Narciso Rodriguez]]."),
            ("Zin in een minder alledaags parfum?",
             "Bekijk ook onze [[niche|nicheparfums]] (Xerjoff, Parfums de Marly, Kilian…) en onze [[parfums-arabes|Arabische parfums]], "
             "vaak gourmand en amberachtig. De [[/pages/quiz|quiz]] helpt je in enkele vragen op weg."),
            ("Eau de parfum of eau de toilette?",
             "Eau de parfum is geconcentreerder dan eau de toilette en blijft meestal langer hangen. Eau de toilette is lichter, aangenaam "
             "overdag en bij mooi weer. Bestaat er een tester, dan betaal je minder voor hetzelfde parfum."),
        ],
        "en": [
            ("Choosing a women's fragrance",
             "A fragrance is chosen first by olfactory family: floral (rose, jasmine, orange blossom), fruity, gourmand (vanilla, praline), "
             "woody or amber. Families often blend: a floral can be powdery, a gourmand can hide a heart of white flowers. "
             "Every product page details the pyramid, the family, the seasons, the occasions, the longevity and the sillage."),
            ("The great houses",
             "[[chanel|Chanel]] launched N°5 in 1921, composed by Ernest Beaux. [[dior|Dior]] presented Miss Dior in 1947, the year of "
             "Christian Dior's first show. [[guerlain|Guerlain]], founded in Paris in 1828, created Shalimar (1925). You will also find "
             "[[yves-saint-laurent|Yves Saint Laurent]], [[lancome|Lancôme]], [[carolina-herrera|Carolina Herrera]], [[givenchy|Givenchy]], "
             "[[paco-rabanne|Rabanne]] and [[narciso-rodriguez|Narciso Rodriguez]]."),
            ("Looking for something less common?",
             "Have a look at our [[niche|niche fragrances]] (Xerjoff, Parfums de Marly, Kilian…) and our [[parfums-arabes|Arabian fragrances]], "
             "often gourmand and amber. The [[/pages/quiz|quiz]] guides you in a few questions."),
            ("Eau de parfum or eau de toilette?",
             "Eau de parfum is more concentrated than eau de toilette and usually lasts longer. Eau de toilette is lighter, pleasant during "
             "the day and in warm weather. When there is one, the tester lets you pay less for the same fragrance."),
        ],
    },
    "parfums-homme": {
        "fr": [
            ("Choisir un parfum pour homme",
             "Les grandes familles sont le frais aromatique (bergamote, lavande, menthe), le boisé (cèdre, vétiver, santal), l'ambré épicé "
             "(ambre, vanille, cardamome), le cuir et l'aquatique. Chaque fiche détaille la pyramide, la famille, la tenue et le sillage, "
             "pour savoir à quoi t'attendre avant d'acheter."),
            ("Les maisons chez Qosmi",
             "Côté grands classiques : [[dior|Dior]], [[chanel|Chanel]], [[yves-saint-laurent|Yves Saint Laurent]], [[hugo-boss|Hugo Boss]], "
             "[[versace|Versace]], [[paco-rabanne|Rabanne]], [[jean-paul-gaultier|Jean Paul Gaultier]] ou [[giorgio-armani|Giorgio Armani]]. "
             "[[tom-ford|Tom Ford]] a lancé sa ligne beauté avec Estée Lauder ; Black Orchid (2006) en est la pierre angulaire. "
             "Côté niche : [[creed|Creed]], [[parfums-de-marly|Parfums de Marly]] et [[xerjoff|Xerjoff]]. Et pour un sillage généreux, "
             "les [[parfums-arabes|parfums arabes]] de Lattafa, Armaf ou Al Haramain."),
            ("Quel parfum pour quelle occasion ?",
             "Un parfum frais ou aromatique convient bien au bureau et aux beaux jours. Les boisés et les ambrés prennent toute leur place "
             "le soir et en hiver. Chaque fiche indique les saisons et les occasions conseillées, et le "
             "[[/pages/quiz|quiz « Trouve ton parfum »]] t'aide à affiner."),
            ("Concentration et testeur",
             "L'eau de parfum est plus concentrée que l'eau de toilette et tient en général plus longtemps. Quand il existe, le format "
             "testeur te permet de payer moins cher le même parfum, avec son bouchon, dans un emballage plus simple."),
        ],
        "nl": [
            ("Een herenparfum kiezen",
             "De grote families zijn fris aromatisch (bergamot, lavendel, munt), houtig (ceder, vetiver, sandelhout), amberachtig en kruidig "
             "(amber, vanille, kardemom), leder en aquatisch. Elke productpagina toont de piramide, de familie, de houdbaarheid en de sillage, "
             "zodat je weet wat je mag verwachten."),
            ("De huizen bij Qosmi",
             "Grote klassiekers: [[dior|Dior]], [[chanel|Chanel]], [[yves-saint-laurent|Yves Saint Laurent]], [[hugo-boss|Hugo Boss]], "
             "[[versace|Versace]], [[paco-rabanne|Rabanne]], [[jean-paul-gaultier|Jean Paul Gaultier]] of [[giorgio-armani|Giorgio Armani]]. "
             "[[tom-ford|Tom Ford]] lanceerde zijn beautylijn met Estée Lauder; Black Orchid (2006) is er de hoeksteen van. "
             "Niche: [[creed|Creed]], [[parfums-de-marly|Parfums de Marly]] en [[xerjoff|Xerjoff]]. En voor een royale sillage: de "
             "[[parfums-arabes|Arabische parfums]] van Lattafa, Armaf of Al Haramain."),
            ("Welk parfum voor welke gelegenheid?",
             "Een fris of aromatisch parfum past goed op kantoor en bij mooi weer. Houtige en amberachtige geuren komen 's avonds en in de "
             "winter het best tot hun recht. Elke productpagina vermeldt de aanbevolen seizoenen en gelegenheden, en de "
             "[[/pages/quiz|quiz]] helpt je verder."),
            ("Concentratie en tester",
             "Eau de parfum is geconcentreerder dan eau de toilette en blijft meestal langer hangen. Bestaat er een tester, dan betaal je "
             "minder voor hetzelfde parfum, met dop, in een eenvoudigere verpakking."),
        ],
        "en": [
            ("Choosing a men's fragrance",
             "The main families are fresh aromatic (bergamot, lavender, mint), woody (cedar, vetiver, sandalwood), spicy amber "
             "(amber, vanilla, cardamom), leather and aquatic. Every product page details the pyramid, the family, the longevity and the "
             "sillage, so you know what to expect before you buy."),
            ("The houses at Qosmi",
             "The great classics: [[dior|Dior]], [[chanel|Chanel]], [[yves-saint-laurent|Yves Saint Laurent]], [[hugo-boss|Hugo Boss]], "
             "[[versace|Versace]], [[paco-rabanne|Rabanne]], [[jean-paul-gaultier|Jean Paul Gaultier]] and [[giorgio-armani|Giorgio Armani]]. "
             "[[tom-ford|Tom Ford]] launched his beauty line with Estée Lauder; Black Orchid (2006) is its cornerstone. "
             "Niche: [[creed|Creed]], [[parfums-de-marly|Parfums de Marly]] and [[xerjoff|Xerjoff]]. And for a generous sillage, the "
             "[[parfums-arabes|Arabian fragrances]] of Lattafa, Armaf or Al Haramain."),
            ("Which fragrance for which occasion?",
             "A fresh or aromatic fragrance works well at the office and in warm weather. Woody and amber scents come into their own in "
             "the evening and in winter. Every product page lists the recommended seasons and occasions, and the "
             "[[/pages/quiz|quiz]] helps you narrow it down."),
            ("Concentration and testers",
             "Eau de parfum is more concentrated than eau de toilette and usually lasts longer. When there is one, the tester lets you pay "
             "less for the same fragrance, with its cap, in simpler packaging."),
        ],
    },
    "parfums-mixtes": {
        "fr": [
            ("C'est quoi un parfum mixte ?",
             "Un parfum mixte, ou unisexe, n'est pas pensé pour un genre en particulier. On y trouve des colognes fraîches, des boisés, "
             "des ambrés, des cuirs ou des ouds. Beaucoup de maisons de niche ne font d'ailleurs plus de distinction : c'est la peau "
             "et l'envie qui décident."),
            ("Les maisons chez Qosmi",
             "[[jo-malone|Jo Malone London]], née à Londres en 1990, s'est fait connaître avec des Colognes lumineuses et l'idée de superposer "
             "deux parfums. [[maison-francis-kurkdjian|Maison Francis Kurkdjian]] est née à Paris en 2009 et [[initio|Initio]] en 2015. "
             "Tu trouveras aussi [[acqua-di-parma|Acqua di Parma]], [[xerjoff|Xerjoff]], [[montale|Montale]], [[mancera|Mancera]], "
             "[[by-kilian|Kilian]] et de nombreux [[parfums-arabes|parfums arabes]]."),
            ("Comment choisir un parfum mixte",
             "Pars des odeurs que tu aimes : agrumes, bois, vanille, cuir, encens… La [[/pages/odeurs|recherche par odeurs]] et le "
             "[[/pages/quiz|quiz « Trouve ton parfum »]] te proposent des parfums proches de tes préférés, et chaque fiche détaille la pyramide, "
             "les saisons, la tenue et le sillage."),
        ],
        "nl": [
            ("Wat is een unisex parfum?",
             "Een unisex parfum is niet bedoeld voor één bepaald geslacht. Je vindt er frisse colognes, houtige en amberachtige geuren, "
             "leder of oud. Veel nichehuizen maken trouwens geen onderscheid meer: je huid en je zin beslissen."),
            ("De huizen bij Qosmi",
             "[[jo-malone|Jo Malone London]], in 1990 in Londen opgericht, werd bekend met stralende Colognes en het idee om twee parfums te "
             "combineren. [[maison-francis-kurkdjian|Maison Francis Kurkdjian]] ontstond in 2009 in Parijs en [[initio|Initio]] in 2015. "
             "Je vindt er ook [[acqua-di-parma|Acqua di Parma]], [[xerjoff|Xerjoff]], [[montale|Montale]], [[mancera|Mancera]], "
             "[[by-kilian|Kilian]] en heel wat [[parfums-arabes|Arabische parfums]]."),
            ("Hoe kies je een unisex parfum?",
             "Vertrek van de geuren die je lekker vindt: citrus, hout, vanille, leder, wierook… Met [[/pages/odeurs|zoeken op geur]] en de "
             "[[/pages/quiz|quiz]] vind je parfums die op je favorieten lijken, en elke productpagina toont de piramide, de seizoenen, "
             "de houdbaarheid en de sillage."),
        ],
        "en": [
            ("What is a unisex fragrance?",
             "A unisex fragrance is not designed for any particular gender. It covers fresh colognes, woody and amber scents, leather "
             "or oud. Many niche houses no longer make the distinction at all: your skin and your mood decide."),
            ("The houses at Qosmi",
             "[[jo-malone|Jo Malone London]], founded in London in 1990, became known for its bright Colognes and the idea of layering two "
             "fragrances. [[maison-francis-kurkdjian|Maison Francis Kurkdjian]] was born in Paris in 2009 and [[initio|Initio]] in 2015. "
             "You will also find [[acqua-di-parma|Acqua di Parma]], [[xerjoff|Xerjoff]], [[montale|Montale]], [[mancera|Mancera]], "
             "[[by-kilian|Kilian]] and many [[parfums-arabes|Arabian fragrances]]."),
            ("How to choose a unisex fragrance",
             "Start from the scents you like: citrus, woods, vanilla, leather, incense… [[/pages/odeurs|Search by scent]] and the "
             "[[/pages/quiz|quiz]] suggest fragrances close to your favourites, and every product page details the pyramid, the seasons, "
             "the longevity and the sillage."),
        ],
    },
}


def _liens(t, p):
    def r(m):
        cible, texte = m.group(1), m.group(2)
        url = p + (cible if cible.startswith("/") else "/collections/" + cible)
        return '<a href="%s">%s</a>' % (url, texte)
    return _re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r, t)


def suite(handle, langue):
    """Texte long (qk-suite) d'une collection, ou "" si aucun."""
    if handle == "niche":
        return suite_niche(langue)
    if handle not in TEXTES:
        return ""
    p = {"fr": "", "nl": "/nl", "en": "/en"}[langue]
    parties = TEXTES[handle][langue] + [_FIN[langue]]
    return '<div class="qk-suite">\n' + "\n".join("<h2>%s</h2>\n<p>%s</p>" % (h, _liens(c, p)) for h, c in parties) + "\n</div>"
