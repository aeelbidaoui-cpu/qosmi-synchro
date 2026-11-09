"""Lot n°1 Qosmi : calendrier et légendes des 30 publications (16/11 → 15/12/2026)."""
import json, os, datetime as dt

O = "https://www.olfastory.com"
L = []  # (id, type, titre, sources, légende)

L.append(("1-parfum-du-jour", "Le parfum du jour", "Delina, Parfums de Marly", [("Delina", "/parfum/delina-parfums-de-marly")], """Le parfum du jour : Delina, de Parfums de Marly.

Une rose de Damas, mais pas sage du tout. La rhubarbe et le litchi ouvrent le bal, la vanille et la muscade arrivent ensuite, et le fond reste longtemps sur le vétiver, le cèdre et l'encens.

Composé par Quentin Bisch en 2017, il s'inspire des dames de la cour. Depuis, la maison en a fait une lignée : Delina La Rosée, puis Delina Exclusif.

Pour qui ? Celles qui aiment la rose, mais fraîche et un peu fruitée.

Disponible sur qosmi.be

#delina #parfumsdemarly #parfumdujour #parfumdeniche #qosmi"""))

L.append(("2-carrousel-hiver", "Carrousel · la sélection", "3 parfums pour les soirs d'hiver", [("Lost Cherry", "/parfum/lost-cherry"), ("Angels' Share", "/parfum/angels-share"), ("Black Orchid", "/parfum/black-orchid")], """Quand il fait nuit à 17 h, on a envie de parfums qui réchauffent. Nos 3 choix pour les soirées d'hiver :

1. Tom Ford Lost Cherry : cerise noire, liqueur et amande amère, sur un fond de fève tonka. Gourmand, mais adulte.

2. By Kilian Angels' Share : une vraie essence de cognac, de la cannelle et de la praline. Kilian Hennessy s'est inspiré des chais de cognac qu'il visitait enfant.

3. Tom Ford Black Orchid : le tout premier parfum de Tom Ford, sorti en 2006. Il a 20 ans cette année.

Ton préféré ? Dis-nous 1, 2 ou 3 en commentaire.
Les trois sont sur qosmi.be

#parfumhiver #tomford #kilian #lostcherry #angelsshare"""))

L.append(("3-carrousel-conseil", "Carrousel · le conseil", "5 gestes pour que ton parfum tienne", [], """Ton parfum disparaît au bout de deux heures ? Avant d'accuser le flacon, regarde comment tu le portes.

5 gestes simples :
1. Hydrate ta peau avant, avec une crème sans parfum
2. Vise les points chauds : poignets, cou, creux des coudes
3. Ne frotte pas tes poignets
4. Un nuage sur ton écharpe (pas sur la soie)
5. Range ton flacon loin de la lumière et de la chaleur

Enregistre le post pour t'en souvenir, et donne-nous ton astuce en commentaire.

#conseilparfum #astuceparfum #parfum #qosmi"""))

L.append(("4-matiere-oud", "Carrousel · matière première", "L'oud", [("Oud", "/matiere/oud"), ("Oud Wood", "/parfum/oud-wood")], """L'oud, tu en sens partout. Mais tu sais d'où il vient ?

C'est une résine. L'Aquilaria, un arbre des forêts tropicales d'Asie, la fabrique pour se défendre quand un champignon l'attaque. Le bois devient sombre, lourd et très parfumé. Son nom vient de l'arabe « al-oud » : le bois.

Au Moyen-Orient, il est vénéré depuis toujours. En 2007, Tom Ford lui consacre Oud Wood : de l'oud, du santal et du vétiver, réchauffés par la vanille et la fève tonka.

Envie de l'essayer ? Oud Wood et toute notre sélection de parfums arabes sont sur qosmi.be

#oud #matierepremiere #tomford #oudwood #parfumarabe"""))

