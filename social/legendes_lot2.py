"""Lot n°2 Qosmi : calendrier et légendes FR + NL des 30 publications (16/12/2026 → 14/01/2027).
Faits repris d'Olfastory (autorisation d'Amine). Légende publiée = FR, puis NL, puis hashtags."""
import json, os, datetime as dt

O = "https://www.olfastory.com"
ICI = os.path.dirname(os.path.abspath(__file__))
L = []  # (id, type, titre, sources, produits (clés), FR, NL, hashtags)


def add(pid, typ, titre, src, prods, fr, nl, tags):
    L.append((pid, typ, titre, src, prods, fr.strip(), nl.strip(), tags))


add("01-sel-lui", "Spécial Noël · la sélection", "3 cadeaux de dernière minute pour lui",
    [("Spicebomb", "/parfum/spicebomb"), ("Gentleman Eau de Parfum", "/parfum/gentleman-eau-de-parfum"), ("Boss Bottled Eau de Parfum", "/parfum/boss-bottled-eau-de-parfum")],
    ["spicebomb", "gentleman", "bossedp"], """
Tu n'as toujours rien trouvé pour lui ? On t'aide :

1. Viktor&Rolf Spicebomb : pamplemousse, safran, piment et cannelle, dans un flacon en forme de grenade. Pour celui qui aime qu'on le remarque.

2. Givenchy Gentleman Eau de Parfum : poivre noir, iris, patchouli et vanille. L'élégance d'un costume bien coupé.

3. Hugo Boss Boss Bottled Eau de Parfum : la version eau de parfum, sortie en 2020, d'un classique né en 1998. Pomme, cannelle, vétiver.

Lequel pour lui ? Dis-nous 1, 2 ou 3 en commentaire.
Les trois sont sur qosmi.be""", """
Nog niets gevonden voor hem? We helpen je:

1. Viktor&Rolf Spicebomb: grapefruit, saffraan, chili en kaneel, in een flacon in de vorm van een granaat. Voor wie graag opvalt.

2. Givenchy Gentleman Eau de Parfum: zwarte peper, iris, patchoeli en vanille. De elegantie van een goed gesneden pak.

3. Hugo Boss Boss Bottled Eau de Parfum: de eau de parfum-versie (2020) van een klassieker uit 1998. Appel, kaneel, vetiver.

Welke kies jij voor hem? Zeg 1, 2 of 3 in de reacties.
Alle drie op qosmi.be""", "#cadeaunoel #parfumhomme #spicebomb #givenchy #bossbottled #qosmi")

add("02-conseil-hiver", "Carrousel · le conseil", "Ton parfum en hiver : 4 conseils", [], [], """
Le froid change la façon dont ton parfum se comporte. 4 conseils pour l'hiver :

1. Mise sur les notes chaudes : vanille, ambre, épices et bois tiennent mieux quand il fait froid
2. Hydrate ta peau avec une crème sans parfum : une peau sèche retient moins le parfum
3. Ne laisse pas ton flacon dans une voiture glacée : les écarts de température l'abîment
4. À l'intérieur, dans une pièce chauffée, deux pulvérisations suffisent

Et toi, c'est quoi ton parfum d'hiver ?""", """
Kou verandert hoe je parfum zich gedraagt. 4 tips voor de winter:

1. Kies warme noten: vanille, amber, specerijen en hout houden beter stand in de kou
2. Hydrateer je huid met een ongeparfumeerde crème: een droge huid houdt parfum minder goed vast
3. Laat je flacon niet achter in een ijskoude auto: grote temperatuurverschillen beschadigen het parfum
4. Binnen, in een verwarmde ruimte, zijn twee verstuivingen genoeg

En jij, wat is jouw winterparfum?""", "#conseilparfum #parfumhiver #astuceparfum #qosmi")

add("03-pdj-prn", "Le parfum du jour", "La Petite Robe Noire, Guerlain", [("La Petite Robe Noire", "/parfum/la-petite-robe-noire")], ["prn"], """
Le parfum du jour : La Petite Robe Noire, de Guerlain.

Une cerise noire, de l'amande et de la réglisse, posées sur une rose. Le fond reste longtemps sur le patchouli et le thé noir.

Avant sa sortie mondiale en 2012, elle avait d'abord été vendue en 2009 dans les seules boutiques Guerlain. Thierry Wasser en a ensuite retravaillé la formule. Elle a fait entrer le gourmand chez Guerlain.

Pour qui ? Celles qui aiment les parfums gourmands, mais avec du caractère.

Disponible sur qosmi.be""", """
Het parfum van de dag: La Petite Robe Noire van Guerlain.

Zwarte kers, amandel en zoethout op een roos. De basis blijft lang hangen op patchoeli en zwarte thee.

Voor de wereldwijde lancering in 2012 werd ze in 2009 eerst enkel in de Guerlain-boetieks verkocht. Thierry Wasser werkte de formule daarna opnieuw uit. Zo bracht ze het gourmand-genre naar Guerlain.

Voor wie? Wie van zoete parfums houdt, maar met karakter.

Verkrijgbaar op qosmi.be""", "#lapetiterobenoire #guerlain #parfumdujour #parfumfemme #qosmi")

