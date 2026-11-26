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