L.append(("5-anniversaire-coco", "Joyeux anniversaire", "Coco Mademoiselle a 25 ans", [("Coco Mademoiselle", "/parfum/coco-mademoiselle")], """Coco Mademoiselle a 25 ans.

En 2001, Jacques Polge, alors parfumeur de Chanel, imagine une version plus jeune de Coco : une orange vive, un cœur de rose et de jasmin, et un fond de patchouli et de vétiver. Kate Moss en est le premier visage, Keira Knightley lui succède en 2007.

Vingt-cinq ans plus tard, c'est toujours l'un de ces sillages qu'on reconnaît en croisant quelqu'un dans la rue.

Et toi, tu l'as déjà porté ?
L'eau de parfum est sur qosmi.be

#cocomademoiselle #chanel #parfumculte #qosmi"""))

L.append(("06-pdj-jadore", "Le parfum du jour", "J'adore, Dior", [("J'adore", "/parfum/jadore")], """Le parfum du jour : J'adore, de Dior.

Un floral solaire, tout en or : la mandarine et la bergamote en ouverture, puis un bouquet de rose, de jasmin et de violette, sur un fond de muscs blancs.

Composé par Calice Becker en 1999, il a même détrôné le N°5 de Chanel en 2010, en devenant le parfum féminin le plus vendu en France. Son flacon amphore, signé Hervé Van der Straeten, se reconnaît au premier coup d'œil.

Un classique qu'on offre les yeux fermés, surtout à Noël.

Disponible sur qosmi.be

#jadore #dior #parfumdujour #parfumfemme #qosmi"""))

L.append(("07-bio-kurkdjian", "Carrousel · le parfumeur", "Francis Kurkdjian", [("Francis Kurkdjian", "/parfumeur/francis-kurkdjian"), ("Le Male", "/parfum/le-male"), ("Gentle Fluidity Gold", "/parfum/gentle-fluidity-gold")], """Francis Kurkdjian a décidé de devenir parfumeur à 15 ans, sans rien connaître du métier.

Il entre à l'ISIPCA, l'école de parfumerie de Versailles, en 1990. Cinq ans plus tard, il signe Le Male pour Jean Paul Gaultier. En 2009, il ouvre sa propre maison, d'où viennent Aqua Universalis puis Gentle Fluidity.

Avant la parfumerie, il y a eu le piano et la danse classique. Ça se sent dans ses créations : beaucoup de rigueur, et toujours de l'émotion.

Le Male, Aqua Universalis Cologne Forte et Gentle Fluidity Gold sont sur qosmi.be

#franciskurkdjian #parfumeur #mfk #lemale #qosmi"""))

L.append(("08-sel-noel-elle", "Carrousel · spécial Noël", "3 cadeaux pour elle", [("La Vie est Belle", "/parfum/la-vie-est-belle"), ("Flowerbomb", "/parfum/flowerbomb")], """Tu cherches quoi lui offrir ? 3 parfums qui font plaisir à coup sûr :

1. Yves Saint Laurent Libre : la lavande rencontre la fleur d'oranger, sur un fond de vanille. Élégant, sans jamais être sage.

2. Lancôme La Vie est Belle : poire, iris, praline et vanille. Le gourmand qu'on ne présente plus, sorti en 2012.

3. Viktor&Rolf Flowerbomb : thé, jasmin, orchidée et rose sur un fond de patchouli. Le tout premier parfum de la maison, en 2005, dans son flacon en forme de grenade.

Lequel finira sous le sapin ? Dis-le nous en commentaire.

#cadeaunoel #parfumfemme #ideecadeau #noel2026 #qosmi"""))

L.append(("09-mat-vanille", "Carrousel · matière première", "La vanille", [("Vanille", "/matiere/vanille"), ("Shalimar", "/parfum/shalimar"), ("Yara", "/parfum/yara")], """La vanille, tu la connais en cuisine. En parfumerie, c'est une star.

C'est le fruit d'une orchidée. Originaire du Mexique, où elle parfumait déjà le cacao, elle pousse aujourd'hui surtout à Madagascar et à La Réunion. Sa gousse réunit des centaines de molécules odorantes, d'où cette odeur à la fois sucrée, grasse et un peu épicée.

C'est Shalimar de Guerlain, en 1925, qui l'a rendue incontournable dans les parfums.

À sentir : Guerlain Shalimar, et Lattafa Yara pour une vanille plus gourmande. Les deux sont sur qosmi.be

#vanille #matierepremiere #shalimar #parfumgourmand #qosmi"""))