add("04-sel-elle", "Spécial Noël · la sélection", "3 cadeaux pour elle",
    [("My Way", "/parfum/my-way"), ("Organza", "/parfum/organza"), ("Chance Eau de Parfum", "/parfum/chance")], ["myway", "organza", "chance"], """
3 idées de cadeaux pour elle, qui ne déçoivent pas :

1. Giorgio Armani My Way : bergamote, fleur d'oranger, tubéreuse et vanille. Un bouquet de fleurs blanches, lumineux et doux.

2. Givenchy Organza : néroli, jasmin, ylang-ylang et vanille, dans un flacon en forme de silhouette drapée. Composé par Sophie Labbé en 1996.

3. Chanel Chance Eau de Parfum : baies roses, jasmin, patchouli et vanille, dans le flacon rond de la ligne. Signé Jacques Polge.

Sous le sapin ? Dis-nous lequel en commentaire.
Les trois sont sur qosmi.be""", """
3 cadeau-ideeën voor haar die nooit tegenvallen:

1. Giorgio Armani My Way: bergamot, oranjebloesem, tuberoos en vanille. Een stralend en zacht boeket witte bloemen.

2. Givenchy Organza: neroli, jasmijn, ylang-ylang en vanille, in een flacon in de vorm van een gedrapeerd silhouet. Gecomponeerd door Sophie Labbé in 1996.

3. Chanel Chance Eau de Parfum: roze peper, jasmijn, patchoeli en vanille, in de ronde flacon van de lijn. Gesigneerd Jacques Polge.

Onder de kerstboom? Zeg welke in de reacties.
Alle drie op qosmi.be""", "#cadeaunoel #parfumfemme #myway #organza #chanelchance #qosmi")

add("05-bio-ropion", "Carrousel · le parfumeur", "Dominique Ropion", [("Dominique Ropion", "/parfumeur/dominique-ropion"), ("Ysatis", "/parfum/ysatis"), ("Amarige", "/parfum/amarige"), ("L'Interdit", "/parfum/linterdit-0")],
    ["ysatis", "amarige", "interdit"], """
Tu connais forcément l'un de ses parfums. Lui, beaucoup moins.

Dominique Ropion a grandi tout près des odeurs : sa mère et son grand-père travaillaient chez Roure, une maison de matières premières. Adolescent, il y passe ses vacances à faire des pesées, et croise déjà Jacques Polge et Jean-Louis Sieuzac.

Après des études de physique, il travaille avec Sieuzac de 1989 à 1998, puis entre chez IFF en 2001. On lui doit Ysatis, Amarige, Alien, et il a cosigné L'Interdit et Invictus.

Sa vision du métier : « Une formule, ça se triture dans tous les sens. »

Ysatis, Amarige et L'Interdit sont sur qosmi.be""", """
Je kent vast een van zijn parfums. Hem zelf veel minder.

Dominique Ropion groeide op tussen de geuren: zijn moeder en grootvader werkten bij Roure, een huis van grondstoffen. Als tiener bracht hij er zijn vakanties door met afwegen, en ontmoette hij al Jacques Polge en Jean-Louis Sieuzac.

Na een studie fysica werkte hij van 1989 tot 1998 samen met Sieuzac, en in 2001 ging hij naar IFF. Van hem zijn onder meer Ysatis, Amarige en Alien, en hij tekende mee voor L'Interdit en Invictus.

Zijn kijk op het vak: "Une formule, ça se triture dans tous les sens." (Een formule kneed je in alle richtingen.)

Ysatis, Amarige en L'Interdit op qosmi.be""", "#dominiqueropion #parfumeur #givenchy #ysatis #amarige #qosmi")

add("06-mat-tonka", "Carrousel · matière première", "La fève tonka", [("Fève tonka", "/matiere/feve-tonka"), ("Khamrah", "/parfum/khamrah"), ("La Vie est Belle", "/parfum/la-vie-est-belle")],
    ["khamrah", "lveb"], """
Amande, foin, caramel : c'est l'odeur de la fève tonka.

C'est la graine d'un grand arbre d'Amérique du Sud. Séchée, puis macérée dans du rhum, elle se couvre de petits cristaux de coumarine. Ce sont eux qui lui donnent son odeur si gourmande.

Jicky de Guerlain, en 1889, a été l'un des tout premiers parfums à l'utiliser. Aujourd'hui, on la trouve partout : dans le fond de Khamrah de Lattafa, ou dans La Vie est Belle de Lancôme.

Les deux sont sur qosmi.be""", """
Amandel, hooi, karamel: zo ruikt de tonkaboon.

Het is het zaad van een grote boom uit Zuid-Amerika. Gedroogd en daarna in rum geweekt, raakt het bedekt met kleine kristallen coumarine. Die geven de boon haar zoete geur.

Jicky van Guerlain (1889) was een van de allereerste parfums die ze gebruikten. Vandaag vind je ze overal: in de basis van Khamrah van Lattafa, of in La Vie est Belle van Lancôme.

Beide op qosmi.be""", "#tonka #matierepremiere #khamrah #lavieestbelle #qosmi")

