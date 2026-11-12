#!/usr/bin/env python3
"""Lexique du parfum (/pages/lexique, NL : geurwoordenboek) — 13/11/2026, demande d'Amine (idée tirée du glossaire de Nose Paris,
textes Qosmi). Matières premières et mots du métier, FR + NL. Pas d'avis santé ni de note de « toxicité ».
Chaque matière renvoie vers la recherche par odeurs (/pages/odeurs?o=<odeur>) pour voir les parfums qui en contiennent.

  python3 scripts/page_lexique.py --section   # régénère theme_rk/sections/qk-lexique.liquid
  python3 scripts/page_lexique.py             # crée ou met à jour la page Shopify (modèle page.lexique)
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CAT = {"agrumes": ("Agrumes", "Citrus"), "fleurs": ("Fleurs", "Bloemen"), "epices": ("Épices", "Specerijen"),
       "bois": ("Bois", "Hout"), "gourmand": ("Gourmand", "Gourmand"), "ambre": ("Ambré, résines et muscs", "Amber, harsen en muskus"),
       "frais": ("Frais et aromatique", "Fris en aromatisch"), "metier": ("Mots du parfum", "Parfumtermen")}

# (catégorie, terme FR, terme NL, texte FR, texte NL, odeur liée ou None)
LEX = [
    ("agrumes", "Bergamote", "Bergamot",
     "Agrume cultivé surtout en Calabre, dans le sud de l'Italie. On presse son zeste pour en tirer une essence fraîche, un peu amère et florale. Elle ouvre une grande partie des parfums, des colognes aux boisés.",
     "Citrusvrucht die vooral in Calabrië (Zuid-Italië) groeit. Uit de schil perst men een frisse, licht bittere en bloemige olie. Ze opent heel veel parfums, van colognes tot houtgeuren.", "bergamote"),
    ("agrumes", "Citron", "Citroen",
     "Zeste vif et pétillant qui donne un effet de propreté immédiat. Très présent dans les eaux fraîches et les parfums d'été, il s'évapore vite et sert surtout de note de tête.",
     "Levendige, sprankelende schil die meteen een propere indruk geeft. Veel gebruikt in frisse geuren en zomerparfums. Hij vervliegt snel en is vooral een topnoot.", "citron"),
    ("agrumes", "Mandarine", "Mandarijn",
     "Plus douce et plus sucrée que l'orange, la mandarine apporte une fraîcheur juteuse et ronde. On la trouve aussi bien dans les parfums masculins que dans les floraux fruités.",
     "Zachter en zoeter dan sinaasappel. Mandarijn geeft een sappige, ronde frisheid en zit zowel in herenparfums als in fruitig-bloemige geuren.", "orange"),
    ("agrumes", "Pamplemousse", "Grapefruit",
     "Note acidulée et légèrement amère, très tonique. Elle donne du peps aux parfums frais et sportifs.",
     "Zurige, licht bittere en heel opwekkende noot. Geeft pit aan frisse en sportieve parfums.", "pamplemousse"),
    ("agrumes", "Néroli", "Neroli",
     "Essence tirée des fleurs du bigaradier (l'oranger amer). Fraîche, verte et lumineuse, elle est au cœur des eaux de Cologne classiques.",
     "Olie uit de bloesems van de bittere sinaasappelboom. Fris, groen en stralend: het hart van de klassieke eau de cologne.", "fleur_oranger"),
    ("fleurs", "Rose", "Roos",
     "La fleur la plus utilisée en parfumerie. Rose de Damas ou rose centifolia, elle peut être fraîche et poudrée, fruitée ou sombre et épicée selon ce qui l'accompagne. Associée à l'oud, elle forme un accord très apprécié au Moyen-Orient.",
     "De meest gebruikte bloem in de parfumerie. Damascusroos of centifolia: fris en poederig, fruitig of donker en kruidig, afhankelijk van wat ermee samengaat. Samen met oud vormt ze een akkoord dat in het Midden-Oosten erg geliefd is.", "rose"),
    ("fleurs", "Jasmin", "Jasmijn",
     "Fleur blanche riche et solaire, à la fois douce et un peu animale. Le jasmin grandiflorum et le jasmin sambac donnent du corps et de la sensualité à beaucoup de parfums féminins.",
     "Rijke, zonnige witte bloem, zoet en een tikje dierlijk. Jasmijn grandiflorum en sambac geven veel damesparfums body en sensualiteit.", "jasmin"),
    ("fleurs", "Fleur d'oranger", "Oranjebloesem",
     "Fleur blanche lumineuse, miellée et rassurante. Plus douce et plus florale que le néroli, issu du même arbre.",
     "Stralende witte bloem, honingachtig en geruststellend. Zachter en bloemiger dan neroli, dat van dezelfde boom komt.", "fleur_oranger"),
    ("fleurs", "Iris", "Iris",
     "On utilise la racine de l'iris, séchée pendant plusieurs années. Elle donne une odeur poudrée, élégante, qui rappelle le maquillage et la terre fraîche. C'est l'une des matières les plus chères.",
     "Men gebruikt de wortel van de iris, die jarenlang droogt. Die geeft een poederige, elegante geur die doet denken aan make-up en verse aarde. Een van de duurste grondstoffen.", "iris"),
    ("fleurs", "Tubéreuse", "Tuberoos",
     "Fleur blanche opulente, crémeuse et capiteuse. Elle signe les grands floraux intenses et se remarque de loin.",
     "Weelderige witte bloem, romig en bedwelmend. Ze tekent de grote, intense bloemengeuren en valt meteen op.", "tubereuse"),
    ("fleurs", "Ylang-ylang", "Ylang-ylang",
     "Fleur jaune des Comores et de Madagascar, solaire et crémeuse, avec une facette légèrement fruitée. Elle arrondit et réchauffe les bouquets floraux.",
     "Gele bloem uit de Comoren en Madagaskar, zonnig en romig met een licht fruitig kantje. Ze maakt bloemenboeketten ronder en warmer.", "ylang"),
    ("fleurs", "Muguet", "Lelietje-van-dalen",
     "Fleur printanière fraîche et verte. Impossible à extraire, son odeur est recréée par les parfumeurs à partir d'autres matières.",
     "Frisse, groene lentebloem. De geur is niet te extraheren en wordt door parfumeurs nagemaakt met andere grondstoffen.", "muguet"),
    ("fleurs", "Violette", "Viooltje",
     "Note poudrée et douce, parfois sucrée. La feuille de violette, elle, apporte une fraîcheur verte et légèrement aquatique.",
     "Poederige, zachte en soms zoete noot. Het blad van het viooltje geeft dan weer een groene, licht waterige frisheid.", "violette"),
    ("epices", "Safran", "Saffraan",
     "Épice précieuse au parfum cuiré, miellé et un peu métallique. Très présent dans les parfums orientaux et les accords avec l'oud.",
     "Kostbare specerij met een leerachtige, honingzoete en licht metalige geur. Veel gebruikt in oosterse parfums en samen met oud.", "safran"),
    ("epices", "Cardamome", "Kardemom",
     "Épice fraîche et aromatique, presque mentholée. Elle éclaire les parfums boisés et ambrés sans les alourdir.",
     "Frisse, aromatische specerij, bijna muntachtig. Ze geeft houtige en amberige parfums licht zonder ze zwaar te maken.", "cardamome"),
    ("epices", "Cannelle", "Kaneel",
     "Épice chaude et sucrée, qui évoque la pâtisserie et les fêtes de fin d'année. On la retrouve dans beaucoup de parfums d'hiver.",
     "Warme, zoete specerij die doet denken aan gebak en de feestdagen. Vaak in winterparfums.", "cannelle"),
    ("epices", "Poivre", "Peper",
     "Poivre noir, poivre rose ou baies roses : une note piquante et pétillante qui donne du relief dès l'ouverture.",
     "Zwarte peper, roze peper of roze bessen: een pikante, sprankelende noot die meteen reliëf geeft.", "poivre"),
    ("epices", "Gingembre", "Gember",
     "Note épicée, fraîche et un peu citronnée. Elle apporte de l'énergie aux parfums frais comme aux boisés.",
     "Kruidige, frisse en licht citroenachtige noot. Ze geeft energie aan frisse parfums en houtgeuren.", "gingembre"),
    ("bois", "Oud", "Oud",
     "Aussi appelé bois d'agar. Résine qui se forme dans le cœur de l'aquilaria quand l'arbre est infecté. Son odeur est profonde, boisée, cuirée et parfois animale. Très précieuse, elle est souvent reconstituée en partie en parfumerie.",
     "Ook agarhout genoemd. Een hars die ontstaat in de kern van de aquilariaboom wanneer die geïnfecteerd raakt. De geur is diep, houtig, leerachtig en soms dierlijk. Erg kostbaar en in parfums vaak deels nagemaakt.", "oud"),
    ("bois", "Santal", "Sandelhout",
     "Bois crémeux, doux et lacté, originaire d'Inde ou d'Australie. Il donne une base chaude et enveloppante.",
     "Romig, zacht en melkachtig hout uit India of Australië. Het geeft een warme, omhullende basis.", "santal"),
    ("bois", "Cèdre", "Ceder",
     "Bois sec et net, qui évoque le crayon taillé. Il structure le fond de nombreux parfums masculins et mixtes.",
     "Droog, zuiver hout dat doet denken aan een geslepen potlood. Het geeft structuur aan de basis van veel heren- en unisexparfums.", "cedre"),
    ("bois", "Vétiver", "Vetiver",
     "Racine d'une herbe tropicale, surtout cultivée à Haïti et à Java. Son odeur est boisée, terreuse et parfois fumée. Elle donne une élégance sèche.",
     "Wortel van een tropisch gras, vooral geteeld in Haïti en op Java. De geur is houtig, aards en soms rokerig, met een droge elegantie.", "vetiver"),
    ("bois", "Patchouli", "Patchoeli",
     "Feuilles d'une plante d'Asie, séchées puis distillées. Note boisée, terreuse et un peu camphrée, indispensable aux chyprés et à beaucoup de parfums modernes.",
     "Bladeren van een Aziatische plant, gedroogd en gedistilleerd. Houtige, aardse en licht kamferachtige noot, onmisbaar in chypres en veel moderne parfums.", "patchouli"),
    ("bois", "Mousse de chêne", "Eikenmos",
     "Lichen qui pousse sur les chênes. Odeur humide, boisée et un peu salée : c'est la signature des parfums chyprés. Son usage est aujourd'hui encadré, les parfumeurs l'adaptent ou la recréent.",
     "Korstmos dat op eiken groeit. Vochtige, houtige en licht zilte geur: het handelsmerk van chypreparfums. Het gebruik is vandaag gereglementeerd, parfumeurs passen het aan of maken het na.", "mousse"),
    ("gourmand", "Vanille", "Vanille",
     "Gousse d'une orchidée, surtout de Madagascar. Douce, chaude et réconfortante, la vanille arrondit les parfums et les rend plus sensuels.",
     "Peul van een orchidee, vooral uit Madagaskar. Zacht, warm en troostend: vanille maakt parfums ronder en sensueler.", "vanille"),
    ("gourmand", "Fève tonka", "Tonkaboon",
     "Graine d'Amérique du Sud aux notes d'amande, de foin et de caramel. Elle donne un fond chaud et légèrement gourmand.",
     "Zaad uit Zuid-Amerika met tonen van amandel, hooi en karamel. Het geeft een warme, licht gourmande basis.", "tonka"),
    ("gourmand", "Praline", "Praliné",
     "Accord gourmand de noisettes ou d'amandes caramélisées. Il donne aux parfums un côté sucré et addictif.",
     "Gourmand akkoord van gekaramelliseerde hazelnoten of amandelen. Het geeft parfums een zoet, verslavend kantje.", "caramel"),
    ("gourmand", "Café", "Koffie",
     "Note torréfiée et un peu amère qui réveille les accords vanillés et boisés. Très utilisée dans les parfums de soirée.",
     "Geroosterde, licht bittere noot die vanille- en houtakkoorden wakker maakt. Veel gebruikt in avondparfums.", "cafe"),
    ("ambre", "Ambre", "Amber",
     "En parfumerie, l'ambre n'est pas la pierre : c'est un accord chaud, doux et résineux, souvent fait de vanille, de benjoin et de labdanum. C'est la base des parfums dits orientaux ou ambrés.",
     "In de parfumerie is amber niet de steen: het is een warm, zacht en harsachtig akkoord, vaak met vanille, benzoë en labdanum. Het vormt de basis van oosterse of amberparfums.", "ambre"),
    ("ambre", "Ambre gris et ambroxan", "Ambergris en ambroxan",
     "L'ambre gris est une matière rare d'origine marine, à l'odeur salée, minérale et douce. Aujourd'hui, on utilise surtout des molécules qui la reproduisent, comme l'ambroxan, qui donne cet effet boisé, lumineux et très persistant.",
     "Ambergris is een zeldzame grondstof uit de zee, met een zilte, minerale en zachte geur. Vandaag gebruikt men vooral moleculen die het nabootsen, zoals ambroxan, met een houtig, stralend en heel blijvend effect.", "ambre_gris"),
    ("ambre", "Encens", "Wierook",
     "Résine d'oliban, brûlée depuis l'Antiquité. Son odeur est fumée, citronnée et un peu mystique.",
     "Hars van de olibanumboom, al sinds de oudheid gebrand. De geur is rokerig, citroenachtig en een beetje mystiek.", "encens"),
    ("ambre", "Benjoin et labdanum", "Benzoë en labdanum",
     "Deux résines chaudes. Le benjoin est doux et vanillé ; le labdanum, tiré du ciste, est plus sombre, cuiré et ambré.",
     "Twee warme harsen. Benzoë is zacht en vanilleachtig; labdanum, uit de cistusroos, is donkerder, leerachtig en amberig.", "baumes"),
    ("ambre", "Musc", "Muskus",
     "Aujourd'hui toujours synthétique, le musc donne un effet de peau propre, doux et enveloppant. Il fixe le parfum et prolonge sa tenue.",
     "Muskus is vandaag altijd synthetisch. Hij geeft een effect van propere, zachte huid en laat het parfum langer blijven.", "musc"),
    ("ambre", "Cuir", "Leer",
     "Accord qui évoque le cuir tanné, souvent créé avec du bouleau, du safran ou des notes fumées. Il apporte du caractère.",
     "Akkoord dat doet denken aan gelooid leer, vaak gemaakt met berk, saffraan of rokerige noten. Het geeft karakter.", "cuir"),
    ("ambre", "Tabac", "Tabak",
     "Feuilles de tabac séchées, au parfum miellé, boisé et légèrement fumé. Une note chaude, très présente dans les parfums d'hiver.",
     "Gedroogde tabaksbladeren met een honingachtige, houtige en licht rokerige geur. Een warme noot, vaak in winterparfums.", "tabac"),
    ("frais", "Lavande", "Lavendel",
     "Plante de Provence, à la fois fraîche, aromatique et douce. Elle est à la base des fougères, la famille des parfums masculins classiques.",
     "Plant uit de Provence, fris, aromatisch en zacht tegelijk. De basis van de fougères, de familie van de klassieke herenparfums.", "lavande"),
    ("frais", "Menthe", "Munt",
     "Note fraîche et vive, qui donne une sensation de froid. Elle réveille les parfums d'été.",
     "Frisse, levendige noot die een koel gevoel geeft. Ze maakt zomerparfums wakker.", "menthe"),
    ("frais", "Notes marines", "Zeenoten",
     "Accords qui évoquent l'air de la mer, le sel et l'eau. On parle aussi de notes aquatiques. Elles ont marqué les parfums frais à partir des années 1990.",
     "Akkoorden die doen denken aan zeelucht, zout en water. Men spreekt ook van aquatische noten. Ze typeren frisse parfums sinds de jaren 1990.", "marin"),
    ("frais", "Thé", "Thee",
     "Thé vert, noir ou matcha : une note transparente, légèrement amère, qui apporte calme et fraîcheur.",
     "Groene, zwarte of matchathee: een transparante, licht bittere noot die rust en frisheid brengt.", "the"),
    # mots du métier
    ("metier", "Notes de tête, de cœur et de fond", "Top-, hart- en basisnoten",
     "Les trois temps d'un parfum. Les notes de tête se sentent tout de suite et partent en quelques minutes. Les notes de cœur forment le caractère du parfum. Les notes de fond, plus lourdes, restent des heures sur la peau.",
     "De drie fases van een parfum. Topnoten ruik je meteen en ze verdwijnen na enkele minuten. Hartnoten bepalen het karakter. Basisnoten zijn zwaarder en blijven uren op de huid.", None),
    ("metier", "Pyramide olfactive", "Geurpiramide",
     "La manière de présenter les notes d'un parfum en trois étages : tête, cœur et fond.",
     "De manier om de noten van een parfum in drie lagen voor te stellen: top, hart en basis.", None),
    ("metier", "Accord", "Akkoord",
     "Mélange de plusieurs matières qui crée une odeur nouvelle, comme un accord de musique. Par exemple, l'accord ambré ou l'accord cuir.",
     "Mengsel van meerdere grondstoffen dat een nieuwe geur vormt, zoals een akkoord in de muziek. Bijvoorbeeld het amberakkoord of het leerakkoord.", None),
    ("metier", "Famille olfactive", "Geurfamilie",
     "Manière de classer les parfums selon leur odeur dominante : hespéridé (agrumes), floral, fougère, chypré, boisé, ambré (oriental), cuir, gourmand…",
     "Manier om parfums in te delen volgens hun belangrijkste geur: citrus, bloemig, fougère, chypre, houtig, amber (oosters), leer, gourmand…", None),
    ("metier", "Chypré", "Chypre",
     "Famille construite sur le contraste entre la bergamote en tête et la mousse de chêne, le patchouli et le labdanum en fond.",
     "Familie gebouwd op het contrast tussen bergamot in de top en eikenmos, patchoeli en labdanum in de basis.", None),
    ("metier", "Fougère", "Fougère",
     "Famille née à la fin du XIXe siècle : lavande, géranium, mousse de chêne et coumarine (l'odeur de la fève tonka). C'est le grand classique des parfums masculins.",
     "Familie uit het einde van de 19e eeuw: lavendel, geranium, eikenmos en coumarine (de geur van de tonkaboon). De grote klassieker bij herenparfums.", None),
    ("metier", "Gourmand", "Gourmand",
     "Parfum aux notes qui se mangent : vanille, caramel, chocolat, café, praliné… Une famille très populaire depuis les années 1990.",
     "Parfum met eetbare noten: vanille, karamel, chocolade, koffie, praliné… Een erg populaire familie sinds de jaren 1990.", None),
    ("metier", "Eau de toilette, eau de parfum, extrait", "Eau de toilette, eau de parfum, extrait",
     "La concentration en essences. En général, une eau de toilette est plus légère, une eau de parfum plus concentrée, un parfum ou extrait encore plus. La tenue dépend aussi de la composition et de la peau.",
     "De concentratie aan geurstoffen. Meestal is een eau de toilette lichter, een eau de parfum geconcentreerder en een parfum of extrait nog meer. Hoe lang een geur blijft, hangt ook af van de samenstelling en de huid.", None),
    ("metier", "Tenue", "Houdbaarheid",
     "Le temps pendant lequel on sent le parfum sur la peau après l'avoir vaporisé.",
     "Hoe lang je het parfum op je huid ruikt nadat je het gesprayd hebt.", None),
    ("metier", "Sillage", "Sillage",
     "La trace odorante que le parfum laisse autour de soi quand on bouge. Un sillage fort se remarque de loin, un sillage discret reste proche de la peau.",
     "Het geurspoor dat een parfum achterlaat als je beweegt. Een sterke sillage valt van ver op, een subtiele blijft dicht bij de huid.", None),
    ("metier", "Flanker", "Flanker",
     "Variante d'un parfum existant, qui garde son nom en l'adaptant : version Intense, Parfum, Eau Fraîche, édition d'été…",
     "Variant van een bestaand parfum dat de naam behoudt maar aanpast: Intense, Parfum, Eau Fraîche, zomereditie…", None),
    ("metier", "Parfum de niche", "Nicheparfum",
     "Parfum créé par une maison spécialisée, souvent indépendante, qui privilégie la création et les matières plutôt que la grande distribution.",
     "Parfum van een gespecialiseerd, vaak onafhankelijk huis, dat creativiteit en grondstoffen belangrijker vindt dan massadistributie.", None),
    ("metier", "Nez", "Neus",
     "Le surnom du parfumeur créateur, celui qui compose la formule d'un parfum.",
     "De bijnaam van de parfumeur, degene die de formule van een parfum samenstelt.", None),
    ("metier", "Macération", "Maceratie",
     "Temps de repos du parfum après le mélange, avant la mise en flacon, pour que les matières se fondent entre elles.",
     "De rusttijd van het parfum na het mengen en vóór het bottelen, zodat de grondstoffen goed samensmelten.", None),
    ("metier", "Mouillette", "Geurstrip",
     "Fine bande de papier buvard sur laquelle on vaporise un parfum pour le sentir sans le porter.",
     "Dun strookje vloeipapier waarop je een parfum spuit om het te ruiken zonder het te dragen.", None),
]


def section():
    import html as H
    def bloc(nl):
        out = []
        ordre = list(CAT)
        for c in ordre:
            items = sorted([x for x in LEX if x[0] == c], key=lambda x: x[2 if nl else 1].lower())
            out.append('<h2 class="qk-lex__cat" id="%s">%s</h2>' % (c, CAT[c][1 if nl else 0]))
            for _, t_fr, t_nl, x_fr, x_nl, odeur in items:
                t, x = (t_nl, x_nl) if nl else (t_fr, x_fr)
                lien = ""
                if odeur:
                    lien = '<a class="qk-lex__lien" href="{{ routes.root_url | append: \'/pages/odeurs?o=%s\' | replace: \'//\', \'/\' }}">%s</a>' % (
                        odeur, "Parfums met deze noot" if nl else "Parfums qui en contiennent")
                out.append('<div class="qk-lex__item"><h3>%s</h3><p>%s</p>%s</div>' % (H.escape(t), H.escape(x), lien))
        return "\n".join(out)

    def nav(nl):
        return "".join('<a href="#%s">%s</a>' % (c, CAT[c][1 if nl else 0]) for c in CAT)

    def ld(nl):
        return json.dumps({"@context": "https://schema.org", "@type": "DefinedTermSet",
                           "name": "Geurwoordenboek Qosmi" if nl else "Lexique du parfum Qosmi",
                           "hasDefinedTerm": [{"@type": "DefinedTerm", "name": x[2 if nl else 1], "description": x[4 if nl else 3]} for x in LEX]},
                          ensure_ascii=False)

    liq = """{%- comment -%} Généré par scripts/page_lexique.py : ne pas modifier à la main. Lexique Qosmi (13/11/2026). {%- endcomment -%}
{%- assign qk_nl = false -%}{%- if request.locale.iso_code == 'nl' -%}{%- assign qk_nl = true -%}{%- endif -%}
<section class="qk-section qk-lex">
  <div class="qk-largeur qk-lex__largeur">
    <img class="qk-faq__image" src="{{ 'qosmi-matieres-premieres.jpg' | file_url }}" alt="" width="2400" height="1340" loading="eager">
    <h1 class="qk-titre-section">{% if qk_nl %}Geurwoordenboek{% else %}Lexique du parfum{% endif %}</h1>
    <p class="qk-faq__intro">{% if qk_nl %}De belangrijkste grondstoffen en woorden uit de parfumwereld, kort uitgelegd. Klik op ‘Parfums met deze noot’ om ze in onze collectie te vinden.{% else %}Les grandes matières premières et les mots du parfum, expliqués simplement. Clique sur « Parfums qui en contiennent » pour les retrouver dans notre catalogue.{% endif %}</p>
    <nav class="qk-lex__nav">{% if qk_nl %}NAV_NL{% else %}NAV_FR{% endif %}</nav>
    <input class="qk-faq__recherche" type="search" data-qk-lex-recherche placeholder="{% if qk_nl %}Zoek een woord…{% else %}Rechercher un mot…{% endif %}" aria-label="{% if qk_nl %}Zoek een woord{% else %}Rechercher un mot{% endif %}">
    <div class="qk-lex__liste">
      {%- if qk_nl -%}