L.append(("10-conseil-offrir", "Carrousel · le conseil (Noël)", "Offrir un parfum sans se tromper", [], """Offrir un parfum, c'est le cadeau qui fait peur. Pourtant, avec ces 4 réflexes, tu tombes juste presque à tous les coups :

1. Regarde ce qu'il ou elle porte déjà
2. Pense à ses goûts, pas aux tiens
3. Mise sur un classique en cas de doute
4. Choisis une taille raisonnable pour une première fois

Tu hésites encore ? Envoie-nous un message, on t'aide à choisir.

#cadeaunoel #offrirunparfum #conseilparfum #noel2026 #qosmi"""))

L.append(("11-pdj-shalimar", "Le parfum du jour", "Shalimar, Guerlain", [("Shalimar", "/parfum/shalimar")], """Le parfum du jour a plus de cent ans : Shalimar, de Guerlain.

Jacques Guerlain le crée en 1925 autour de la vanilline, une vanille de synthèse. On le présente souvent comme le premier grand oriental de l'histoire.

Son nom vient des jardins de Shalimar, liés à l'histoire d'amour de l'empereur Shah Jahan et de Mumtaz Mahal, celle du Taj Mahal.

Bergamote, iris, vanille, fève tonka : un sillage chaud qu'on reconnaît entre mille.

Disponible sur qosmi.be

#shalimar #guerlain #parfumdujour #parfumculte #qosmi"""))

L.append(("12-sel-noel-lui", "Carrousel · spécial Noël", "3 cadeaux pour lui", [("Bleu de Chanel", "/parfum/bleu-de-chanel"), ("Sauvage Parfum", "/parfum/sauvage-parfum"), ("Aventus", "/parfum/aventus-creed")], """Pour lui, 3 valeurs sûres qu'on ne regrette jamais d'offrir :

1. Bleu de Chanel : agrumes, gingembre et bois de santal. Créé par Jacques Polge en 2010, c'est le premier grand parfum masculin de Chanel depuis Égoïste.

2. Dior Sauvage Parfum : mandarine, bergamote, santal et vanille. La version concentrée de Sauvage, plus chaude et enveloppante.

3. Creed Aventus : ananas, bouleau fumé et mousse de chêne. La maison dit s'être inspirée de la vie de Napoléon.

Ton choix ? 1, 2 ou 3 en commentaire.

#cadeaunoel #parfumhomme #bleudechanel #sauvage #aventus"""))

L.append(("13-anniv-terre", "Joyeux anniversaire", "Terre d'Hermès a 20 ans", [("Terre d'Hermès", "/parfum/terre-dhermes")], """Terre d'Hermès a 20 ans.

En 2006, Jean-Claude Ellena compose pour Hermès un parfum sur le lien entre l'homme et la terre : l'éclat du pamplemousse et de l'orange, une touche minérale de silex et de poivre, puis le cèdre et le vétiver.

Vingt ans plus tard, ce boisé minéral n'a pas pris une ride.

Tu l'as déjà senti ?
Disponible sur qosmi.be

#terredhermes #hermes #jeanclaudeellena #parfumhomme #qosmi"""))