add("07-sel-fraiches", "Spécial Noël · la sélection", "3 parfums frais à offrir",
    [("Eau d'Orange Verte", "/parfum/eau-dorange-verte"), ("Voyage d'Hermès", "/parfum/voyage-dhermes"), ("Un Jardin sur la Lagune", "/parfum/un-jardin-sur-le-lagune")], ["orangeverte", "voyage", "lagune"], """
Pas tout le monde aime les parfums lourds en hiver. Pour ceux qui préfèrent la fraîcheur, 3 idées signées Hermès :

1. Eau d'Orange Verte : orange, mandarine, menthe et mousse de chêne. Une eau de Cologne pétillante, composée par Françoise Caron en 1979.

2. Voyage d'Hermès : citron, thé, cardamome et muscs blancs, par Jean-Claude Ellena en 2010. Son flacon pivote, comme un objet de voyage.

3. Un Jardin sur la Lagune : magnolia, pittosporum et lys, avec des notes salées. Christine Nagel s'est inspirée d'un jardin secret de Venise.

Ton préféré ? 1, 2 ou 3 en commentaire.""", """
Niet iedereen houdt van zware parfums in de winter. Voor wie van frisheid houdt: 3 ideeën van Hermès.

1. Eau d'Orange Verte: sinaasappel, mandarijn, munt en eikenmos. Een sprankelende eau de Cologne van Françoise Caron uit 1979.

2. Voyage d'Hermès: citroen, thee, kardemom en witte musk, door Jean-Claude Ellena in 2010. De flacon draait, als een reisvoorwerp.

3. Un Jardin sur la Lagune: magnolia, pittosporum en lelie, met zilte noten. Christine Nagel liet zich inspireren door een geheime tuin in Venetië.

Jouw favoriet? 1, 2 of 3 in de reacties.""", "#hermes #parfumfrais #cadeaunoel #voyagedhermes #qosmi")

add("08-anniv-eausauvage", "Joyeux anniversaire", "Eau Sauvage a 60 ans", [("Eau Sauvage", "/parfum/eau-sauvage")], ["eausauvage"], """
Eau Sauvage a 60 ans.

En 1966, Edmond Roudnitska compose le tout premier parfum masculin de Dior : citron, bergamote, basilic, sur un fond de vétiver et de mousse de chêne.

Son secret : l'hédione, une molécule alors toute nouvelle, à l'odeur de jasmin transparent. Eau Sauvage en est le premier grand emploi, et elle est aujourd'hui partout en parfumerie.

Soixante ans plus tard, son flacon n'a presque pas bougé.

Disponible sur qosmi.be""", """
Eau Sauvage wordt 60.

In 1966 componeert Edmond Roudnitska het allereerste herenparfum van Dior: citroen, bergamot, basilicum, op een basis van vetiver en eikenmos.

Het geheim: hedione, een toen gloednieuwe molecule met de geur van transparante jasmijn. Eau Sauvage was het eerste grote parfum dat ze gebruikte; vandaag zit ze overal.

Zestig jaar later is de flacon bijna niet veranderd.

Verkrijgbaar op qosmi.be""", "#eausauvage #dior #joyeuxanniversaire #parfumhomme #qosmi")

add("09-fete-noel", "Fêtes", "Joyeux Noël", [], [], """
Joyeux Noël 🤍

Toute l'équipe Qosmi te souhaite de belles fêtes, et de beaux sillages autour de la table.

Et toi, tu as eu un parfum sous le sapin ?""", """
Vrolijk Kerstfeest 🤍

Het hele Qosmi-team wenst je fijne feestdagen, en mooie geuren rond de tafel.

En jij, kreeg je een parfum onder de kerstboom?""", "#joyeuxnoel #vrolijkkerstfeest #qosmi")

add("10-pdj-fahrenheit", "Le parfum du jour", "Fahrenheit, Dior", [("Fahrenheit", "/parfum/fahrenheit")], ["fahrenheit"], """
Le parfum du jour : Fahrenheit, de Dior.

En 1988, Jean-Louis Sieuzac bouscule la parfumerie masculine : une mandarine fraîche, puis un accord inédit de feuille de violette, de bois et de cuir.

Il divise autant qu'il séduit, et devient tout de suite un classique. Son flacon dégradé, couleur de feu, serait né d'un défaut de refroidissement du verre, selon la maison.

Pour qui ? Ceux qui aiment les parfums qui ne ressemblent à aucun autre.

Disponible sur qosmi.be""", """
Het parfum van de dag: Fahrenheit van Dior.

In 1988 zet Jean-Louis Sieuzac de herenparfumerie op zijn kop: frisse mandarijn, gevolgd door een nooit eerder geroken akkoord van viooltjesblad, hout en leer.

Het verdeelt evenveel als het verleidt, en wordt meteen een klassieker. De vuurkleurige flacon zou volgens het huis zijn ontstaan door een fout bij het afkoelen van het glas.

Voor wie? Wie houdt van parfums die op geen enkel ander lijken.

Verkrijgbaar op qosmi.be""", "#fahrenheit #dior #parfumdujour #parfumhomme #qosmi")

