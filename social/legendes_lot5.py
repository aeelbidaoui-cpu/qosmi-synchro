#!/usr/bin/env python3
"""Qosmi — lot n°5 « Tendances » (28 publications, 06/03 → 02/04/2027), demandé par Amine le 18/11/2026.

Base : les classements publics de Fragrance Index (fragranceindex.ai, accord obtenu par Amine le 13/11/2026),
relevés le 18/11/2026 (semaine du 10 au 16 novembre 2026) :
  - « Social Hype Score » : les 100 parfums dont les créateurs parlent le plus (rang noté « shs ») ;
  - « Top Movers » : les parfums dont les mentions montent le plus vite (« +x % » sur la semaine) ;
  - « What America is searching » : recherches en hausse (pistache +50 %).
Seuls les parfums vendus sur qosmi.be sont repris. Notes : config/profils_parfums.json (Fragrance Index / Fragrantica).
Un jour en néerlandais, le lendemain en français (le lot n°1 finit en français le 05/03).

  python3 social/legendes_lot5.py   → écrit social/lot5/lot5.json (les visuels : social/visuels_lot5.py)
"""
import datetime as dt, json, os

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
PROFILS = json.load(open(os.path.join(RACINE, "config", "profils_parfums.json"), encoding="utf-8"))["parfums"]

SOURCE_FR = "Source : Fragrance Index, classements de novembre 2026."
SOURCE_NL = "Bron: Fragrance Index, rankings van november 2026."
TAGS_FR = "#parfum #tendanceparfum #fragranceindex #parfumtiktok #qosmi"
TAGS_NL = "#parfum #parfumtrend #fragranceindex #parfumtok #qosmi"

# ------------------------------------------------------------------ les parfums
# handle, marque, nom affiché, année, signal Fragrance Index (fr, nl)
P = {
    "aventus": ("creed-aventus-eau-de-parfum-pour-homme", "Creed", "Aventus"),
    "hawas-ice": ("rasasi-hawas-ice-eau-de-parfum-pour-homme", "Rasasi", "Hawas Ice"),
    "dhi": ("dior-homme-intense-2025-eau-de-parfum-pour-homme", "Dior", "Dior Homme Intense"),
    "bdc-parfum": ("chanel-bleu-de-chanel-parfum-pour-homme", "Chanel", "Bleu de Chanel Parfum"),
    "sauvage-elixir": ("dior-sauvage-elixir-parfum-pour-homme", "Dior", "Sauvage Elixir"),
    "layton": ("parfums-de-marly-layton-eau-de-parfum-mixte", "Parfums de Marly", "Layton"),
    "khamrah": ("lattafa-khamrah-eau-de-parfum-mixte", "Lattafa", "Khamrah"),
    "naxos": ("xerjoff-xj-1861-naxos-eau-de-parfum-mixte", "Xerjoff", "Naxos"),
    "asad": ("lattafa-asad-eau-de-parfum-pour-homme", "Lattafa", "Asad"),
    "asad-elixir": ("lattafa-asad-elixir-eau-de-parfum-pour-homme", "Lattafa", "Asad Elixir"),
    "asad-bourbon": ("lattafa-asad-bourbon-eau-de-parfum-pour-homme", "Lattafa", "Asad Bourbon"),
    "khamrah-qahwa": ("lattafa-khamrah-qahwa-eau-de-parfum-mixte", "Lattafa", "Khamrah Qahwa"),
    "9pm-night-out": ("afnan-9pm-night-out-extrait-de-parfum-mixte", "Afnan", "9pm Night Out"),
    "supremacy": ("afnan-supremacy-collector-s-edition-eau-de-parfum-pour-homme", "Afnan", "Supremacy Collector's Edition"),
    "br540": ("maison-francis-kurkdjian-baccarat-rouge-540-eau-de-parfum-mixte", "Maison Francis Kurkdjian", "Baccarat Rouge 540"),
    "le-male-elixir": ("jean-paul-gaultier-le-male-elixir-parfum-pour-homme", "Jean Paul Gaultier", "Le Male Elixir"),
    "angham": ("lattafa-angham-eau-de-parfum-mixte", "Lattafa", "Angham"),
    "khair": ("paris-corner-khair-pistachio-eau-de-parfum-mixte", "Paris Corner", "Khair Pistachio"),
    "eclaire": ("lattafa-eclaire-pistache-eau-de-parfum-mixte", "Lattafa", "Éclaire Pistache"),
    "pistachio-cousin": ("liquides-imaginaires-pistachio-cousin-eau-de-parfum-mixte", "Liquides Imaginaires", "Pistachio Cousin"),
    "pistachio-kunafa": ("anfar-1950-pistachio-kunafa-extrait-de-parfum-mixte", "Anfar 1950", "Pistachio Kunafa"),
    "ombre-leather": ("tom-ford-ombre-leather-parfum-mixte", "Tom Ford", "Ombré Leather Parfum"),
    "vibrato": ("sospiro-vibrato-eau-de-parfum-mixte", "Sospiro", "Vibrato"),
    "bdc-edp": ("chanel-bleu-de-chanel-eau-de-parfum-pour-homme", "Chanel", "Bleu de Chanel"),
    "git": ("creed-green-irish-tweed-eau-de-parfum-pour-homme", "Creed", "Green Irish Tweed"),
    "cdn-man": ("armaf-club-de-nuit-intense-man-eau-de-parfum-pour-homme", "Armaf", "Club de Nuit Intense Man"),
    "eros-flame": ("versace-eros-flame-eau-de-parfum-pour-homme-2", "Versace", "Eros Flame"),
    "good-girl": ("carolina-herrera-good-girl-eau-de-parfum-pour-femme", "Carolina Herrera", "Good Girl"),
    "liquid-brun": ("french-avenue-sweet-pleasure-collection-liquid-brun-eau-de-parfum-pour-homme", "French Avenue", "Liquid Brun"),
    "noir-extreme": ("tom-ford-noir-extreme-parfum-pour-homme", "Tom Ford", "Noir Extreme Parfum"),
    "erba-pura": ("xerjoff-erba-pura-eau-de-parfum-mixte", "Xerjoff", "Erba Pura"),
    "vulcan-feu": ("french-avenue-vulcan-feu-extrait-de-parfum-mixte", "French Avenue", "Vulcan Feu"),
    "hawas-black": ("rasasi-hawas-black-eau-de-parfum-pour-homme", "Rasasi", "Hawas Black"),
    "hawas-kobra": ("rasasi-hawas-kobra-eau-de-parfum-pour-homme", "Rasasi", "Hawas Kobra"),
    "eros-energy": ("versace-eros-energy-eau-de-parfum-pour-homme", "Versace", "Eros Energy"),
    "cdn-bling": ("armaf-club-de-nuit-bling-eau-de-parfum-mixte", "Armaf", "Club de Nuit Bling"),
    "dior-homme": ("dior-homme-2020-eau-de-toilette-pour-homme", "Dior", "Dior Homme"),
}

