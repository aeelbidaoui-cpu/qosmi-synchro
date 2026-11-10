# Journal Qosmi — ligne éditoriale

Décisions d'Amine (08/11/2026) :
- un article par semaine, **publié automatiquement** ;
- en **français et en néerlandais** ;
- signé **« L'équipe Qosmi »**, sans avis personnel ;
- avec des **photos**.

But : être trouvé sur Google et cité par les assistants IA (ChatGPT, Gemini, Claude, Perplexity) quand quelqu'un pose une question sur le parfum.

## Règles (non négociables)
1. **Honnêteté.**
   - Personne chez Qosmi n'a senti les parfums pour l'article. On n'écrit jamais « testé », « on a senti », « notre avis après X jours ».
   - On décrit ce que la marque publie (notes, famille, concentration, année si elle est sûre) et ce qui fait consensus (« souvent décrit comme… »).
   - Pas de note sur 10, pas de faux avis, pas de témoignages inventés.
2. **Exactitude.**
   - Chaque fait vient de la marque ou d'au moins deux sources sérieuses, vérifiées sur le web au moment d'écrire.
   - En cas de doute : on ne l'écrit pas (année, nom du parfumeur…).
3. **Confidentialité.** Jamais : prix d'achat, nom des fournisseurs, marges, prix ou noms de concurrents. Ni la commune d'établissement de la société.
4. **Prix.** On n'écrit pas les prix dans les articles (ils changent). On renvoie vers la fiche.
5. **Fiches liées.**
   - On ne lie que des fiches en ligne. Le script refuse les autres.
   - L'image principale doit être une fiche en ligne.
6. **Photos.** Uniquement les photos des fiches Qosmi (autorisées) et les visuels Qosmi. Jamais d'image prise ailleurs.
7. **Pas de « dupes ».** Pas de « parfum qui sent comme X », pas de comparaison dénigrante avec une marque. On peut dire « dans le même esprit, de la même famille olfactive ».
8. **Santé.** Pas de conseil médical (allergies, grossesse) au-delà de « demande à ton médecin ou à ton pharmacien ».
9. **Testeurs.** Le sujet reste factuel. On ne publie pas d'article qui fait la promotion des testeurs tant que la question juridique n'est pas tranchée avec l'avocat.
10. **Ton.** En FR, on tutoie, comme sur le site. En NL, « je ». Phrases courtes, claires, sans jargon non expliqué.

## Format d'un article (pour Google et les assistants IA)
- **Titre** = la question telle que les gens la posent (« … : quelle différence ? », « … : notes, tenue, pour qui ? »).
- **Début** : la réponse en 2-3 phrases. Un assistant IA doit pouvoir la citer telle quelle.
- **Corps** : 600 à 1 000 mots, avec des intertitres `<h2>`.
  - Un tableau ou une liste quand ça aide.
  - Des liens vers 3 à 6 fiches Qosmi.
  - Au moins une photo (`[[photo:...]]` ou `[[photos:...]]`).
- **FAQ** : 3 à 5 questions courtes, avec des réponses autonomes de 1 à 3 phrases.
- **SEO** : titre de 70 caractères maximum, description de 160 caractères maximum, avec le nom du parfum ou de la question.
- **NL** : une vraie version néerlandaise (pas mot à mot), avec son propre `handle` en néerlandais.
- **Fichier** : `blog/articles/<numéro sur 3 chiffres>-<handle>.json` (voir `scripts/blog.py`). Un push sur `main` publie l'article (workflow « Qosmi - journal »).
- **Liens** : jamais d'adresse écrite à la main. Utiliser `[[produit:…]]`, `[[collection:…]]` ou `[[marque:…]]` : le script calcule l'adresse FR et l'adresse NL.
- **Vérification** : `python scripts/blog.py --essai` doit passer avant le push (mots interdits, longueurs SEO, champs).

## Sujets
Prendre le premier sujet non fait. Pour une fiche parfum, vérifier d'abord que le parfum est en ligne (https://qosmi.be/products.json). Sinon, passer au suivant.

Faits :
- [x] 001 Eau de parfum, eau de toilette, extrait : quelle différence ?
- [x] 002 Xerjoff Erba Pura : notes, tenue et pour qui ?
- [x] 003 Comment faire tenir son parfum plus longtemps ?

À faire :
- [ ] Parfum de niche : c'est quoi, et pourquoi c'est plus cher ?
- [ ] Nishane Hundred Silent Ways : notes et pour qui ?
- [ ] Comment choisir un parfum en ligne sans le sentir ?
- [ ] Les familles olfactives expliquées (hespéridé, floral, boisé, ambré, fougère, chypre, cuir)
- [ ] Creed Aventus : notes, versions (Aventus, Absolu, Cologne, For Her)
- [ ] Parfum d'hiver : quelles notes choisir quand il fait froid ?
- [ ] Notes de tête, de cœur et de fond : comment évolue un parfum ?
- [ ] Parfums de Marly Layton : notes et pour qui ?
- [ ] Comment conserver son parfum (lumière, chaleur, salle de bain) ?
- [ ] Idées de cadeaux parfum pour Noël (sélection par budget, sans prix exacts)
- [ ] Parfum mixte : c'est quoi ?
- [ ] Combien de pulvérisations de parfum mettre ?
- [ ] Chanel Coco Mademoiselle : EDP, Intense, Eau de Toilette, quelles différences ?
- [ ] Dior Sauvage : Parfum ou Elixir ?
- [ ] Qu'est-ce que l'oud ?
- [ ] Le musc en parfumerie : blanc, animal, synthétique ?
- [ ] La vanille en parfumerie
- [ ] Parfum au bureau : discret mais présent
- [ ] Maison Francis Kurkdjian : les incontournables