add("11-anniv-lightblue", "Joyeux anniversaire", "Light Blue a 25 ans", [("Light Blue", "/parfum/light-blue")], ["lightbluef"], """
Light Blue a 25 ans.

En 2001, Olivier Cresp s'inspire de la Sicile pour Dolce&Gabbana : citron de Sicile, pomme Granny Smith, bambou, jasmin et rose, sur un fond de cèdre, d'ambre et de musc.

Ses films tournés à Capri en ont fait l'un des plus grands succès de la maison. Un parfum d'été qu'on a envie de porter toute l'année.

Disponible sur qosmi.be""", """
Light Blue wordt 25.

In 2001 haalt Olivier Cresp zijn inspiratie uit Sicilië voor Dolce&Gabbana: Siciliaanse citroen, Granny Smith-appel, bamboe, jasmijn en roos, op een basis van ceder, amber en musk.

Dankzij de films op Capri werd het een van de grootste successen van het huis. Een zomerparfum dat je het hele jaar wilt dragen.

Verkrijgbaar op qosmi.be""", "#lightblue #dolcegabbana #joyeuxanniversaire #parfumfemme #qosmi")

add("12-conseil-superposer", "Carrousel · le conseil", "Superposer deux parfums", [], [], """
Superposer deux parfums, ça s'appelle le layering. Le mode d'emploi :

1. Deux parfums, pas plus : un pour la base, un pour la relever
2. Le plus riche d'abord (boisé, vanillé), le plus léger par-dessus
3. Cherche un point commun : vanille, agrumes… une note partagée les aide à s'accorder
4. Teste ton duo un jour calme, et attends une heure avant de juger

Tu as déjà un mélange préféré ? Dis-le nous en commentaire.""", """
Twee parfums combineren heet layering. Zo doe je het:

1. Twee parfums, niet meer: één als basis, één om het op te fleuren
2. Het rijkste eerst (houtig, vanille), het lichtste erover
3. Zoek een gemeenschappelijke noot: vanille, citrus… zo passen ze beter bij elkaar
4. Test je duo op een rustige dag, en wacht een uur voor je oordeelt

Heb jij al een favoriete combinatie? Vertel het in de reacties.""", "#layering #conseilparfum #astuceparfum #qosmi")

add("13-mat-iris", "Carrousel · matière première", "L'iris", [("Iris", "/matiere/iris"), ("Gentleman Eau de Parfum", "/parfum/gentleman-eau-de-parfum"), ("Gucci Bloom", "/parfum/gucci-bloom")],
    ["gentleman", "bloom"], """
L'iris, c'est la fleur qui sent… par sa racine.

En parfumerie, on n'utilise pas la fleur, mais le rhizome, sa tige souterraine. Il doit sécher environ trois ans avant d'être distillé, et une tonne d'iris ne donne que deux kilos d'huile essentielle. C'est l'une des matières les plus chères : poudrée, beurrée, un peu boisée.

Le saviez-vous ? L'iris des marais, jaune, est le symbole de Bruxelles.

À sentir dans Gentleman de Givenchy et Bloom de Gucci, sur qosmi.be""", """
De iris is de bloem die geurt… via haar wortel.

In de parfumerie gebruik je niet de bloem, maar de wortelstok. Die moet ongeveer drie jaar drogen voor hij gedistilleerd wordt, en een ton iris levert maar twee kilo essentiële olie op. Een van de duurste grondstoffen: poederig, botterig, licht houtig.

Wist je dat? De gele lis is het symbool van Brussel.

Te ruiken in Gentleman van Givenchy en Bloom van Gucci, op qosmi.be""", "#iris #matierepremiere #bruxelles #givenchy #guccibloom #qosmi")

add("14-bio-ellena", "Carrousel · le parfumeur", "Jean-Claude Ellena", [("Jean-Claude Ellena", "/parfumeur/jean-claude-ellena"), ("Terre d'Hermès", "/parfum/terre-dhermes"), ("Un Jardin sur le Toit", "/parfum/un-jardin-sur-le-toit"), ("Jour d'Hermès Absolu", "/parfum/jour-dhermes-absolu")],
    ["terre", "jardintoit", "jourabsolu"], """
Jean-Claude Ellena, le parfumeur qui fait beaucoup avec très peu.

Né à Grasse, fils de parfumeur, il commence à 16 ans chez Chiris, puis entre à l'école Givaudan de Genève en 1968. À 28 ans, il signe First pour Van Cleef & Arpels. En 2004, il devient le parfumeur exclusif d'Hermès.

Sa marque de fabrique : des formules courtes. Il travaille avec environ 200 matières premières, là où beaucoup en utilisent plus de mille. Selon lui, son métier « consiste à vous faire croire avec très peu de moyens ».

Terre d'Hermès, Un Jardin sur le Toit et Jour d'Hermès Absolu sont sur qosmi.be""", """
Jean-Claude Ellena, de parfumeur die veel doet met weinig.

Geboren in Grasse, zoon van een parfumeur, begint hij op zijn 16e bij Chiris en gaat hij in 1968 naar de Givaudan-school in Genève. Op zijn 28e tekent hij First voor Van Cleef & Arpels. In 2004 wordt hij de huisparfumeur van Hermès.

Zijn handelsmerk: korte formules. Hij werkt met ongeveer 200 grondstoffen, waar velen er meer dan duizend gebruiken.

Terre d'Hermès, Un Jardin sur le Toit en Jour d'Hermès Absolu op qosmi.be""", "#jeanclaudeellena #parfumeur #hermes #terredhermes #qosmi")