# signal Fragrance Index affiché sur le visuel : (fr, nl)
SIG = {
    "aventus": ("N°1 du classement", "Nr. 1 in de ranking"),
    "hawas-ice": ("N°4 du classement", "Nr. 4 in de ranking"),
    "dhi": ("N°7 du classement", "Nr. 7 in de ranking"),
    "bdc-parfum": ("N°8 du classement", "Nr. 8 in de ranking"),
    "sauvage-elixir": ("N°10 du classement", "Nr. 10 in de ranking"),
    "liquid-brun": ("N°11 du classement", "Nr. 11 in de ranking"),
    "naxos": ("+167 % en une semaine", "+167 % in één week"),
    "layton": ("N°13 du classement", "Nr. 13 in de ranking"),
    "vibrato": ("N°14 du classement", "Nr. 14 in de ranking"),
    "bdc-edp": ("N°15 du classement", "Nr. 15 in de ranking"),
    "cdn-man": ("N°19 du classement", "Nr. 19 in de ranking"),
    "le-male-elixir": ("N°20 du classement", "Nr. 20 in de ranking"),
    "khamrah": ("N°21 du classement", "Nr. 21 in de ranking"),
    "asad": ("N°25 du classement", "Nr. 25 in de ranking"),
    "khamrah-qahwa": ("N°39 du classement", "Nr. 39 in de ranking"),
    "eros-flame": ("N°41 du classement", "Nr. 41 in de ranking"),
    "supremacy": ("+150 % en une semaine", "+150 % in één week"),
    "ombre-leather": ("N°46 du classement", "Nr. 46 in de ranking"),
    "br540": ("N°47 du classement", "Nr. 47 in de ranking"),
    "9pm-night-out": ("N°51 du classement", "Nr. 51 in de ranking"),
    "asad-bourbon": ("N°54 du classement", "Nr. 54 in de ranking"),
    "noir-extreme": ("N°62 du classement", "Nr. 62 in de ranking"),
    "asad-elixir": ("En forte hausse", "Sterk in opmars"),
    "hawas-kobra": ("N°76 du classement", "Nr. 76 in de ranking"),
    "erba-pura": ("N°78 du classement", "Nr. 78 in de ranking"),
    "git": ("N°88 du classement", "Nr. 88 in de ranking"),
    "eros-energy": ("N°86 du classement", "Nr. 86 in de ranking"),
    "vulcan-feu": ("N°93 du classement", "Nr. 93 in de ranking"),
    "hawas-black": ("N°100 du classement", "Nr. 100 in de ranking"),
    "angham": ("+500 %, en pleine montée", "+500 %, sterk in opmars"),
    "good-girl": ("En pleine montée", "Sterk in opmars"),
    "dior-homme": ("En pleine montée", "Sterk in opmars"),
    "cdn-bling": ("En pleine montée", "Sterk in opmars"),
    "khair": ("", ""), "eclaire": ("", ""), "pistachio-cousin": ("", ""), "pistachio-kunafa": ("", ""),
}

CONC = [("extrait-de-parfum", "Extrait de parfum"), ("eau-de-parfum", "Eau de parfum"), ("eau-de-toilette", "Eau de toilette"),
        ("eau-de-cologne", "Eau de cologne"), ("-parfum-", "Parfum")]


def concentration(h):
    return next((v for k, v in CONC if k in h), "")