L.append(("14-bio-bisch", "Carrousel · le parfumeur", "Quentin Bisch", [("Quentin Bisch", "/parfumeur/quentin-bisch"), ("Valaya", "/parfum/parfums-de-marly-valaya")], """À 11 ans, Quentin Bisch annonce à un professeur qu'il sera parfumeur. Le problème : il est nul en sciences, et les écoles de parfumerie demandent de la chimie.

Il fait donc un master en arts du spectacle… puis écrit aux grandes maisons. Il devient assistant parfumeur à Grasse, avant d'être formé chez Givaudan.

On lui doit entre autres Delina et Valaya de Parfums de Marly, et Very Good Girl de Carolina Herrera. Sa mémoire olfactive est telle qu'il se souvient encore du parfum de chacun de ses professeurs.

Ses créations sont sur qosmi.be

#quentinbisch #parfumeur #delina #verygoodgirl #qosmi"""))

L.append(("15-conseil-concentrations", "Carrousel · le conseil", "Eau de toilette, eau de parfum, extrait", [], """Eau de toilette, eau de parfum, extrait… ce n'est pas qu'une question de prix.

La différence, c'est la quantité de concentré de parfum dans l'alcool. En général :
• Eau de toilette : 5 à 15 %, plus légère et fraîche
• Eau de parfum : 15 à 20 %, plus de tenue
• Extrait : 20 % et plus, le plus riche

Attention : un même nom peut sentir assez différemment d'une version à l'autre. Ce n'est pas toujours la même formule en plus concentré.

Et toi, tu es plutôt team eau de toilette ou team extrait ?

#conseilparfum #eaudeparfum #extraitdeparfum #parfum #qosmi"""))

L.append(("16-pdj-9pm", "Le parfum du jour", "9pm, Afnan", [("9pm", "/parfum/afnan-9pm")], """Le parfum du jour : 9pm, d'Afnan.

Son nom veut dire 21 h, et ce n'est pas un hasard : c'est un parfum de soirée. Lavande, pomme et cannelle en ouverture, puis un fond chaud de vanille, de patchouli et de fève tonka.

Sorti en 2020, il a tellement plu qu'Afnan en a fait toute une ligne : 9pm Elixir, Rebel, Pour Femme, Night Out…

Parfait pour les soirées d'hiver, et doux pour le budget.

Disponible sur qosmi.be

#afnan #9pm #parfumarabe #parfumdujour #qosmi"""))

L.append(("17-mat-rose", "Carrousel · matière première", "La rose", [("Rose", "/matiere/rose")], """La rose, la reine des fleurs, et des parfums.

En parfumerie, on travaille surtout deux roses : la rose centifolia, aussi appelée rose de mai, cultivée en France et au Maroc, et la rose de Damas, cultivée en Bulgarie et en Turquie.

La rose de Damas est distillée pour obtenir une huile essentielle fraîche, presque citronnée. La centifolia donne une absolue plus chaude, miellée, presque épicée.

À sentir : Delina, construit autour de la rose de Damas, et Coco Mademoiselle, où la rose rencontre le jasmin. Sur qosmi.be

#rose #matierepremiere #rosedemai #parfumfloral #qosmi"""))

L.append(("18-sel-mixtes", "Carrousel · spécial Noël", "3 parfums à partager à deux", [("CK One", "/parfum/ck-one"), ("Colonia", "/parfum/acqua-di-parma-colonia"), ("Red Tobacco", "/parfum/mancera-red-tobacco")], """Un seul parfum pour deux : les mixtes, c'est l'idée cadeau maligne.

1. Calvin Klein CK One : pensé pour les hommes comme pour les femmes dès 1994. Agrumes, thé vert, muscs propres. Le parfum de toute une génération.

2. Acqua di Parma Colonia : l'eau de Cologne qui a fondé la maison en 1916. Agrumes, lavande, vétiver. Le chic italien en flacon.

3. Mancera Red Tobacco : cannelle, safran et tabac. Pour ceux qui aiment les parfums qui se remarquent.

Vous partageriez lequel ?

#parfummixte #cadeaunoel #ckone #acquadiparma #qosmi"""))