add("15-pdj-tuscan", "Le parfum du jour", "Tuscan Leather, Tom Ford", [("Tuscan Leather", "/parfum/tuscan-leather")], ["tuscan"], """
Le parfum du jour : Tuscan Leather, de Tom Ford.

En 2007, Tom Ford ajoute à sa collection Private Blend sa version du parfum de cuir classique. Framboise, safran et thym en ouverture, de l'oliban et du jasmin au cœur, puis du cuir, du daim et un bois ambré qui tiennent des heures.

Pour qui ? Ceux qui aiment les parfums riches, qui se remarquent.

Disponible sur qosmi.be""", """
Het parfum van de dag: Tuscan Leather van Tom Ford.

In 2007 voegt Tom Ford zijn versie van de klassieke leergeur toe aan de Private Blend-collectie. Framboos, saffraan en tijm als opening, wierook en jasmijn in het hart, en daarna leer, suède en amberhout die urenlang blijven.

Voor wie? Wie houdt van rijke parfums die opvallen.

Verkrijgbaar op qosmi.be""", "#tuscanleather #tomford #parfumdujour #parfumcuir #qosmi")

add("16-sel-reveillon", "Spécial réveillon · la sélection", "3 parfums pour le réveillon",
    [("La Nuit Trésor", "/parfum/la-nuit-tresor"), ("1 Million", "/parfum/1-million"), ("L'Interdit", "/parfum/linterdit-0")], ["nuittresor", "onemillion", "interdit"], """
Ce soir, on sort le grand jeu. 3 parfums pour le réveillon :

1. Lancôme La Nuit Trésor : rose, fruit de la passion, vanille et café. Le côté nuit de Trésor, plus gourmand.

2. Paco Rabanne 1 Million : mandarine, cannelle, rose et cuir, dans un flacon en forme de lingot d'or. Pour briller à minuit.

3. Givenchy L'Interdit : fleur d'oranger, tubéreuse et jasmin sur un fond de patchouli. Le grand retour, en 2018, d'un parfum créé pour Audrey Hepburn.

Tu portes lequel ce soir ?""", """
Vanavond gaan we voluit. 3 parfums voor oudejaarsavond:

1. Lancôme La Nuit Trésor: roos, passievrucht, vanille en koffie. De nachtelijke, zoetere kant van Trésor.

2. Paco Rabanne 1 Million: mandarijn, kaneel, roos en leer, in een flacon in de vorm van een goudstaaf. Om te schitteren om middernacht.

3. Givenchy L'Interdit: oranjebloesem, tuberoos en jasmijn op een basis van patchoeli. De grote terugkeer, in 2018, van een parfum dat voor Audrey Hepburn werd gemaakt.

Welke draag jij vanavond?""", "#reveillon #nouvelan #oudjaar #1million #linterdit #qosmi")

add("17-fete-annee", "Fêtes", "Bonne année 2027", [], [], """
Bonne année 2027 🤍

Merci d'avoir été là en 2026. On te souhaite une année pleine de belles découvertes, et de parfums qui te ressemblent.

Ta bonne résolution parfum pour 2027 ?""", """
Gelukkig nieuwjaar 2027 🤍

Bedankt dat je er in 2026 bij was. We wensen je een jaar vol mooie ontdekkingen, en parfums die bij je passen.

Jouw parfumvoornemen voor 2027?""", "#bonneannee #gelukkignieuwjaar #2027 #qosmi")

add("18-pdj-neroli", "Le parfum du jour", "Neroli Portofino, Tom Ford", [("Neroli Portofino", "/parfum/neroli-portofino")], ["neroli"], """
Le parfum du jour : Neroli Portofino, de Tom Ford.

Composé par Rodrigo Flores-Roux en 2007, c'est une relecture de l'eau de Cologne italienne : bergamote, mandarine et citron, néroli de Tunisie, fleur d'oranger et lavande, sur un fond d'ambre et de romarin.

Il a tellement marché qu'il a donné son nom à toute une collection. Parfait pour commencer l'année avec un peu de soleil.

Disponible sur qosmi.be""", """
Het parfum van de dag: Neroli Portofino van Tom Ford.

Gecomponeerd door Rodrigo Flores-Roux in 2007, als nieuwe kijk op de Italiaanse eau de Cologne: bergamot, mandarijn en citroen, Tunesische neroli, oranjebloesem en lavendel, op een basis van amber en rozemarijn.

Zo succesvol dat het een hele collectie zijn naam gaf. Perfect om het jaar met wat zon te beginnen.

Verkrijgbaar op qosmi.be""", "#neroliportofino #tomford #parfumdujour #parfummixte #qosmi")

add("19-conseil-familles", "Carrousel · le conseil", "Les grandes familles olfactives", [], [], """
Hespéridée, chyprée, fougère… Les familles olfactives, expliquées simplement :

1. Hespéridée : les agrumes, frais et pétillants
2. Florale : rose, jasmin, tubéreuse, la famille la plus vaste
3. Boisée : cèdre, santal, vétiver
4. Ambrée (ou orientale) : vanille, épices, résines
5. Chyprée : bergamote, mousse de chêne, patchouli. Son nom vient de Chypre, un parfum de Coty de 1917
6. Fougère : lavande, coumarine, mousse de chêne

Et toi, tu es plutôt quelle famille ?""", """
Citrus, chypre, fougère… De geurfamilies, eenvoudig uitgelegd:

1. Citrus (hespéridée): fris en sprankelend
2. Bloemig: roos, jasmijn, tuberoos, de grootste familie
3. Houtig: ceder, sandelhout, vetiver
4. Amber (of oriëntaals): vanille, specerijen, harsen
5. Chypre: bergamot, eikenmos, patchoeli. De naam komt van Chypre, een parfum van Coty uit 1917
6. Fougère: lavendel, coumarine, eikenmos

En jij, welke familie past bij jou?""", "#famillesolfactives #conseilparfum #parfum #qosmi")