def notes(cle, nl=False, n=4):
    """Les notes marquantes : la 1re de tête, les 2 premières de cœur, la 1re de fond (profil Qosmi)."""
    p = PROFILS.get(P[cle][0]) or {}
    d = p.get("nn" if nl else "nf") or {}
    l = (d.get("t") or [])[:1] + (d.get("c") or [])[:2] + (d.get("f") or [])[:1]
    l = [x.strip() for x in l if x.strip()][:n]
    if not l:
        return ""
    l = [l[0][:1].upper() + l[0][1:]] + [x[:1].lower() + x[1:] if not x.isupper() else x for x in l[1:]]
    return ", ".join(l)


def annee(cle):
    return (PROFILS.get(P[cle][0]) or {}).get("a")


def parfumeurs(cle):
    return (PROFILS.get(P[cle][0]) or {}).get("pf") or []


# ------------------------------------------------------------------ le calendrier
# type : "pdj" (un parfum), "sel" (carrousel de parfums), "conseil" (carrousel de texte)
L = []


def pub(cle_id, type_, langue, titre, titre_nl, txt, txt_nl, **k):
    L.append(dict(id="l5-%02d-%s" % (len(L) + 1, cle_id), type=type_, langue=langue, titre=titre, titre_nl=titre_nl,
                  txt=txt, txt_nl=txt_nl, **k))


pub("buzz", "sel", "nl", "Les 5 parfums dont tout le monde parle", "De 5 parfums waar iedereen over praat",
    "Aventus, Hawas Ice, Dior Homme Intense, Bleu de Chanel Parfum, Sauvage Elixir : voici le haut du classement des parfums "
    "dont les créateurs de contenu parlent le plus.\n\nLe « Social Hype Score » de Fragrance Index mesure combien et combien "
    "longtemps un parfum est cité dans les vidéos. Ces cinq-là ne quittent pas le sommet.\n\nTon préféré, c'est lequel ? 👇\n\n" + SOURCE_FR,
    "Aventus, Hawas Ice, Dior Homme Intense, Bleu de Chanel Parfum, Sauvage Elixir: dit is de top van de parfums waar "
    "contentcreators het meest over praten.\n\nDe « Social Hype Score » van Fragrance Index meet hoe vaak en hoe lang een parfum "
    "in video's genoemd wordt. Deze vijf blijven bovenaan staan.\n\nWelke is jouw favoriet? 👇\n\n" + SOURCE_NL,
    parfums=["aventus", "hawas-ice", "dhi", "bdc-parfum", "sauvage-elixir"],
    couv=("Les 5 parfums<br>dont tout le<br>monde parle", "De 5 parfums<br>waar iedereen<br>over praat"))

pub("layton", "pdj", "fr", "Layton, Parfums de Marly", "Layton, Parfums de Marly",
    "Layton fait partie des parfums les plus cités par les créateurs, et il continue de monter (+29 % de mentions en une semaine).\n\n"
    "Pomme et cardamome en ouverture, lavande et géranium au cœur, puis un fond vanillé, praliné et boisé. "
    "Un parfum chaleureux qui se porte très bien quand il fait frais.\n\n" + SOURCE_FR,
    "Layton hoort bij de parfums die creators het vaakst noemen, en hij blijft stijgen (+29 % vermeldingen in één week).\n\n"
    "Appel en kardemom in de opening, lavendel en geranium in het hart, dan een basis van vanille, praliné en hout. "
    "Een warme geur die perfect is als het fris is.\n\n" + SOURCE_NL, parfums=["layton"])

pub("khamrah", "pdj", "nl", "Khamrah, Lattafa", "Khamrah, Lattafa",
    "Khamrah est l'un des orientaux les plus en vue du moment : cannelle et muscade, dattes et praliné, puis un fond de vanille, "
    "de fève tonka et de bois ambrés.\n\nUn gourmand épicé, rond et généreux, pour les soirées d'hiver.\n\n" + SOURCE_FR,
    "Khamrah is een van de oosterse parfums waar het meest over gepraat wordt: kaneel en nootmuskaat, dadels en praliné, dan een "
    "basis van vanille, tonkaboon en amberhout.\n\nEen kruidige gourmand, rond en royaal, voor winteravonden.\n\n" + SOURCE_NL,
    parfums=["khamrah"])

pub("conseil-tendance", "conseil", "fr", "Un parfum « tendance », c'est quoi ?", "Wat is een « trending » parfum?",
    "Tu vois passer les mêmes flacons sur TikTok et YouTube ? Ce n'est pas un hasard.\n\nFragrance Index suit chaque jour ce que "
    "disent les créateurs de contenu et en tire deux classements : les parfums dont on parle le plus, et ceux qui montent le plus vite.\n\n"
    "Glisse pour comprendre comment ça marche 👉\n\n" + SOURCE_FR,
    "Zie je steeds dezelfde flacons op TikTok en YouTube? Dat is geen toeval.\n\nFragrance Index volgt elke dag wat contentcreators "
    "zeggen en maakt er twee rankings van: de parfums waar het meest over gepraat wordt, en die het snelst stijgen.\n\n"
    "Swipe om te zien hoe het werkt 👉\n\n" + SOURCE_NL,
    couv=("Un parfum<br>« tendance »,<br>c'est quoi ?", "Wat is een<br>« trending »<br>parfum?"),
    slides=[("Le score", "Chaque mention d'un parfum dans une vidéo compte, selon l'audience du créateur. Plus il y a de créateurs différents qui en parlent, plus le score monte.",
             "De score", "Elke vermelding van een parfum in een video telt, volgens het bereik van de creator. Hoe meer verschillende creators erover praten, hoe hoger de score."),
            ("Le temps", "Une mention s'efface au bout de quelques mois. Un parfum qui reste en haut, comme Aventus, est cité encore et encore.",
             "De tijd", "Een vermelding vervaagt na een paar maanden. Een parfum dat bovenaan blijft, zoals Aventus, wordt keer op keer genoemd."),
            ("La montée", "L'autre classement suit la vitesse : un parfum qui passe de 3 à 8 mentions par semaine grimpe plus vite qu'un classique déjà au sommet.",
             "De stijging", "De andere ranking volgt de snelheid: een parfum dat van 3 naar 8 vermeldingen per week gaat, stijgt sneller dan een klassieker die al bovenaan staat."),
            ("Et toi ?", "Une tendance dit ce dont on parle, pas ce qui te va. Le meilleur test reste ta peau.",
             "En jij?", "Een trend zegt waar men over praat, niet wat bij jou past. De beste test blijft je eigen huid.")])