L.append(("19-pdj-hypnotic", "Le parfum du jour", "Hypnotic Poison, Dior", [("Hypnotic Poison", "/parfum/hypnotic-poison")], """Le parfum du jour : Hypnotic Poison, de Dior.

En 1998, Annick Menardo reprend l'idée de Poison, sorti treize ans plus tôt, et la rend gourmande. Au centre, une amande amère qui tient tête à la vanille et au santal. En ouverture, de la noix de coco, de la prune et de l'abricot.

Envoûtant, comme son nom l'indique. Parfait pour les soirées de décembre.

Disponible sur qosmi.be

#hypnoticpoison #dior #parfumdujour #parfumgourmand #qosmi"""))

L.append(("20-bio-polge", "Carrousel · le parfumeur", "Jacques Polge", [("Jacques Polge", "/parfumeur/jacques-polge"), ("Coco Mademoiselle", "/parfum/coco-mademoiselle")], """Pendant 37 ans, de 1978 à 2015, c'est lui qui a composé les parfums Chanel.

Jacques Polge est né en 1943 dans le Vaucluse. Après Givaudan Roure, il entre chez Chanel en 1978, où il succède à Henri Robert, le créateur du N°19 et de Cristalle. La mission : faire vivre l'héritage du N°5.

Son premier parfum pour la maison ? Coco, en 1984. Suivront Allure, Coco Mademoiselle, Bleu de Chanel… Aujourd'hui, c'est son fils Olivier Polge qui a pris le relais.

Coco Mademoiselle et Bleu de Chanel sont sur qosmi.be

#jacquespolge #chanel #parfumeur #cocomademoiselle #bleudechanel"""))

L.append(("21-conseil-tester", "Carrousel · le conseil", "Comment bien tester un parfum", [], """Tu achètes souvent un parfum sur un coup de cœur… et tu le regrettes deux heures plus tard ? Voici comment bien tester :

1. Commence par la mouillette pour faire un premier tri
2. Puis teste sur la peau : c'est là que le parfum se révèle vraiment
3. Attends au moins une heure avant de décider
4. Pas plus de trois parfums à la fois
5. Entre deux essais, repose ton nez en sentant ton pull

Enregistre ce post pour ta prochaine virée en parfumerie.

#conseilparfum #testerunparfum #astuceparfum #parfum #qosmi"""))

L.append(("22-sel-arabes", "Carrousel · spécial Noël", "3 parfums arabes à offrir", [("Khamrah", "/parfum/khamrah"), ("Yara", "/parfum/yara"), ("Asad", "/parfum/lattafa-asad")], """Envie d'offrir un parfum qui sort de l'ordinaire, sans exploser le budget ? Les parfums arabes sont faits pour ça.

1. Lattafa Khamrah : cannelle, dattes, praline et vanille. Chaud et gourmand, taillé pour l'hiver.

2. Lattafa Yara : orchidée, fruits exotiques et vanille. Doux et réconfortant, il a donné naissance à toute une ligne.

3. Lattafa Asad : poivre noir, tabac et café. Son nom veut dire « lion » en arabe.

Toute notre sélection de parfums arabes est sur qosmi.be

#parfumarabe #lattafa #khamrah #yara #cadeaunoel"""))

L.append(("23-mat-santal", "Carrousel · matière première", "Le santal", [("Santal", "/matiere/santal")], """Le santal, c'est ce bois doux et crémeux qu'on retrouve au fond de tant de parfums.

Il est connu depuis 4 000 ans : l'Égypte ancienne l'utilisait déjà. Aujourd'hui, il vient surtout d'Inde, mais aussi d'Australie ou du Sri Lanka. Devenu rare, il coûte de plus en plus cher.

Sa particularité : il n'est pas très puissant, mais il tient longtemps et donne du velouté à tout ce qu'il touche.

À sentir : Bleu de Chanel, qui revendique un santal de Nouvelle-Calédonie, et Hypnotic Poison, où il enveloppe l'amande et la vanille. Sur qosmi.be

#santal #matierepremiere #boisdesantal #parfumboise #qosmi"""))