BLOC_NL
      {%- else -%}
BLOC_FR
      {%- endif -%}
    </div>
  </div>
  {%- if qk_nl -%}<script type="application/ld+json">LD_NL</script>{%- else -%}<script type="application/ld+json">LD_FR</script>{%- endif -%}
  <script>
    (function () {
      var c = document.querySelector('[data-qk-lex-recherche]');
      if (!c) return;
      var norm = function (s) { return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase(); };
      c.addEventListener('input', function () {
        var q = norm(c.value.trim());
        document.querySelectorAll('.qk-lex__item').forEach(function (d) { d.hidden = q && norm(d.textContent).indexOf(q) < 0; });
        document.querySelectorAll('.qk-lex__cat').forEach(function (h) {
          var e = h.nextElementSibling, vis = false;
          while (e && !e.classList.contains('qk-lex__cat')) { if (!e.hidden) vis = true; e = e.nextElementSibling; }
          h.hidden = !vis;
        });
      });
    })();
  </script>
</section>
{% schema %}
{ "name": "Qosmi · Lexique", "tag": "div", "settings": [] }
{% endschema %}
"""
    liq = (liq.replace("BLOC_NL", bloc(True)).replace("BLOC_FR", bloc(False)).replace("NAV_NL", nav(True)).replace("NAV_FR", nav(False))
              .replace("LD_NL", ld(True)).replace("LD_FR", ld(False)))
    for m in ("soleluna", "marge", "margin", "toxi"):
        if m in liq.lower():
            raise SystemExit("Contrôle : « %s » dans le lexique" % m)
    open(os.path.join(RACINE, "theme_rk", "sections", "qk-lexique.liquid"), "w", encoding="utf-8").write(liq)
    open(os.path.join(RACINE, "theme_rk", "templates", "page.lexique.json"), "w", encoding="utf-8").write(
        json.dumps({"sections": {"main": {"type": "qk-lexique", "settings": {}}}, "order": ["main"]}, indent=2) + "\n")
    print("Section qk-lexique : %d entrées" % len(LEX))


def page():
    from shopify_api import Shopify
    s = Shopify()
    champs = {"title": "Lexique du parfum", "handle": "lexique", "body": "", "isPublished": True, "templateSuffix": "lexique"}
    d = s.gql('query($q: String!) { pages(first: 1, query: $q) { nodes { id } } }', {"q": "handle:lexique"})["pages"]["nodes"]
    if d:
        r = s.gql("mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id } userErrors { field message } } }",
                  {"id": d[0]["id"], "p": champs})["pageUpdate"]
    else:
        r = s.gql("mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id } userErrors { field message } } }", {"p": champs})["pageCreate"]
    if r["userErrors"]:
        sys.exit("Refus : %s" % json.dumps(r["userErrors"], ensure_ascii=False))
    pid = r["page"]["id"]
    tr = s.gql("query($id: ID!) { translatableResource(resourceId: $id) { translatableContent { key digest } } }", {"id": pid})
    dig = {x["key"]: x["digest"] for x in (tr["translatableResource"] or {}).get("translatableContent", [])}
    t = [{"locale": "nl", "key": k, "value": v, "translatableContentDigest": dig[k]}
         for k, v in (("title", "Geurwoordenboek"), ("handle", "geurwoordenboek")) if k in dig]
    e = s.gql("""mutation($id: ID!, $t: [TranslationInput!]!) { translationsRegister(resourceId: $id, translations: $t) { userErrors { message } } }""",
              {"id": pid, "t": t})["translationsRegister"]["userErrors"]
    print("Page Lexique OK :", pid, "NL :", e or "ok")


if __name__ == "__main__":
    section() if "--section" in sys.argv else page()