pub("le-male-elixir", "pdj", "nl", "Le Male Elixir, Jean Paul Gaultier", "Le Male Elixir, Jean Paul Gaultier",
    "Le Male Elixir est dans le top 20 des parfums les plus cités par les créateurs, et ses mentions ont encore grimpé de 43 % en une semaine.\n\n"
    "Lavande et menthe, puis benjoin et vanille, sur un fond de miel, de tabac et de fève tonka. Intense et sucré, pour le soir.\n\n" + SOURCE_FR,
    "Le Male Elixir staat in de top 20 van de parfums die creators het vaakst noemen, en zijn vermeldingen stegen nog met 43 % in één week.\n\n"
    "Lavendel en munt, dan benzoë en vanille, op een basis van honing, tabak en tonkaboon. Intens en zoet, voor de avond.\n\n" + SOURCE_NL,
    parfums=["le-male-elixir"])

pub("orient", "sel", "fr", "Les orientaux qui font le buzz", "De oosterse parfums met de meeste buzz",
    "Ils sont partout dans les vidéos parfum : les orientaux de Lattafa et d'Afnan.\n\nAsad, Khamrah Qahwa, 9pm Night Out, Asad Bourbon : "
    "quatre parfums chauds, épicés ou gourmands, tous dans le classement des parfums les plus cités par les créateurs.\n\n"
    "Glisse pour les découvrir 👉\n\n" + SOURCE_FR,
    "Ze zijn overal in parfumvideo's: de oosterse geuren van Lattafa en Afnan.\n\nAsad, Khamrah Qahwa, 9pm Night Out, Asad Bourbon: "
    "vier warme, kruidige of gourmand parfums, allemaal in de ranking van de parfums die creators het vaakst noemen.\n\n"
    "Swipe om ze te ontdekken 👉\n\n" + SOURCE_NL,
    parfums=["asad", "khamrah-qahwa", "9pm-night-out", "asad-bourbon"],
    couv=("Les orientaux<br>qui font<br>le buzz", "Oosterse<br>parfums met<br>veel buzz"))

pub("br540", "pdj", "nl", "Baccarat Rouge 540, Maison Francis Kurkdjian", "Baccarat Rouge 540, Maison Francis Kurkdjian",
    "Plus de dix ans après sa sortie, Baccarat Rouge 540 reste dans le classement des parfums les plus cités par les créateurs.\n\n"
    "Jasmin et safran, ambre gris et bois ambré, sur un fond d'ambroxan et de cèdre. Une signature lumineuse et reconnaissable, "
    "signée Francis Kurkdjian.\n\n" + SOURCE_FR,
    "Meer dan tien jaar na de lancering staat Baccarat Rouge 540 nog altijd in de ranking van de parfums die creators het vaakst noemen.\n\n"
    "Jasmijn en saffraan, grijze amber en amberhout, op een basis van ambroxan en ceder. Een stralende, herkenbare signatuur "
    "van Francis Kurkdjian.\n\n" + SOURCE_NL, parfums=["br540"])

pub("vibrato", "pdj", "fr", "Vibrato, Sospiro", "Vibrato, Sospiro",
    "Moins connu du grand public, Vibrato de Sospiro est pourtant n°14 des parfums les plus cités par les créateurs.\n\n"
    "Bergamote, pamplemousse et fleurs blanches, puis gingembre et notes poudrées, sur un fond d'ambre, de cèdre et de musc. "
    "Frais, élégant, facile à porter au printemps.\n\n" + SOURCE_FR,
    "Minder bekend bij het grote publiek, maar Vibrato van Sospiro staat op nr. 14 van de parfums die creators het vaakst noemen.\n\n"
    "Bergamot, grapefruit en witte bloemen, dan gember en poederige noten, op een basis van amber, ceder en musk. "
    "Fris, elegant en makkelijk te dragen in de lente.\n\n" + SOURCE_NL, parfums=["vibrato"])