L.append(("24-pdj-hacivat", "Le parfum du jour", "Hacivat, Nishane", [("Hacivat", "/parfum/nishane-hacivat")], """Le parfum du jour : Hacivat, de Nishane.

Une maison d'Istanbul, un extrait de parfum et une histoire : Hacivat est un personnage du théâtre d'ombres turc, popularisé à l'époque ottomane. Le parfum fait partie d'une trilogie qui rend hommage à ce théâtre.

Dans le flacon : de l'ananas et du pamplemousse très frais, puis du jasmin, du patchouli et du cèdre, sur un fond de mousse de chêne. Un chypre fruité qu'on n'oublie pas.

Disponible sur qosmi.be

#nishane #hacivat #parfumdeniche #parfumdujour #qosmi"""))

L.append(("25-anniv-goodgirl", "Joyeux anniversaire", "Good Girl a 10 ans", [("Good Girl", "/parfum/good-girl")], """Good Girl a 10 ans.

En 2016, Carolina Herrera sort un parfum dans un flacon en forme d'escarpin bleu nuit. Pari gagné : il fait exploser les ventes de la maison.

Dedans, Louise Turner (qui a aussi composé Lost Cherry pour Tom Ford) mélange l'amande et le café, la tubéreuse et le jasmin, puis la fève tonka et le cacao.

Team Good Girl ou Very Good Girl ?
Les deux sont sur qosmi.be

#goodgirl #carolinaherrera #parfumfemme #anniversaire #qosmi"""))

L.append(("26-bio-morillas", "Carrousel · le parfumeur", "Alberto Morillas", [("Alberto Morillas", "/parfumeur/alberto-morillas"), ("CK One", "/parfum/ck-one"), ("Light Blue pour Homme", "/parfum/light-blue-pour-homme")], """Alberto Morillas n'a jamais fait d'école de parfumerie.

Né à Séville en 1950, il étudie les Beaux-Arts à Genève quand un article sur la parfumerie le fascine. Il entre chez Firmenich, d'abord au service chimie, et apprend le métier seul, en étudiant les matières premières.

Son premier grand succès arrive avec Must de Cartier, en 1981. Suivront CK One, Light Blue pour Homme et bien d'autres. En 2003, il reçoit le prix François Coty, l'une des grandes récompenses du métier.

CK One et Light Blue pour Homme sont sur qosmi.be

#albertomorillas #parfumeur #ckone #lightblue #qosmi"""))

L.append(("27-conseil-peau", "Carrousel · le conseil", "Pourquoi il ne sent pas pareil sur toi", [], """Ton ami(e) sent divinement bon avec ce parfum, tu l'achètes… et sur toi, ce n'est pas pareil. Normal !

• Ta peau : sèche ou grasse, elle ne retient pas les notes de la même façon
• Ta température : une peau plus chaude diffuse davantage
• La saison : le froid freine le parfum, la chaleur l'amplifie
• Ton nez : au bout de quelques minutes, tu ne sens plus ton propre parfum, mais les autres oui

Le bon réflexe : toujours tester sur ta peau avant d'acheter.

#conseilparfum #parfum #astuceparfum #qosmi"""))

L.append(("28-pdj-erba", "Le parfum du jour", "Erba Pura, Xerjoff", [("Erba Pura", "/parfum/xerjoff-erba-pura")], """Le parfum du jour : Erba Pura, de Xerjoff.

Un rayon de soleil italien en plein décembre : bergamote de Calabre, orange de Sicile et citron en ouverture, une corbeille de fruits méditerranéens au cœur, puis un fond doux d'ambre, de vanille de Madagascar et de musc blanc.

Son flacon turquoise ne passe pas inaperçu sous le sapin.

Disponible sur qosmi.be

#xerjoff #erbapura #parfumdeniche #parfumdujour #qosmi"""))