add("20-mat-patchouli", "Carrousel · matière première", "Le patchouli", [("Patchouli", "/matiere/patchouli"), ("La Petite Robe Noire", "/parfum/la-petite-robe-noire"), ("La Nuit Trésor", "/parfum/la-nuit-tresor")],
    ["prn", "nuittresor"], """
Le patchouli, tu crois le connaître ?

C'est une plante tropicale, cultivée surtout en Indonésie. Ses feuilles fraîches ne sentent presque rien : c'est le séchage, puis la distillation, qui révèlent son odeur terreuse, boisée, un peu camphrée. Il sert aussi à faire durer les autres notes.

Star des années 70, puis un peu oublié, il revient en force dans les années 1990 avec Angel de Thierry Mugler.

Aujourd'hui, il est dans le fond de La Petite Robe Noire et de La Nuit Trésor. Les deux sont sur qosmi.be""", """
Patchoeli, denk je het te kennen?

Het is een tropische plant, vooral geteeld in Indonesië. De verse bladeren ruiken bijna nergens naar: pas door het drogen en distilleren komt de aardse, houtige, licht kamferachtige geur vrij. Het helpt ook om andere noten langer te laten duren.

Een ster in de jaren 70, daarna wat vergeten, en in de jaren 90 terug dankzij Angel van Thierry Mugler.

Vandaag zit het in de basis van La Petite Robe Noire en La Nuit Trésor. Beide op qosmi.be""", "#patchouli #matierepremiere #guerlain #lancome #qosmi")

add("21-pdj-kenzoworld", "Le parfum du jour", "Kenzo World, Kenzo", [("Kenzo World", "/parfum/kenzo-world")], ["kenzoworld"], """
Le parfum du jour : Kenzo World.

Lancé en 2016, c'est Francis Kurkdjian qui l'a composé : pivoine, jasmin d'Égypte et Ambroxan, dans un floral ambré.

Son flacon en forme d'œil reprend un motif des collections Kenzo, et son film signé Spike Jonze, où danse Margaret Qualley, a fait le tour du monde.

Pour qui ? Celles qui aiment les fleurs, mais sans rien de sage.

Disponible sur qosmi.be""", """
Het parfum van de dag: Kenzo World.

Gelanceerd in 2016 en gecomponeerd door Francis Kurkdjian: pioen, Egyptische jasmijn en Ambroxan, in een bloemig-amberachtig parfum.

De flacon in de vorm van een oog komt uit de Kenzo-collecties, en de film van Spike Jonze, met een dansende Margaret Qualley, ging de wereld rond.

Voor wie? Wie van bloemen houdt, maar zonder braafheid.

Verkrijgbaar op qosmi.be""", "#kenzoworld #kenzo #parfumdujour #franciskurkdjian #qosmi")

add("22-pdj-bloom", "Le parfum du jour", "Bloom, Gucci", [("Gucci Bloom", "/parfum/gucci-bloom")], ["bloom"], """
Le parfum du jour : Bloom, de Gucci.

Composé par Alberto Morillas en 2017, il réunit des fleurs blanches : tubéreuse, jasmin, et un fond poudré d'iris. Comme un jardin en pleine floraison.

Pour qui ? Celles qui aiment les bouquets riches, généreux et lumineux.

Disponible sur qosmi.be""", """
Het parfum van de dag: Bloom van Gucci.

Gecomponeerd door Alberto Morillas in 2017, met witte bloemen: tuberoos, jasmijn en een poederige basis van iris. Als een tuin in volle bloei.

Voor wie? Wie houdt van rijke, gulle en stralende boeketten.

Verkrijgbaar op qosmi.be""", "#guccibloom #gucci #parfumdujour #parfumfemme #qosmi")

add("23-bio-nagel", "Carrousel · le parfumeur", "Christine Nagel", [("Christine Nagel", "/parfumeur/christine-nagel"), ("Un Jardin sur la Lagune", "/parfum/un-jardin-sur-le-lagune"), ("Eau de Basilic Pourpre", "/parfum/eau-de-basilic-pourpre")],
    ["lagune", "basilic"], """
Christine Nagel ne se destinait pas du tout à la parfumerie.

Née à Genève en 1959, chimiste de formation, elle commence chez Firmenich au service chromatographie : elle analyse les parfums, molécule par molécule. Un jour, Alberto Morillas lui fait sentir ses accords. Elle décide de devenir parfumeur.

Elle signe ensuite The One de Dolce&Gabbana ou Miss Dior Chérie, puis entre chez Hermès en 2014. Depuis 2016, elle y dirige la création des parfums.

Un Jardin sur la Lagune et Eau de Basilic Pourpre sont sur qosmi.be""", """
Christine Nagel was helemaal niet voorbestemd voor de parfumerie.

Geboren in Genève in 1959, opgeleid als scheikundige, begint ze bij Firmenich op de afdeling chromatografie: ze analyseert parfums, molecule per molecule. Op een dag laat Alberto Morillas haar zijn akkoorden ruiken. Ze besluit parfumeur te worden.

Daarna tekent ze onder meer The One van Dolce&Gabbana en Miss Dior Chérie, en in 2014 gaat ze naar Hermès. Sinds 2016 leidt ze er de parfumcreatie.

Un Jardin sur la Lagune en Eau de Basilic Pourpre op qosmi.be""", "#christinenagel #parfumeur #hermes #unjardinsurlalagune #qosmi")