pub("pistache", "sel", "nl", "La pistache, la note qui monte", "Pistache, de noot in opmars",
    "La pistache est partout : dans les desserts, les cafés… et maintenant dans les parfums. Aux États-Unis, les recherches "
    "« pistache » sur Fragrance Index ont grimpé de 50 %.\n\nQuatre parfums à la pistache, du plus crémeux au plus gourmand. Glisse 👉\n\n" + SOURCE_FR,
    "Pistache is overal: in desserts, koffie… en nu ook in parfums. In de Verenigde Staten stegen de zoekopdrachten naar « pistache » op Fragrance Index met 50 %.\n\n"
    "Vier parfums met pistache, van romig tot echt gourmand. Swipe 👉\n\n" + SOURCE_NL,
    parfums=["khair", "eclaire", "pistachio-cousin", "pistachio-kunafa"],
    couv=("La pistache,<br>la note<br>qui monte", "Pistache,<br>de noot<br>in opmars"), chip=("Recherches +50 %", "Zoekopdrachten +50 %"))

pub("naxos", "pdj", "fr", "Naxos, Xerjoff", "Naxos, Xerjoff",
    "+167 % de mentions en une semaine : Naxos de Xerjoff fait partie des parfums qui montent le plus vite chez les créateurs.\n\n"
    "Bergamote, lavande et citron, puis miel et jasmin, sur un fond de tabac, de fève tonka et de vanille. Un tabac miellé, chic et chaleureux.\n\n" + SOURCE_FR,
    "+167 % vermeldingen in één week: Naxos van Xerjoff hoort bij de parfums die het snelst stijgen bij creators.\n\n"
    "Bergamot, lavendel en citroen, dan honing en jasmijn, op een basis van tabak, tonkaboon en vanille. Honingzoete tabak, chic en warm.\n\n" + SOURCE_NL,
    parfums=["naxos"])

pub("angham", "pdj", "nl", "Angham, Lattafa", "Angham, Lattafa",
    "Angham est en train de décoller : ses mentions ont été multipliées par six en une semaine chez les créateurs.\n\n"
    "Gingembre et mandarine, puis lavande, praliné et cacao, sur un fond de vanille, d'ambre et de musc. Un gourmand épicé, à partager.\n\n" + SOURCE_FR,
    "Angham is aan het doorbreken: zijn vermeldingen bij creators zijn in één week verzesvoudigd.\n\n"
    "Gember en mandarijn, dan lavendel, praliné en cacao, op een basis van vanille, amber en musk. Een kruidige gourmand, om te delen.\n\n" + SOURCE_NL,
    parfums=["angham"])

pub("ombre-leather", "pdj", "fr", "Ombré Leather Parfum, Tom Ford", "Ombré Leather Parfum, Tom Ford",
    "Le cuir version Tom Ford : Ombré Leather Parfum est dans le classement des parfums les plus cités par les créateurs.\n\n"
    "Feuille de violette et cèdre, jasmin sambac et iris, sur un fond de cuir, de bois et de tabac. Sombre, doux et très reconnaissable.\n\n" + SOURCE_FR,
    "Leer volgens Tom Ford: Ombré Leather Parfum staat in de ranking van de parfums die creators het vaakst noemen.\n\n"
    "Violetblad en ceder, sambac-jasmijn en iris, op een basis van leer, hout en tabak. Donker, zacht en heel herkenbaar.\n\n" + SOURCE_NL,
    parfums=["ombre-leather"])

pub("classiques", "sel", "nl", "Les classiques toujours au sommet", "De klassiekers die bovenaan blijven",
    "Certains parfums sont sortis il y a près de 10 ans, plus de 40 ans même pour Green Irish Tweed… et les créateurs en parlent toujours.\n\n"
    "Bleu de Chanel, Club de Nuit Intense Man, Eros Flame, Green Irish Tweed : quatre classiques qui tiennent leur place dans le classement. Glisse 👉\n\n" + SOURCE_FR,
    "Sommige parfums kwamen bijna 10 jaar geleden uit, Green Irish Tweed zelfs meer dan 40 jaar geleden… en creators praten er nog altijd over.\n\n"
    "Bleu de Chanel, Club de Nuit Intense Man, Eros Flame, Green Irish Tweed: vier klassiekers die hun plaats in de ranking houden. Swipe 👉\n\n" + SOURCE_NL,
    parfums=["bdc-edp", "cdn-man", "eros-flame", "git"],
    couv=("Les classiques<br>toujours<br>au sommet", "Klassiekers<br>die bovenaan<br>blijven"))

pub("good-girl", "pdj", "fr", "Good Girl, Carolina Herrera", "Good Girl, Carolina Herrera",
    "Le célèbre escarpin de Carolina Herrera revient dans les vidéos : Good Girl fait partie des parfums qui remontent chez les créateurs.\n\n"
    "Amande et café, tubéreuse et jasmin sambac, sur un fond de fève tonka et de cacao. Sucré, floral et un peu mystérieux.\n\n" + SOURCE_FR,
    "Het bekende pumpje van Carolina Herrera duikt weer op in video's: Good Girl hoort bij de parfums die opnieuw stijgen bij creators.\n\n"
    "Amandel en koffie, tuberoos en sambac-jasmijn, op een basis van tonkaboon en cacao. Zoet, bloemig en een tikje mysterieus.\n\n" + SOURCE_NL,
    parfums=["good-girl"])