L.append(("29-mat-bergamote", "Carrousel · matière première", "La bergamote", [("Bergamote", "/matiere/bergamote"), ("Sauvage Parfum", "/parfum/sauvage-parfum"), ("Colonia", "/parfum/acqua-di-parma-colonia")], """La bergamote, c'est ce pétillant qu'on sent dans les premières secondes de beaucoup de parfums.

C'est un agrume, le fruit du bergamotier, entre l'orange amère et le citron. Elle pousse surtout en Calabre, tout au sud de l'Italie. Douce, acidulée, légèrement amère, elle donne de l'éclat à tout ce qu'elle touche.

On la trouve surtout en note de tête, des colognes aux parfums les plus chauds. En 1925, Shalimar a été l'un des premiers parfums à en utiliser autant.

À sentir : Dior Sauvage Parfum, où la bergamote rencontre la mandarine, et Acqua di Parma Colonia. Sur qosmi.be

#bergamote #matierepremiere #agrumes #calabre #qosmi"""))

L.append(("30-sel-derniere-minute", "Carrousel · spécial Noël", "3 cadeaux qui plaisent à tout le monde", [("Le Male", "/parfum/le-male"), ("Light Blue pour Homme", "/parfum/light-blue-pour-homme"), ("Aqua Universalis Cologne Forte", "/parfum/aqua-universalis-cologne-forte")], """Noël approche et toujours pas d'idée ? 3 parfums qui plaisent à presque tout le monde :

1. Jean Paul Gaultier Le Male : lavande, cannelle et vanille dans son célèbre flacon en buste. Un classique depuis 1995, signé Francis Kurkdjian.

2. Dolce&Gabbana Light Blue pour Homme : pamplemousse, genièvre et romarin. Frais et facile à porter.

3. Maison Francis Kurkdjian Aqua Universalis Cologne Forte : bergamote, pois de senteur et musc. Une odeur de propre, élégante, qui va à tout le monde.

Commande sur qosmi.be tant qu'il est temps.

#cadeaunoel #idéecadeau #lemale #lightblue #qosmi"""))