add("24-conseil-pyramide", "Carrousel · le conseil", "Tête, cœur, fond", [], [], """
Notes de tête, de cœur, de fond : comment se lit un parfum ?

1. Les notes de tête : les premières minutes, souvent des agrumes ou des notes fraîches, qui s'évaporent vite
2. Les notes de cœur : elles prennent le relais et donnent sa personnalité au parfum
3. Les notes de fond : celles qui restent des heures sur la peau, comme les bois, la vanille ou les muscs

Le bon réflexe : ne juge jamais un parfum sur les premières secondes. Attends son cœur.

Quelle note sens-tu en premier sur ton parfum ?""", """
Topnoten, hartnoten, basisnoten: hoe lees je een parfum?

1. De topnoten: de eerste minuten, vaak citrus of frisse noten die snel verdampen
2. De hartnoten: die nemen het over en geven het parfum zijn karakter
3. De basisnoten: die blijven urenlang op de huid, zoals hout, vanille of musk

Goede reflex: beoordeel een parfum nooit op de eerste seconden. Wacht op het hart.

Welke noot ruik jij eerst in jouw parfum?""", "#pyramideolfactive #conseilparfum #parfum #qosmi")

add("25-pdj-habitrouge", "Le parfum du jour", "Habit Rouge, Guerlain", [("Habit Rouge", "/parfum/habit-rouge")], ["habitrouge"], """
Le parfum du jour : Habit Rouge, de Guerlain.

En 1965, Jean-Paul Guerlain imagine un parfum pour homme élégant et chaleureux : lavande, néroli et agrumes, un cœur de rose et de jasmin, puis un fond de cannelle, de patchouli et de vanille.

À l'époque, les parfums masculins manquaient d'audace. Habit Rouge, lui, osait les fleurs et la vanille.

Pour qui ? Ceux qui aiment les classiques qui ne vieillissent pas.

Disponible sur qosmi.be""", """
Het parfum van de dag: Habit Rouge van Guerlain.

In 1965 bedenkt Jean-Paul Guerlain een elegant en warm herenparfum: lavendel, neroli en citrus, een hart van roos en jasmijn, en daarna een basis van kaneel, patchoeli en vanille.

Herenparfums waren toen weinig gedurfd. Habit Rouge durfde bloemen en vanille.

Voor wie? Wie houdt van klassiekers die niet verouderen.

Verkrijgbaar op qosmi.be""", "#habitrouge #guerlain #parfumdujour #parfumhomme #qosmi")

add("26-mat-cannelle", "Carrousel · matière première", "La cannelle", [("Cannelle", "/matiere/cannelle"), ("1 Million", "/parfum/1-million"), ("Boss Bottled Eau de Parfum", "/parfum/boss-bottled-eau-de-parfum")],
    ["onemillion", "bossedp"], """
La cannelle, la plus ancienne des épices connues.

C'est l'écorce intérieure du cannelier, un arbre originaire d'Asie tropicale. Elle vient aujourd'hui surtout du Sri Lanka, des Seychelles et de Madagascar. Dans l'Antiquité, on s'en servait déjà pour embaumer.

En parfumerie, elle est chaude, sucrée, épicée, et réchauffe les parfums ambrés et boisés. On la sent dans 1 Million de Paco Rabanne ou Boss Bottled Eau de Parfum.

Les deux sont sur qosmi.be""", """
Kaneel, de oudste bekende specerij.

Het is de binnenste schors van de kaneelboom, oorspronkelijk uit tropisch Azië. Vandaag komt ze vooral uit Sri Lanka, de Seychellen en Madagaskar. In de oudheid gebruikte men ze al om te balsemen.

In parfum is kaneel warm, zoet en kruidig, en verwarmt het amberachtige en houtige parfums. Je ruikt het in 1 Million van Paco Rabanne of Boss Bottled Eau de Parfum.

Beide op qosmi.be""", "#cannelle #matierepremiere #1million #bossbottled #qosmi")

add("27-conseil-conserver", "Carrousel · le conseil", "Combien de temps se garde un parfum ?", [], [], """
Ton parfum a-t-il une date limite ?

1. Fermé et bien rangé, un flacon peut se garder des années
2. Une fois ouvert, il reste en général beau plusieurs années, s'il est bien conservé
3. Ses trois ennemis : la lumière, la chaleur et l'air. Garde-le dans sa boîte, dans un placard
4. Les signes qui ne trompent pas : une couleur qui fonce, une odeur aigre ou métallique au début

Fais le test : va sentir ton plus vieux flacon, et dis-nous en commentaire.""", """
Heeft je parfum een vervaldatum?

1. Gesloten en goed bewaard kan een flacon jarenlang mee
2. Eenmaal geopend blijft hij meestal enkele jaren mooi, als je hem goed bewaart
3. Zijn drie vijanden: licht, warmte en lucht. Bewaar hem in zijn doos, in een kast
4. Signalen die niet liegen: een donkerder kleur, een zure of metalige geur bij het begin

Doe de test: ruik aan je oudste flacon, en laat het ons weten in de reacties.""", "#conseilparfum #conserverparfum #astuceparfum #qosmi")