pub("conseil-mots", "conseil", "nl", "Le vocabulaire des fans de parfum", "De woordenschat van parfumfans",
    "Blind buy, beast mode, compliment getter… Si tu regardes des vidéos parfum, tu as forcément entendu ces mots.\n\n"
    "Quatre expressions expliquées simplement. Glisse 👉",
    "Blind buy, beast mode, compliment getter… Als je parfumvideo's kijkt, heb je deze woorden zeker al gehoord.\n\n"
    "Vier uitdrukkingen eenvoudig uitgelegd. Swipe 👉",
    couv=("Blind buy,<br>beast mode…<br>ça veut dire quoi ?", "Blind buy,<br>beast mode…<br>wat betekent dat?"),
    slides=[("Blind buy", "Acheter un parfum sans l'avoir senti, sur la foi des avis. Risqué : commence par un petit format quand il existe.",
             "Blind buy", "Een parfum kopen zonder het te ruiken, op basis van reviews. Riskant: begin met een klein formaat als dat bestaat."),
            ("Beast mode", "Un parfum qui tient très longtemps et se remarque de loin. Une ou deux pulvérisations suffisent.",
             "Beast mode", "Een parfum dat heel lang blijft en van ver opvalt. Eén of twee sprays zijn genoeg."),
            ("Compliment getter", "Un parfum qui attire les compliments. Sur Fragrance Index, les recherches de cette expression ont été multipliées par quatre.",
             "Compliment getter", "Een parfum dat complimenten oplevert. Op Fragrance Index zijn de zoekopdrachten naar deze uitdrukking verviervoudigd."),
            ("Signature", "Ton parfum à toi, celui qu'on reconnaît quand tu entres dans une pièce.",
             "Signature", "Jouw eigen parfum, dat men herkent wanneer je een kamer binnenkomt.")])

pub("liquid-brun", "pdj", "fr", "Liquid Brun, French Avenue", "Liquid Brun, French Avenue",
    "Liquid Brun de French Avenue est n°11 des parfums les plus cités par les créateurs, devant bien des grandes maisons.\n\n"
    "Bergamote, cardamome et cannelle, puis vanille Bourbon et élémi, sur un fond de praliné, de bois de gaïac et de musc. "
    "Un gourmand épicé, chaleureux et enveloppant.\n\n" + SOURCE_FR,
    "Liquid Brun van French Avenue staat op nr. 11 van de parfums die creators het vaakst noemen, vóór veel grote huizen.\n\n"
    "Bergamot, kardemom en kaneel, dan bourbonvanille en elemi, op een basis van praliné, guajakhout en musk. "
    "Een kruidige gourmand, warm en omhullend.\n\n" + SOURCE_NL, parfums=["liquid-brun"])

pub("aventus", "pdj", "nl", "Aventus, Creed", "Aventus, Creed",
    "N°1. Aventus de Creed est le parfum dont les créateurs parlent le plus.\n\n"
    "Pomme, bergamote et cassis, ananas et jasmin, sur un fond de mousse de chêne, de cèdre et d'ambroxan. "
    "Fruité et boisé : un classique moderne depuis 2010.\n\n" + SOURCE_FR,
    "Nr. 1. Aventus van Creed is het parfum waar creators het meest over praten.\n\n"
    "Appel, bergamot en zwarte bes, ananas en jasmijn, op een basis van eikenmos, ceder en ambroxan. "
    "Fruitig en houtig: een moderne klassieker sinds 2010.\n\n" + SOURCE_NL, parfums=["aventus"])

pub("printemps", "sel", "fr", "La tendance fraîche pour le printemps", "De frisse trend voor de lente",
    "Les beaux jours arrivent : place aux parfums frais qui font parler d'eux.\n\n"
    "Hawas Kobra, Eros Energy, Club de Nuit Bling : agrumes, épices légères et fond musqué. Glisse 👉\n\n" + SOURCE_FR,
    "De mooie dagen komen eraan: tijd voor frisse parfums waar over gepraat wordt.\n\n"
    "Hawas Kobra, Eros Energy, Club de Nuit Bling: citrus, lichte kruiden en een muskachtige basis. Swipe 👉\n\n" + SOURCE_NL,
    parfums=["hawas-kobra", "eros-energy", "cdn-bling"],
    couv=("La tendance<br>fraîche pour<br>le printemps", "De frisse<br>trend voor<br>de lente"))

pub("noir-extreme", "pdj", "nl", "Noir Extreme Parfum, Tom Ford", "Noir Extreme Parfum, Tom Ford",
    "Noir Extreme Parfum de Tom Ford fait partie des parfums les plus cités par les créateurs.\n\n"
    "Cardamome, gingembre et mandarine, rose et fleur d'oranger, sur un fond de vanille, de cuir et de daim. "
    "Un oriental gourmand, velouté, pour le soir.\n\n" + SOURCE_FR,
    "Noir Extreme Parfum van Tom Ford hoort bij de parfums die creators het vaakst noemen.\n\n"
    "Kardemom, gember en mandarijn, roos en oranjebloesem, op een basis van vanille, leer en suède. "
    "Een fluweelzachte oosterse gourmand, voor de avond.\n\n" + SOURCE_NL, parfums=["noir-extreme"])