# Fiches Qosmi montrées dans chaque publication (titre exact) : le robot vérifie leur stock avant de publier.
T = {
 "1-parfum-du-jour": ["Parfums de Marly Delina — Eau de Parfum pour femme"],
 "2-carrousel-hiver": ["Tom Ford Private Blend Lost Cherry — Eau de Parfum mixte", "By Kilian The Liquors Angels' Share — Eau de Parfum mixte", "Tom Ford Black Orchid — Parfum mixte"],
 "4-matiere-oud": ["Tom Ford Private Blend Oud Wood — Eau de Parfum mixte"],
 "5-anniversaire-coco": ["Chanel Coco Mademoiselle — Eau de Parfum pour femme"],
 "06-pdj-jadore": ["Dior J'adore — Eau de Parfum pour femme"],
 "07-bio-kurkdjian": ["Jean Paul Gaultier Le Male — Eau de Toilette pour homme", "Maison Francis Kurkdjian Aqua Universalis Cologne Forte — Eau de Parfum mixte", "Maison Francis Kurkdjian Gentle Fluidity Gold — Eau de Parfum mixte"],
 "08-sel-noel-elle": ["Yves Saint Laurent Libre — Eau de Parfum pour femme", "Lancôme La Vie Est Belle — Eau de Parfum pour femme", "Viktor & Rolf Flowerbomb — Eau de Parfum pour femme"],
 "09-mat-vanille": ["Guerlain Shalimar — Eau de Parfum pour femme", "Lattafa Yara — Eau de Parfum pour femme"],
 "10-conseil-offrir": ["Dior J'adore — Eau de Parfum pour femme", "Chanel Bleu de Chanel — Eau de Parfum pour homme", "Lancôme La Vie Est Belle — Eau de Parfum pour femme"],
 "11-pdj-shalimar": ["Guerlain Shalimar — Eau de Parfum pour femme"],
 "12-sel-noel-lui": ["Chanel Bleu de Chanel — Eau de Parfum pour homme", "Dior Sauvage — Parfum pour homme", "Creed Aventus — Eau de Parfum pour homme"],
 "13-anniv-terre": ["Hermes Terre d´Hermès — Eau de Toilette pour homme"],
 "14-bio-bisch": ["Parfums de Marly Delina — Eau de Parfum pour femme", "Parfums de Marly Valaya — Eau de Parfum pour femme", "Carolina Herrera Very Good Girl — Eau de Parfum pour femme"],
 "15-conseil-concentrations": ["Jean Paul Gaultier Le Male — Eau de Toilette pour homme", "Dior J'adore — Eau de Parfum pour femme", "Nishane Hacivat — Extrait de Parfum mixte"],
 "16-pdj-9pm": ["Afnan 9pm — Eau de Parfum pour homme"],
 "17-mat-rose": ["Parfums de Marly Delina — Eau de Parfum pour femme", "Chanel Coco Mademoiselle — Eau de Parfum pour femme"],
 "18-sel-mixtes": ["Calvin Klein CK One — Eau de Toilette mixte", "Acqua di Parma Colonia — Eau de Cologne mixte", "Mancera Les Confidentiels Red Tobacco — Eau de Parfum mixte"],
 "19-pdj-hypnotic": ["Dior Hypnotic Poison — Eau de Parfum pour femme"],
 "20-bio-polge": ["Chanel Coco Mademoiselle — Eau de Parfum pour femme", "Chanel Bleu de Chanel — Eau de Parfum pour homme"],
 "21-conseil-tester": ["Xerjoff Erba Pura — Eau de Parfum mixte", "Nishane Hacivat — Extrait de Parfum mixte", "Maison Francis Kurkdjian Aqua Universalis Cologne Forte — Eau de Parfum mixte"],
 "22-sel-arabes": ["Lattafa Khamrah — Eau de Parfum mixte", "Lattafa Yara — Eau de Parfum pour femme", "Lattafa Asad — Eau de Parfum pour homme"],
 "23-mat-santal": ["Chanel Bleu de Chanel — Eau de Parfum pour homme", "Dior Hypnotic Poison — Eau de Parfum pour femme"],
 "24-pdj-hacivat": ["Nishane Hacivat — Extrait de Parfum mixte"],
 "25-anniv-goodgirl": ["Carolina Herrera Good Girl — Eau de Parfum pour femme"],
 "26-bio-morillas": ["Calvin Klein CK One — Eau de Toilette mixte", "Dolce&Gabbana Light Blue — Eau de Toilette pour homme"],
 "28-pdj-erba": ["Xerjoff Erba Pura — Eau de Parfum mixte"],
 "29-mat-bergamote": ["Dior Sauvage — Parfum pour homme", "Acqua di Parma Colonia — Eau de Cologne mixte"],
 "30-sel-derniere-minute": ["Jean Paul Gaultier Le Male — Eau de Toilette pour homme", "Dolce&Gabbana Light Blue — Eau de Toilette pour homme", "Maison Francis Kurkdjian Aqua Universalis Cologne Forte — Eau de Parfum mixte"],
}
PS = {p["title"]: p["handle"] for p in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "produits.json")))}

ICI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ICI, "page", "img")
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
d0 = dt.date(2026, 11, 16)
out = []
for k, (pid, typ, titre, src, txt) in enumerate(L):
    d = d0 + dt.timedelta(days=k)
    imgs = sorted([f[:-4] for f in os.listdir(IMG) if f.startswith(pid + "-") and f[len(pid) + 1:-4].isdigit()],
                  key=lambda x: int(x.rsplit("-", 1)[1]))
    out.append({"n": k + 1, "id": pid, "date": "%s %d %s" % (JOURS[d.weekday()], d.day, MOIS[d.month]), "iso": d.isoformat(),
                "sur": typ, "titre": titre, "img": imgs, "produits": [PS[t] for t in T.get(pid, [])], "src": [[a, O + b] for a, b in src], "txt": txt})
    assert imgs, pid
json.dump(out, open(os.path.join(ICI, "lot1.json"), "w"), ensure_ascii=False, indent=1)
print(len(out), "publications,", sum(len(p["img"]) for p in out), "visuels")