add("28-conseil-doser", "Carrousel · le conseil", "Combien de pulvérisations ?", [], [], """
Combien de pulvérisations, au juste ?

1. Eau de toilette : en général 3 ou 4, elle est plus légère
2. Eau de parfum : 2 ou 3 suffisent
3. Extrait : 1 ou 2, ou quelques touches du bout des doigts
4. Pense aux autres : au bureau ou au restaurant, ton parfum doit se sentir de près, pas à trois mètres

Et toi, combien de pschitt le matin ?""", """
Hoeveel keer verstuiven, eigenlijk?

1. Eau de toilette: meestal 3 of 4, ze is lichter
2. Eau de parfum: 2 of 3 is genoeg
3. Extrait: 1 of 2, of een paar toetsjes met je vingertoppen
4. Denk aan de anderen: op kantoor of op restaurant ruik je je parfum van dichtbij, niet op drie meter

En jij, hoeveel pschitt 's ochtends?""", "#conseilparfum #astuceparfum #parfum #qosmi")

add("29-pdj-invictus", "Le parfum du jour", "Invictus, Paco Rabanne", [("Invictus", "/parfum/invictus")], ["invictus"], """
Le parfum du jour : Invictus, de Paco Rabanne.

Lancé en 2013, il est signé par quatre parfumeurs : Véronique Nyberg, Anne Flipo, Olivier Polge et Dominique Ropion. Le choc d'un pamplemousse frais et d'un accord marin, sur un fond de bois de gaïac, de patchouli et d'ambre gris.

Son flacon en forme de trophée a été dessiné par Cédric Ragot.

Pour qui ? Ceux qui aiment les parfums frais, mais avec du fond.

Disponible sur qosmi.be""", """
Het parfum van de dag: Invictus van Paco Rabanne.

Gelanceerd in 2013 en getekend door vier parfumeurs: Véronique Nyberg, Anne Flipo, Olivier Polge en Dominique Ropion. Frisse grapefruit en een zeeakkoord, op een basis van guajakhout, patchoeli en grijze amber.

De flacon in de vorm van een trofee werd ontworpen door Cédric Ragot.

Voor wie? Wie houdt van frisse parfums, maar met diepgang.

Verkrijgbaar op qosmi.be""", "#invictus #pacorabanne #parfumdujour #parfumhomme #qosmi")

add("30-sel-valentin", "Saint-Valentin · la sélection", "La Saint-Valentin, c'est dans un mois",
    [("La Petite Robe Noire", "/parfum/la-petite-robe-noire"), ("Spicebomb", "/parfum/spicebomb"), ("Kenzo World", "/parfum/kenzo-world")], ["prn", "spicebomb", "kenzoworld"], """
La Saint-Valentin, c'est dans un mois. On prend de l'avance ?

1. Guerlain La Petite Robe Noire : cerise, amande, rose et réglisse. Gourmande et sûre d'elle.

2. Viktor&Rolf Spicebomb : pour lui, s'il aime les parfums qui réchauffent.

3. Kenzo World : pivoine et jasmin, dans un flacon en forme d'œil impossible à oublier.

Toutes nos idées sont sur qosmi.be""", """
Valentijn is binnen een maand. Al wat voorbereiden?

1. Guerlain La Petite Robe Noire: kers, amandel, roos en zoethout. Zoet en zelfzeker.

2. Viktor&Rolf Spicebomb: voor hem, als hij van verwarmende parfums houdt.

3. Kenzo World: pioen en jasmijn, in een flacon in de vorm van een oog die je niet vergeet.

Al onze ideeën op qosmi.be""", "#saintvalentin #valentijn #cadeauparfum #qosmi")

PRODUITS = json.load(open(os.path.join(ICI, "..", "lot2", "produits_lot2.json")))
OUT = os.path.join(ICI, "out3")
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
d0 = dt.date(2026, 12, 16)
out = []
for k, (pid, typ, titre, src, prods, fr, nl, tags) in enumerate(L):
    d = d0 + dt.timedelta(days=k)
    imgs = sorted([f[:-4] for f in os.listdir(OUT) if f.startswith(pid + "-") and f[len(pid) + 1:-4].isdigit()], key=lambda x: int(x.rsplit("-", 1)[1]))
    assert imgs, pid
    out.append({"n": k + 31, "id": pid, "date": "%s %d %s" % (JOURS[d.weekday()], d.day, MOIS[d.month]), "iso": d.isoformat(),
                "sur": typ, "titre": titre, "img": imgs, "produits": [PRODUITS[p] for p in prods], "src": [[a, O + b] for a, b in src],
                "txt": fr, "txt_nl": nl, "tags": tags})
json.dump(out, open(os.path.join(ICI, "lot2.json"), "w"), ensure_ascii=False, indent=1)
print(len(out), "publications,", sum(len(p["img"]) for p in out), "visuels")