pub("erba-pura", "pdj", "fr", "Erba Pura, Xerjoff", "Erba Pura, Xerjoff",
    "Erba Pura de Xerjoff est dans le classement des parfums les plus cités par les créateurs, et c'est le moment de le ressortir.\n\n"
    "Citron, bergamote de Calabre et orange de Sicile, un cœur de fruits méditerranéens, sur un fond d'ambre, de vanille et de musc blanc. "
    "Fruité, solaire, parfait aux beaux jours.\n\n" + SOURCE_FR,
    "Erba Pura van Xerjoff staat in de ranking van de parfums die creators het vaakst noemen, en nu is het moment om hem weer te dragen.\n\n"
    "Citroen, Calabrische bergamot en Siciliaanse sinaasappel, een hart van mediterrane vruchten, op een basis van amber, vanille en witte musk. "
    "Fruitig, zonnig, perfect voor mooie dagen.\n\n" + SOURCE_NL, parfums=["erba-pura"])

pub("vulcan-feu", "pdj", "nl", "Vulcan Feu, French Avenue", "Vulcan Feu, French Avenue",
    "Sorti en 2025, Vulcan Feu de French Avenue est déjà dans le classement des parfums les plus cités par les créateurs.\n\n"
    "Gingembre, citron et mangue, jasmin et baies roses, praliné, sur un fond d'ambre gris, de cèdre et de fève tonka. Fruité et épicé.\n\n" + SOURCE_FR,
    "Vulcan Feu van French Avenue kwam uit in 2025 en staat nu al in de ranking van de parfums die creators het vaakst noemen.\n\n"
    "Gember, citroen en mango, jasmijn en roze peper, praliné, op een basis van grijze amber, ceder en tonkaboon. Fruitig en kruidig.\n\n" + SOURCE_NL,
    parfums=["vulcan-feu"])

pub("montees", "sel", "fr", "Ceux qui montent le plus vite", "De snelste stijgers",
    "Le classement des « Top Movers » de Fragrance Index suit les parfums dont on parle de plus en plus.\n\n"
    "Sur une semaine : Naxos +167 %, Supremacy Collector's Edition +150 %, Le Male Elixir +43 %, Khamrah +33 %, Layton +29 %. Glisse 👉\n\n" + SOURCE_FR,
    "De « Top Movers »-ranking van Fragrance Index volgt de parfums waar steeds meer over gepraat wordt.\n\n"
    "Over één week: Naxos +167 %, Supremacy Collector's Edition +150 %, Le Male Elixir +43 %, Khamrah +33 %, Layton +29 %. Swipe 👉\n\n" + SOURCE_NL,
    parfums=["naxos", "supremacy", "le-male-elixir", "khamrah", "layton"],
    couv=("Ceux qui<br>montent le<br>plus vite", "De<br>snelste<br>stijgers"),
    sig={"le-male-elixir": ("+43 % en une semaine", "+43 % in één week"), "khamrah": ("+33 % en une semaine", "+33 % in één week"),
         "layton": ("+29 % en une semaine", "+29 % in één week")})

pub("hawas-black", "pdj", "nl", "Hawas Black, Rasasi", "Hawas Black, Rasasi",
    "Après Hawas Ice, la version noire de Rasasi entre à son tour dans le classement des parfums les plus cités par les créateurs.\n\n"
    "Bergamote et ananas, jasmin, patchouli et cèdre, sur un fond d'ambre, de mousse de chêne et de bois. Boisé et fruité.\n\n" + SOURCE_FR,
    "Na Hawas Ice komt nu ook de zwarte versie van Rasasi in de ranking van de parfums die creators het vaakst noemen.\n\n"
    "Bergamot en ananas, jasmijn, patchouli en ceder, op een basis van amber, eikenmos en hout. Houtig en fruitig.\n\n" + SOURCE_NL,
    parfums=["hawas-black"])

pub("asad-elixir", "pdj", "fr", "Asad Elixir, Lattafa", "Asad Elixir, Lattafa",
    "Asad Elixir est arrivé d'un coup dans les vidéos : c'est l'un des parfums qui montent le plus vite chez les créateurs.\n\n"
    "Poivre rose, safran et pamplemousse, tabac, vanille et cèdre, sur un fond d'encens et de patchouli. Une version plus boisée et épicée d'Asad.\n\n" + SOURCE_FR,
    "Asad Elixir dook ineens op in video's: het is een van de parfums die het snelst stijgen bij creators.\n\n"
    "Roze peper, saffraan en grapefruit, tabak, vanille en ceder, op een basis van wierook en patchouli. Een houtigere, kruidigere versie van Asad.\n\n" + SOURCE_NL,
    parfums=["asad-elixir"])

pub("conseil-reflexes", "conseil", "nl", "Un parfum qui buzze : 4 réflexes avant d'acheter", "Een parfum met buzz: 4 reflexen voor je koopt",
    "Un parfum est partout sur les réseaux et tu as envie de craquer ? Avant d'acheter, quatre réflexes simples. Glisse 👉",
    "Een parfum is overal op sociale media en je wil het meteen kopen? Vier eenvoudige reflexen voor je koopt. Swipe 👉",
    couv=("Un parfum<br>qui buzze :<br>4 réflexes", "Een parfum<br>met buzz:<br>4 reflexen"),
    slides=[("Sur ta peau", "Un parfum ne sent jamais pareil sur deux personnes. Teste-le sur ton poignet, pas seulement sur une touche.",
             "Op je huid", "Een parfum ruikt nooit hetzelfde op twee personen. Test het op je pols, niet alleen op een papiertje."),
            ("Attends le fond", "La tête dure quelques minutes. Laisse passer une heure avant de décider : c'est le fond que tu porteras toute la journée.",
             "Wacht op de basis", "De topnoten duren een paar minuten. Wacht een uur voor je beslist: de basis draag je de hele dag."),
            ("Pense à la saison", "Un gourmand épicé brille en hiver, un agrume au printemps et en été. Choisis selon le moment où tu le porteras.",
             "Denk aan het seizoen", "Een kruidige gourmand schittert in de winter, citrus in de lente en zomer. Kies volgens het moment waarop je hem draagt."),
            ("Choisis la concentration", "Eau de toilette, eau de parfum, parfum, extrait : plus la concentration est forte, plus il est intense et dure longtemps.",
             "Kies de concentratie", "Eau de toilette, eau de parfum, parfum, extrait: hoe hoger de concentratie, hoe intenser en langer hij blijft.")])

pub("supremacy", "pdj", "fr", "Supremacy Collector's Edition, Afnan", "Supremacy Collector's Edition, Afnan",
    "+150 % de mentions en une semaine : Supremacy Collector's Edition d'Afnan fait partie des parfums qui montent le plus vite chez les créateurs.\n\n"
    "Ananas, bergamote et pomme, fleur d'oranger et bouleau, sur un fond de mousse de chêne, de musc et d'ambre gris. Fruité et boisé.\n\n" + SOURCE_FR,
    "+150 % vermeldingen in één week: Supremacy Collector's Edition van Afnan hoort bij de parfums die het snelst stijgen bij creators.\n\n"
    "Ananas, bergamot en appel, oranjebloesem en berk, op een basis van eikenmos, musk en grijze amber. Fruitig en houtig.\n\n" + SOURCE_NL,
    parfums=["supremacy"])

pub("dior-homme", "pdj", "nl", "Dior Homme, Dior", "Dior Homme, Dior",
    "Dior Homme revient dans les conversations : c'est l'un des parfums qui remontent chez les créateurs.\n\n"
    "Bergamote, élémi et baies roses, cèdre de l'Atlas et bois de cachemire, sur un fond de vétiver d'Haïti et de musc blanc. "
    "Boisé, net, facile à porter tous les jours.\n\n" + SOURCE_FR,
    "Dior Homme is terug in de gesprekken: het is een van de parfums die opnieuw stijgen bij creators.\n\n"
    "Bergamot, elemi en roze peper, Atlasceder en kasjmierhout, op een basis van Haïtiaanse vetiver en witte musk. "
    "Houtig, strak, makkelijk om elke dag te dragen.\n\n" + SOURCE_NL, parfums=["dior-homme"])

pub("dhi", "pdj", "fr", "Dior Homme Intense, Dior", "Dior Homme Intense, Dior",
    "Dior Homme Intense est n°7 des parfums dont les créateurs parlent le plus.\n\n"
    "Un trio iris, ambrette et cèdre de Virginie : poudré, boisé, d'une grande élégance. Un classique du soir.\n\n" + SOURCE_FR,
    "Dior Homme Intense staat op nr. 7 van de parfums waar creators het meest over praten.\n\n"
    "Een trio van iris, ambrette en Virginiaanse ceder: poederig, houtig en heel elegant. Een klassieker voor de avond.\n\n" + SOURCE_NL,
    parfums=["dhi"])

# ------------------------------------------------------------------ dates, hashtags, champs du robot
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
SUR = {"pdj": ("La tendance", "De trend"), "sel": ("Carrousel · la tendance", "Carrousel · de trend"),
       "conseil": ("Carrousel · le conseil", "Carrousel · het advies")}
NB_SLIDES = {"pdj": lambda p: 1, "sel": lambda p: len(p["parfums"]) + 2, "conseil": lambda p: len(p["slides"]) + 2}


def construire():
    debut = dt.date(2027, 3, 6)
    out = []
    for i, p in enumerate(L):
        d = debut + dt.timedelta(days=i)
        q = dict(p)
        q["n"] = 108 + i
        q["iso"] = d.isoformat()
        q["date"] = "%s %d %s" % (JOURS[d.weekday()], d.day, MOIS[d.month - 1])
        q["sur"] = SUR[p["type"]][0]
        q["produits"] = [P[c][0] for c in p.get("parfums", [])]
        q["src"] = ["Fragrance Index (fragranceindex.ai), classements Social Hype Score et Top Movers relevés le 18/11/2026",
                    "Visuels : photos des fiches Qosmi"]
        q["tags"] = TAGS_FR
        q["tags_nl"] = TAGS_NL
        q["img"] = ["%s-%d" % (q["id"], k + 1) for k in range(NB_SLIDES[p["type"]](p))]
        out.append(q)
    return out


if __name__ == "__main__":
    lot = construire()
    os.makedirs(os.path.join(ICI, "lot5"), exist_ok=True)
    json.dump(lot, open(os.path.join(ICI, "lot5", "lot5.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for q in lot:
        print(q["iso"], q["langue"], q["id"], len(q["img"]), "visuel(s)")
    print("%d publications, du %s au %s" % (len(lot), lot[0]["iso"], lot[-1]["iso"]))
