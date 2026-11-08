"""Pages légales Qosmi (FR / NL) — contenu.
Les valeurs entre {accolades} viennent de config/site.json (e-mail du service client, etc.).
Projet à faire relire par un avocat avant l'ouverture du site."""

ENTREPRISE = {
    "raison": "Deway BV",
    "adresse": "Ijsbergstraat 73, 1701 Dilbeek, Belgique",
    "adresse_nl": "Ijsbergstraat 73, 1701 Dilbeek, België",
    "bce": "1040.851.867",
    "tva": "BE 1040.851.867",
}

PAGES = [
    # ------------------------------------------------------------------ CGV
    {
        "handle": "conditions-generales-de-vente", "handle_nl": "algemene-verkoopsvoorwaarden",
        "titre": "Conditions générales de vente", "titre_nl": "Algemene verkoopsvoorwaarden",
        "fr": """
<p><em>Version du {date}.</em></p>
<h2>1. Qui sommes-nous ?</h2>
<p>1.1 Le site qosmi.be (« le site ») est exploité par <strong>Deway BV</strong>, société à responsabilité limitée de droit belge, Ijsbergstraat 73, 1701 Dilbeek, Belgique, numéro d'entreprise {bce}, TVA {tva} (« Qosmi », « nous »). Qosmi est la boutique de parfums et de cosmétiques de Deway BV.</p>
<p>1.2 Service client : <a href="mailto:{email}">{email}</a>. Nous répondons dans les 2 jours ouvrables.</p>
<p>1.3 Ces conditions s'appliquent à toute commande passée sur le site par un consommateur, c'est-à-dire une personne physique qui achète à des fins privées. En passant commande, vous les acceptez. La version applicable est celle en vigueur au moment de votre commande ; vous pouvez l'enregistrer ou l'imprimer.</p>
<p>1.4 Pour commander, vous devez avoir au moins 18 ans ou agir avec l'accord de votre représentant légal.</p>

<h2>2. Nos produits</h2>
<p>2.1 Tous nos produits sont des produits de marque <strong>authentiques et neufs</strong>, achetés auprès de distributeurs et de grossistes établis dans l'Union européenne. Qosmi n'est pas un revendeur agréé des marques, sauf mention contraire, et n'est lié à aucune d'entre elles.</p>
<p>2.2 <strong>Testeurs.</strong> Les produits dont le nom contient « testeur » sont des produits authentiques et neufs, au contenu identique à la version vendue en boîte, mais livrés dans un emballage simple, parfois sans bouchon et avec une mention du type « demonstration » ou « not for sale ». Leur prix tient compte de cette présentation.</p>
<p>2.3 Les photos et descriptions sont données à titre indicatif. L'emballage peut varier selon les séries de fabrication de la marque, sans que le contenu change.</p>
<p>2.4 Les produits sont proposés dans la limite des stocks disponibles. Ils sont expédiés depuis l'entrepôt de notre partenaire logistique dans l'Union européenne.</p>
<p>2.5 Si un produit commandé se révèle indisponible, nous vous prévenons sans délai. Vous pouvez attendre, choisir un autre produit ou annuler ; en cas d'annulation, vous êtes remboursé au plus tard dans les 14 jours.</p>
<p>2.6 Les parfums sont des produits inflammables. Conservez-les à l'abri de la chaleur et de la lumière et utilisez-les selon les indications de l'emballage. Vérifiez la liste des ingrédients avant usage si vous êtes sujet aux allergies.</p>

<h2>3. Prix, commande et paiement</h2>
<p>3.1 Les prix sont indiqués en euros, <strong>TVA comprise</strong>, hors frais de livraison. Les frais de livraison sont affichés avant la validation de la commande. Le prix applicable est celui affiché au moment de la commande.</p>
<p>3.2 En cas d'erreur manifeste de prix (un prix sans rapport avec la valeur du produit, dû à une erreur technique ou de saisie), nous pouvons annuler la commande et vous rembourser intégralement ; vous en êtes informé sans délai.</p>
<p>3.3 Le contrat est conclu quand vous validez votre commande et votre paiement après avoir vérifié le récapitulatif (produits, prix, frais de livraison, total). Vous recevez une confirmation de commande par e-mail.</p>
<p>3.4 Nous pouvons refuser ou annuler une commande pour un motif légitime : suspicion de fraude, litige de paiement antérieur, quantités anormales pour un usage privé. Vous en êtes informé et remboursé intégralement.</p>
<p>3.5 Le paiement se fait en ligne, au moment de la commande, par les moyens proposés à la caisse (par exemple Bancontact, Visa, Mastercard, Apple Pay, Google Pay). Les paiements sont traités par un prestataire de paiement sécurisé ; nous n'avons jamais accès à vos données de carte.</p>
<p>3.6 La facture est envoyée par e-mail. Les produits restent notre propriété jusqu'au paiement complet.</p>

<h2>4. Livraison</h2>
<p>4.1 Nous livrons <strong>uniquement en Belgique</strong>. Les frais de livraison sont de <strong>{frais_livraison} TVA comprise par commande</strong>. Ils sont <strong>offerts dès 2 articles</strong> dans la même commande.</p>
<p>4.2 Délai de livraison : <strong>{delai_total}</strong> à compter de la confirmation du paiement. Le délai de votre commande vous est confirmé dans l'e-mail de confirmation de commande. Sauf autre délai convenu, la livraison a lieu au plus tard 30 jours après la conclusion du contrat.</p>
<p>4.3 En cas de retard au-delà du délai convenu, vous pouvez nous demander de livrer dans un délai supplémentaire raisonnable ; à défaut, vous pouvez annuler la commande et être remboursé sans délai.</p>
<p>4.4 Le colis est remis par un transporteur avec suivi, à l'adresse que vous indiquez. Vérifiez-la bien : un colis retourné pour adresse erronée ou non retiré peut être réexpédié contre de nouveaux frais de livraison.</p>
<p>4.5 Le risque de perte ou d'endommagement vous est transféré quand vous, ou une personne que vous désignez autre que le transporteur, prenez physiquement possession du colis. Un colis visiblement abîmé doit si possible être refusé ou accepté avec réserves, et nous être signalé rapidement avec des photos.</p>

<h2>5. Droit de rétractation</h2>
<p>5.1 Vous disposez de <strong>14 jours calendrier</strong> pour vous rétracter, sans justification ni pénalité. Ce délai court à partir du jour où vous, ou une personne que vous désignez autre que le transporteur, prenez physiquement possession du produit ; pour une commande livrée en plusieurs colis, à partir de la réception du dernier.</p>
<p>5.2 Pour exercer ce droit, informez-nous de votre décision avant la fin du délai par une déclaration claire, par e-mail à <a href="mailto:{email}">{email}</a> ou par courrier, par exemple au moyen du formulaire de la page <a href="/pages/retours">Retours</a> (son usage n'est pas obligatoire).</p>
<p>5.3 Renvoyez les produits sans retard excessif, au plus tard 14 jours après nous avoir communiqué votre décision, à l'adresse : <strong>Qosmi – Deway BV, Ijsbergstraat 73, 1701 Dilbeek, Belgique</strong>. <strong>Les frais de renvoi sont à votre charge.</strong> Les produits voyagent sous votre responsabilité ; un envoi avec suivi est recommandé.</p>
<p>5.4 Nous remboursons tous les paiements reçus, y compris les frais de livraison initiaux, au plus tard 14 jours après avoir été informés de votre rétractation, avec le moyen de paiement utilisé, sans frais pour vous. Nous pouvons différer le remboursement jusqu'à la réception des produits ou jusqu'à la preuve de leur expédition, la date la plus proche étant retenue.</p>
<p>5.5 <strong>Exception : produits descellés.</strong> Pour des raisons d'hygiène et de protection de la santé, le droit de rétractation ne s'applique pas aux produits scellés (film plastique, opercule ou autre scellé) dont vous avez retiré le scellé après la livraison (article VI.53, 5° du Code de droit économique).</p>
<p>5.6 <strong>Testeurs et produits non scellés.</strong> Le droit de rétractation s'applique. Ne manipulez le produit que dans la mesure nécessaire pour en établir la nature et les caractéristiques. Un produit vaporisé ou entamé perd de sa valeur : vous êtes alors responsable de cette dépréciation, qui peut aller jusqu'à la valeur totale du produit et est déduite du remboursement.</p>

<h2>6. Garantie légale et responsabilité</h2>
<p>6.1 Les produits bénéficient de la <strong>garantie légale de conformité de deux ans</strong> à compter de la livraison (articles 1649bis et suivants de l'ancien Code civil). Un défaut qui apparaît dans les deux ans est présumé avoir existé à la livraison, sauf preuve contraire.</p>
<p>6.2 Signalez le défaut à <a href="mailto:{email}">{email}</a> dans les <strong>deux mois</strong> suivant le jour où vous l'avez constaté, avec une description et si possible des photos. Vous avez droit, selon les conditions légales, au remplacement du produit, sinon à une réduction du prix ou au remboursement.</p>
<p>6.3 Ne sont pas des défauts de conformité : l'évaporation normale d'un produit entamé, une altération due à une mauvaise conservation (chaleur, lumière), un usage non conforme, ni une sensibilité personnelle à un ingrédient mentionné sur l'emballage.</p>
<p>6.4 Nous sommes responsables de la bonne exécution du contrat. Notre responsabilité ne peut être engagée pour un dommage indirect ni en cas de force majeure. Ces limites ne s'appliquent pas en cas de dol, de faute lourde ou de dommage corporel, et ne réduisent pas les droits que la loi vous reconnaît.</p>

<h2>7. Données personnelles, réclamations et droit applicable</h2>
<p>7.1 Nous traitons vos données pour exécuter votre commande, assurer le service client et respecter nos obligations légales, comme expliqué dans notre <a href="/pages/confidentialite">politique de confidentialité</a>.</p>
<p>7.2 Les noms et logos des marques appartiennent à leurs titulaires et ne servent qu'à désigner les produits vendus. Les textes, la mise en page, le nom Qosmi et la mascotte Mimi appartiennent à Deway BV.</p>
<p>7.3 Toute réclamation est adressée à <a href="mailto:{email}">{email}</a>. Nous répondons dans les 5 jours ouvrables.</p>
<p>7.4 À défaut de solution amiable, vous pouvez vous adresser gratuitement au <strong>Service de Médiation pour le Consommateur</strong>, boulevard du Roi Albert II 8 bte 1, 1000 Bruxelles, <a href="https://mediationconsommateur.be">mediationconsommateur.be</a>.</p>
<p>7.5 Ces conditions et les ventes conclues sur le site sont soumises au droit belge, sans vous priver de la protection des règles impératives du pays où vous résidez habituellement. Les litiges relèvent des tribunaux compétents selon les règles légales, dont ceux de votre domicile.</p>
<p>7.6 Si une clause est déclarée nulle, les autres restent applicables.</p>
""",
        "nl": """
<p><em>Versie van {date_nl}.</em></p>
<h2>1. Wie zijn wij?</h2>
<p>1.1 De website qosmi.be („de website”) wordt uitgebaat door <strong>Deway BV</strong>, besloten vennootschap naar Belgisch recht, Ijsbergstraat 73, 1701 Dilbeek, België, ondernemingsnummer {bce}, btw {tva} („Qosmi”, „wij”). Qosmi is de winkel voor parfum en cosmetica van Deway BV.</p>
<p>1.2 Klantendienst: <a href="mailto:{email}">{email}</a>. Wij antwoorden binnen 2 werkdagen.</p>
<p>1.3 Deze voorwaarden gelden voor elke bestelling die een consument, dit is een natuurlijke persoon die voor privédoeleinden koopt, op de website plaatst. Door te bestellen aanvaardt u ze. Van toepassing is de versie die geldt op het moment van uw bestelling; u kunt ze opslaan of afdrukken.</p>
<p>1.4 Om te bestellen moet u minstens 18 jaar zijn of handelen met toestemming van uw wettelijke vertegenwoordiger.</p>

<h2>2. Onze producten</h2>
<p>2.1 Al onze producten zijn <strong>originele en nieuwe</strong> merkproducten, aangekocht bij distributeurs en groothandels gevestigd in de Europese Unie. Qosmi is geen erkende verdeler van de merken, tenzij anders vermeld, en is met geen enkel merk verbonden.</p>
<p>2.2 <strong>Testers.</strong> Producten met „tester” in de naam zijn originele, nieuwe producten met dezelfde inhoud als de versie in doos, maar geleverd in een eenvoudige verpakking, soms zonder dop en met een vermelding zoals „demonstration” of „not for sale”. Hun prijs houdt rekening met deze presentatie.</p>
<p>2.3 Foto's en beschrijvingen zijn indicatief. De verpakking kan verschillen naargelang de productiereeks van het merk, zonder dat de inhoud verandert.</p>
<p>2.4 Producten worden aangeboden zolang de voorraad strekt. Ze worden verzonden vanuit het magazijn van onze logistieke partner in de Europese Unie.</p>
<p>2.5 Blijkt een besteld product niet beschikbaar, dan laten wij u dat meteen weten. U kunt wachten, een ander product kiezen of annuleren; bij annulering wordt u uiterlijk binnen 14 dagen terugbetaald.</p>
<p>2.6 Parfums zijn ontvlambare producten. Bewaar ze beschut tegen warmte en licht en gebruik ze volgens de aanwijzingen op de verpakking. Controleer bij allergieën de ingrediëntenlijst vóór gebruik.</p>

<h2>3. Prijzen, bestelling en betaling</h2>
<p>3.1 Prijzen zijn vermeld in euro, <strong>inclusief btw</strong>, exclusief verzendkosten. De verzendkosten worden getoond vóór u de bestelling bevestigt. Van toepassing is de prijs die op het moment van de bestelling wordt getoond.</p>
<p>3.2 Bij een kennelijke prijsfout (een prijs zonder verband met de waarde van het product, door een technische of invoerfout) mogen wij de bestelling annuleren en u volledig terugbetalen; u wordt daar meteen van op de hoogte gebracht.</p>
<p>3.3 De overeenkomst komt tot stand wanneer u uw bestelling en betaling bevestigt na controle van het overzicht (producten, prijzen, verzendkosten, totaal). U ontvangt een orderbevestiging per e-mail.</p>
<p>3.4 Wij kunnen een bestelling om een gegronde reden weigeren of annuleren: vermoeden van fraude, eerder betalingsgeschil, abnormale hoeveelheden voor privégebruik. U wordt verwittigd en volledig terugbetaald.</p>
<p>3.5 Betalen gebeurt online, bij de bestelling, met de betaalmiddelen die bij het afrekenen worden aangeboden (bijvoorbeeld Bancontact, Visa, Mastercard, Apple Pay, Google Pay). Betalingen worden verwerkt door een beveiligde betaaldienst; wij hebben nooit toegang tot uw kaartgegevens.</p>
<p>3.6 De factuur wordt per e-mail verstuurd. De producten blijven onze eigendom tot de volledige betaling.</p>

<h2>4. Levering</h2>
<p>4.1 Wij leveren <strong>enkel in België</strong>. De verzendkosten bedragen <strong>{frais_livraison_nl} inclusief btw per bestelling</strong>. Ze zijn <strong>gratis vanaf 2 artikelen</strong> in dezelfde bestelling.</p>
<p>4.2 Levertermijn: <strong>{delai_total_nl}</strong> na bevestiging van de betaling. De termijn van uw bestelling wordt bevestigd in de bevestigingsmail van uw bestelling. Tenzij anders overeengekomen, wordt uiterlijk 30 dagen na het sluiten van de overeenkomst geleverd.</p>
<p>4.3 Bij vertraging na de overeengekomen termijn kunt u ons vragen binnen een redelijke bijkomende termijn te leveren; gebeurt dat niet, dan kunt u de bestelling annuleren en wordt u meteen terugbetaald.</p>
<p>4.4 Het pakket wordt geleverd door een vervoerder met track-and-trace, op het adres dat u opgeeft. Controleer het goed: een pakket dat terugkomt wegens een fout adres of omdat het niet werd afgehaald, kan opnieuw worden verzonden tegen nieuwe verzendkosten.</p>
<p>4.5 Het risico van verlies of beschadiging gaat op u over wanneer u, of een door u aangewezen persoon andere dan de vervoerder, het pakket fysiek in bezit neemt. Een zichtbaar beschadigd pakket weigert u best of aanvaardt u onder voorbehoud, en meldt u ons snel met foto's.</p>

<h2>5. Herroepingsrecht</h2>
<p>5.1 U hebt <strong>14 kalenderdagen</strong> om de overeenkomst te herroepen, zonder opgave van redenen en zonder boete. Die termijn loopt vanaf de dag waarop u, of een door u aangewezen persoon andere dan de vervoerder, het product fysiek in bezit neemt; bij levering in meerdere pakketten vanaf de ontvangst van het laatste.</p>
<p>5.2 Om dit recht uit te oefenen, meldt u ons uw beslissing vóór het einde van de termijn met een duidelijke verklaring, per e-mail aan <a href="mailto:{email}">{email}</a> of per brief, bijvoorbeeld met het formulier op de pagina <a href="/pages/retours">Retourneren</a> (het gebruik ervan is niet verplicht).</p>
<p>5.3 Stuur de producten zonder onredelijke vertraging terug, uiterlijk 14 dagen nadat u ons uw beslissing hebt meegedeeld, naar: <strong>Qosmi – Deway BV, Ijsbergstraat 73, 1701 Dilbeek, België</strong>. <strong>De kosten van terugzending zijn voor uw rekening.</strong> De producten reizen op uw verantwoordelijkheid; een zending met track-and-trace is aangeraden.</p>
<p>5.4 Wij betalen alle ontvangen bedragen terug, inclusief de oorspronkelijke verzendkosten, uiterlijk 14 dagen nadat wij van uw herroeping op de hoogte zijn, met hetzelfde betaalmiddel, zonder kosten voor u. Wij mogen de terugbetaling uitstellen tot wij de producten hebben ontvangen of tot u aantoont dat u ze hebt teruggestuurd, naargelang wat eerst gebeurt.</p>
<p>5.5 <strong>Uitzondering: verzegelde producten.</strong> Om redenen van hygiëne en gezondheidsbescherming geldt het herroepingsrecht niet voor verzegelde producten (folie, zegel of andere verzegeling) waarvan u de verzegeling na de levering hebt verbroken (artikel VI.53, 5° van het Wetboek van economisch recht).</p>
<p>5.6 <strong>Testers en niet-verzegelde producten.</strong> Het herroepingsrecht is van toepassing. Behandel het product enkel voor zover nodig om de aard en de kenmerken ervan vast te stellen. Een verstoven of aangebroken product verliest waarde: u bent dan aansprakelijk voor die waardevermindering, die kan oplopen tot de volledige waarde van het product en van de terugbetaling wordt afgetrokken.</p>

<h2>6. Wettelijke garantie en aansprakelijkheid</h2>
<p>6.1 Op de producten rust de <strong>wettelijke conformiteitsgarantie van twee jaar</strong> vanaf de levering (artikelen 1649bis en volgende van het oud Burgerlijk Wetboek). Een gebrek dat binnen die twee jaar zichtbaar wordt, wordt vermoed bij de levering te hebben bestaan, behoudens tegenbewijs.</p>
<p>6.2 Meld het gebrek aan <a href="mailto:{email}">{email}</a> binnen <strong>twee maanden</strong> nadat u het hebt vastgesteld, met een beschrijving en zo mogelijk foto's. U hebt volgens de wettelijke voorwaarden recht op vervanging van het product, of anders op prijsvermindering of terugbetaling.</p>
<p>6.3 Geen conformiteitsgebrek zijn: de normale verdamping van een aangebroken product, een aantasting door slechte bewaring (warmte, licht), oneigenlijk gebruik, of een persoonlijke gevoeligheid voor een ingrediënt dat op de verpakking staat.</p>
<p>6.4 Wij zijn aansprakelijk voor de goede uitvoering van de overeenkomst. Wij zijn niet aansprakelijk voor onrechtstreekse schade of bij overmacht. Deze beperkingen gelden niet bij bedrog, zware fout of lichamelijke schade, en beperken de rechten die de wet u geeft niet.</p>

<h2>7. Persoonsgegevens, klachten en toepasselijk recht</h2>
<p>7.1 Wij verwerken uw gegevens om uw bestelling uit te voeren, klantendienst te verlenen en onze wettelijke verplichtingen na te komen, zoals uitgelegd in ons <a href="/pages/confidentialite">privacybeleid</a>.</p>
<p>7.2 Merknamen en logo's behoren toe aan hun eigenaars en dienen enkel om de verkochte producten aan te duiden. De teksten, de vormgeving, de naam Qosmi en de mascotte Mimi behoren toe aan Deway BV.</p>
<p>7.3 Klachten richt u aan <a href="mailto:{email}">{email}</a>. Wij antwoorden binnen 5 werkdagen.</p>
<p>7.4 Komen wij niet tot een minnelijke oplossing, dan kunt u gratis terecht bij de <strong>Consumentenombudsdienst</strong>, Koning Albert II-laan 8 bus 1, 1000 Brussel, <a href="https://consumentenombudsdienst.be">consumentenombudsdienst.be</a>.</p>
<p>7.5 Deze voorwaarden en de verkopen op de website vallen onder het Belgisch recht, zonder dat u de bescherming verliest van de dwingende regels van het land waar u gewoonlijk verblijft. Geschillen behoren tot de bevoegde rechtbanken volgens de wettelijke regels, waaronder die van uw woonplaats.</p>
<p>7.6 Als een bepaling nietig wordt verklaard, blijven de andere van toepassing.</p>
""",
    },
    # ------------------------------------------------------------------ Livraison
    {
        "handle": "livraison", "handle_nl": "levering",
        "titre": "Livraison", "titre_nl": "Levering",
        "fr": """
<p><strong>Livraison partout en Belgique : {frais_livraison} par commande, offerte dès 2 articles.</strong> Nous ne livrons pas en dehors de la Belgique pour le moment.</p>
<h2>Délais</h2>
<p><strong>Livraison en {delai_total}</strong> à compter de la confirmation du paiement.</p>
<p>Le délai de votre commande vous est confirmé dans l'e-mail de confirmation de commande.</p>
<h2>Suivi</h2>
<p>Dès l'expédition, vous recevez un e-mail avec le lien de suivi du colis.</p>
<h2>Un souci avec votre colis ?</h2>
<p>Colis abîmé, en retard ou incomplet : écrivez-nous à <a href="mailto:{email}">{email}</a> avec votre numéro de commande et, si possible, des photos. Les détails figurent dans nos <a href="/pages/conditions-generales-de-vente">conditions générales de vente</a> (article 4).</p>
""",
        "nl": """
<p><strong>Levering in heel België: {frais_livraison_nl} per bestelling, gratis vanaf 2 artikelen.</strong> Wij leveren voorlopig niet buiten België.</p>
<h2>Termijnen</h2>
<p><strong>Levering binnen {delai_total_nl}</strong> na bevestiging van de betaling.</p>
<p>De termijn van uw bestelling wordt bevestigd in de bevestigingsmail van uw bestelling.</p>
<h2>Track-and-trace</h2>
<p>Zodra uw pakket vertrekt, ontvangt u een e-mail met de trackinglink.</p>
<h2>Een probleem met uw pakket?</h2>
<p>Beschadigd, te laat of onvolledig: schrijf ons op <a href="mailto:{email}">{email}</a> met uw bestelnummer en zo mogelijk foto's. Meer details in onze <a href="/pages/conditions-generales-de-vente">algemene verkoopsvoorwaarden</a> (artikel 4).</p>
""",
    },
    # ------------------------------------------------------------------ Retours
    {
        "handle": "retours", "handle_nl": "retourneren",
        "titre": "Retours et rétractation", "titre_nl": "Retourneren en herroeping",
        "fr": """
<p>Vous avez <strong>14 jours</strong> après réception pour changer d'avis.</p>
<h2>Comment retourner un produit</h2>
<ol>
<li>Écrivez-nous à <a href="mailto:{email}">{email}</a> avec votre numéro de commande et le ou les produits concernés (ou envoyez le formulaire ci-dessous).</li>
<li>Renvoyez le colis dans les 14 jours qui suivent, à vos frais, à : <strong>Qosmi – Deway BV, Ijsbergstraat 73, 1701 Dilbeek, Belgique</strong>. Un envoi avec suivi est recommandé.</li>
<li>Nous vous remboursons, frais de livraison initiaux compris, au plus tard 14 jours après votre demande, dès réception du colis ou de la preuve de son envoi.</li>
</ol>
<h2>À savoir</h2>
<ul>
<li>Un produit <strong>scellé</strong> (film, opercule) dont le scellé a été retiré ne peut pas être repris, pour des raisons d'hygiène.</li>
<li>Un produit vaporisé ou entamé perd de sa valeur : cette dépréciation peut être déduite du remboursement.</li>
<li>Produit défectueux ou erreur de notre part : écrivez-nous, les frais de retour sont alors à notre charge.</li>
</ul>
<h2>Formulaire de rétractation</h2>
<p>(À compléter et renvoyer uniquement si vous souhaitez vous rétracter.)</p>
<p>À l'attention de Deway BV (Qosmi), Ijsbergstraat 73, 1701 Dilbeek, Belgique, {email} :<br>
Je vous notifie par la présente ma rétractation du contrat portant sur la vente du ou des produits ci-dessous :<br>
Commandé le / reçu le :<br>
Numéro de commande :<br>
Nom :<br>
Adresse :<br>
Signature (uniquement sur papier) :<br>
Date :</p>
""",
        "nl": """
<p>U hebt <strong>14 dagen</strong> na ontvangst om van gedachten te veranderen.</p>
<h2>Hoe stuurt u een product terug?</h2>
<ol>
<li>Schrijf ons op <a href="mailto:{email}">{email}</a> met uw bestelnummer en het product of de producten (of stuur het formulier hieronder).</li>
<li>Stuur het pakket binnen de 14 dagen daarna op eigen kosten terug naar: <strong>Qosmi – Deway BV, Ijsbergstraat 73, 1701 Dilbeek, België</strong>. Een zending met track-and-trace is aangeraden.</li>
<li>Wij betalen u terug, inclusief de oorspronkelijke verzendkosten, uiterlijk 14 dagen na uw aanvraag, zodra wij het pakket of het bewijs van verzending hebben ontvangen.</li>
</ol>
<h2>Goed om te weten</h2>
<ul>
<li>Een <strong>verzegeld</strong> product (folie, zegel) waarvan de verzegeling verbroken is, kan om hygiënische redenen niet worden teruggenomen.</li>
<li>Een verstoven of aangebroken product verliest waarde: die waardevermindering kan van de terugbetaling worden afgetrokken.</li>
<li>Defect product of vergissing van onze kant: schrijf ons, dan zijn de retourkosten voor ons.</li>
</ul>
<h2>Modelformulier voor herroeping</h2>
<p>(Enkel invullen en terugsturen als u de overeenkomst wilt herroepen.)</p>
<p>Aan Deway BV (Qosmi), Ijsbergstraat 73, 1701 Dilbeek, België, {email}:<br>
Hierbij deel ik u mee dat ik de overeenkomst betreffende de verkoop van de volgende producten herroep:<br>
Besteld op / ontvangen op:<br>
Bestelnummer:<br>
Naam:<br>
Adres:<br>
Handtekening (alleen op papier):<br>
Datum:</p>
""",
    },
    # ------------------------------------------------------------------ Confidentialité
    {
        "handle": "confidentialite", "handle_nl": "privacybeleid",
        "titre": "Politique de confidentialité", "titre_nl": "Privacybeleid",
        "fr": """
<p><em>Version du {date}.</em></p>
<h2>Responsable du traitement</h2>
<p>Deway BV, Ijsbergstraat 73, 1701 Dilbeek, Belgique, numéro d'entreprise {bce}. Contact : <a href="mailto:{email}">{email}</a>.</p>
<h2>Quelles données, pourquoi, sur quelle base</h2>
<ul>
<li><strong>Commande et livraison</strong> : nom, adresse, e-mail, téléphone, produits achetés, montant. Base : l'exécution du contrat.</li>
<li><strong>Paiement</strong> : traité par notre prestataire de paiement. Nous ne voyons pas vos données de carte. Base : l'exécution du contrat.</li>
<li><strong>Facturation et comptabilité</strong> : données de la facture. Base : nos obligations légales.</li>
<li><strong>Service client</strong> : vos messages et nos réponses. Base : l'exécution du contrat et notre intérêt légitime à vous répondre.</li>
<li><strong>Newsletter</strong> (si vous vous y inscrivez) : votre e-mail. Base : votre consentement, que vous pouvez retirer à tout moment par le lien de désinscription.</li>
<li><strong>Prévention de la fraude et sécurité du site</strong> : adresse IP, données techniques de la commande. Base : notre intérêt légitime.</li>
</ul>
<h2>Qui reçoit vos données</h2>
<ul>
<li>Shopify, qui héberge la boutique et traite les paiements (Shopify International Limited, Irlande) ;</li>
<li>le transporteur qui livre votre colis ;</li>
<li>notre partenaire logistique établi dans l'Union européenne, qui prépare et expédie les commandes (nom et adresse de livraison uniquement) ;</li>
<li>notre comptable et, si la loi l'exige, les autorités.</li>
</ul>
<p>Nous ne vendons jamais vos données. Certains prestataires peuvent traiter des données hors de l'Union européenne ; ils le font alors avec les garanties prévues par le RGPD (clauses contractuelles types ou décision d'adéquation).</p>
<h2>Combien de temps</h2>
<p>Les données de commande et de facturation sont gardées pendant le délai légal de conservation des pièces comptables (10 ans). Les autres données sont gardées le temps nécessaire à leur finalité, puis supprimées. Vous pouvez vous désinscrire de la newsletter à tout moment.</p>
<h2>Cookies</h2>
<p>Le site utilise les cookies nécessaires à son fonctionnement (panier, caisse, sécurité). Les cookies de mesure d'audience ou de publicité ne sont déposés qu'avec votre accord, que vous donnez ou refusez dans la bannière de cookies et pouvez modifier à tout moment.</p>
<h2>Vos droits</h2>
<p>Vous pouvez demander l'accès à vos données, leur rectification, leur effacement, la limitation du traitement, la portabilité, ou vous opposer à un traitement fondé sur notre intérêt légitime. Écrivez à <a href="mailto:{email}">{email}</a> ; nous répondons dans un délai d'un mois. Vous pouvez aussi introduire une plainte auprès de l'<strong>Autorité de protection des données</strong>, rue de la Presse 35, 1000 Bruxelles, <a href="https://www.autoriteprotectiondonnees.be">autoriteprotectiondonnees.be</a>.</p>
""",
        "nl": """
<p><em>Versie van {date_nl}.</em></p>
<h2>Verwerkingsverantwoordelijke</h2>
<p>Deway BV, Ijsbergstraat 73, 1701 Dilbeek, België, ondernemingsnummer {bce}. Contact: <a href="mailto:{email}">{email}</a>.</p>
<h2>Welke gegevens, waarom, op welke grond</h2>
<ul>
<li><strong>Bestelling en levering</strong>: naam, adres, e-mail, telefoon, gekochte producten, bedrag. Grond: de uitvoering van de overeenkomst.</li>
<li><strong>Betaling</strong>: verwerkt door onze betaaldienst. Wij zien uw kaartgegevens niet. Grond: de uitvoering van de overeenkomst.</li>
<li><strong>Facturatie en boekhouding</strong>: factuurgegevens. Grond: onze wettelijke verplichtingen.</li>
<li><strong>Klantendienst</strong>: uw berichten en onze antwoorden. Grond: de uitvoering van de overeenkomst en ons gerechtvaardigd belang om u te antwoorden.</li>
<li><strong>Nieuwsbrief</strong> (als u zich inschrijft): uw e-mailadres. Grond: uw toestemming, die u altijd kunt intrekken via de uitschrijflink.</li>
<li><strong>Fraudepreventie en beveiliging</strong>: IP-adres, technische gegevens van de bestelling. Grond: ons gerechtvaardigd belang.</li>
</ul>
<h2>Wie ontvangt uw gegevens</h2>
<ul>
<li>Shopify, dat de winkel host en de betalingen verwerkt (Shopify International Limited, Ierland);</li>
<li>de vervoerder die uw pakket levert;</li>
<li>onze logistieke partner in de Europese Unie, die de bestellingen klaarmaakt en verzendt (enkel naam en leveradres);</li>
<li>onze boekhouder en, als de wet het vereist, de overheid.</li>
</ul>
<p>Wij verkopen uw gegevens nooit. Sommige dienstverleners kunnen gegevens buiten de Europese Unie verwerken; zij doen dat dan met de waarborgen van de AVG (modelcontractbepalingen of adequaatheidsbesluit).</p>
<h2>Hoe lang</h2>
<p>Bestel- en factuurgegevens worden bewaard gedurende de wettelijke bewaartermijn voor boekhoudstukken (10 jaar). Andere gegevens worden bewaard zolang nodig voor hun doel en daarna gewist. U kunt zich op elk moment uitschrijven voor de nieuwsbrief.</p>
<h2>Cookies</h2>
<p>De website gebruikt de cookies die nodig zijn om te werken (winkelmandje, afrekenen, beveiliging). Cookies voor bezoekersstatistieken of reclame worden enkel geplaatst met uw toestemming, die u geeft of weigert in de cookiebanner en altijd kunt wijzigen.</p>
<h2>Uw rechten</h2>
<p>U kunt inzage, verbetering of wissing van uw gegevens vragen, de beperking van de verwerking, overdraagbaarheid, of bezwaar maken tegen een verwerking op grond van ons gerechtvaardigd belang. Schrijf naar <a href="mailto:{email}">{email}</a>; wij antwoorden binnen een maand. U kunt ook klacht indienen bij de <strong>Gegevensbeschermingsautoriteit</strong>, Drukpersstraat 35, 1000 Brussel, <a href="https://www.gegevensbeschermingsautoriteit.be">gegevensbeschermingsautoriteit.be</a>.</p>
""",
    },
    # ------------------------------------------------------------------ Mentions légales
    {
        "handle": "mentions-legales", "handle_nl": "wettelijke-vermeldingen",
        "titre": "Mentions légales", "titre_nl": "Wettelijke vermeldingen",
        "fr": """
<p><strong>Qosmi</strong> est la boutique en ligne de parfums et de cosmétiques de :</p>
<p><strong>Deway BV</strong><br>
Société à responsabilité limitée de droit belge<br>
Siège : Ijsbergstraat 73, 1701 Dilbeek, Belgique<br>
Numéro d'entreprise (BCE) : {bce} – RPR Bruxelles<br>
TVA : {tva}<br>
E-mail : <a href="mailto:{email}">{email}</a></p>
<p><strong>Hébergement</strong> : Shopify International Limited, Victoria Buildings, 2nd Floor, 1-2 Haddington Road, Dublin 4, D04 XN32, Irlande.</p>
<p>Les marques et logos des produits appartiennent à leurs titulaires. Le nom Qosmi, la mascotte Mimi, les textes et la mise en page du site appartiennent à Deway BV.</p>
<p>Voir aussi : <a href="/pages/conditions-generales-de-vente">conditions générales de vente</a> · <a href="/pages/confidentialite">politique de confidentialité</a>.</p>
""",
        "nl": """
<p><strong>Qosmi</strong> is de onlinewinkel voor parfum en cosmetica van:</p>
<p><strong>Deway BV</strong><br>
Besloten vennootschap naar Belgisch recht<br>
Zetel: Ijsbergstraat 73, 1701 Dilbeek, België<br>
Ondernemingsnummer (KBO): {bce} – RPR Brussel<br>
Btw: {tva}<br>
E-mail: <a href="mailto:{email}">{email}</a></p>
<p><strong>Hosting</strong>: Shopify International Limited, Victoria Buildings, 2nd Floor, 1-2 Haddington Road, Dublin 4, D04 XN32, Ierland.</p>
<p>De merken en logo's van de producten behoren toe aan hun eigenaars. De naam Qosmi, de mascotte Mimi, de teksten en de vormgeving van de website behoren toe aan Deway BV.</p>
<p>Zie ook: <a href="/pages/conditions-generales-de-vente">algemene verkoopsvoorwaarden</a> · <a href="/pages/confidentialite">privacybeleid</a>.</p>
""",
    },
]


# =====================================================================
# Ajouts du 30/10 (23 h 45) : confidentialité réécrite, conditions d'utilisation,
# cookies, accessibilité ; « Retours » devient « Retours et remboursements ».
# =====================================================================

CONFIDENTIALITE = {
    "handle": "confidentialite", "handle_nl": "privacybeleid",
    "titre": "Politique de confidentialité", "titre_nl": "Privacybeleid",
    "fr": """
<p><em>Version du {date}.</em></p>
<p>Nous ne collectons que les données nécessaires pour vous vendre et vous livrer nos produits, et pour respecter la loi. Nous ne vendons jamais vos données.</p>
<h2>1. Qui est responsable de vos données ?</h2>
<p>Deway BV (Qosmi), Ijsbergstraat 73, 1701 Dilbeek, Belgique, numéro d'entreprise {bce}. Pour toute question sur vos données : <a href="mailto:{email}">{email}</a>.</p>
<h2>2. Quelles données, pourquoi et sur quelle base légale ?</h2>
<table>
<thead><tr><th scope="col">Situation</th><th scope="col">Données</th><th scope="col">Pourquoi</th><th scope="col">Base légale (RGPD)</th></tr></thead>
<tbody>
<tr><td>Commande</td><td>Nom, adresse de livraison et de facturation, e-mail, produits achetés, montant. Téléphone seulement si vous le donnez (facultatif).</td><td>Traiter, livrer et facturer votre commande ; vous envoyer la confirmation et le suivi.</td><td>Exécution du contrat (art. 6.1.b)</td></tr>
<tr><td>Paiement</td><td>Données de paiement, traitées directement par le prestataire de paiement. Nous ne voyons jamais vos données de carte.</td><td>Encaisser le paiement, prévenir la fraude.</td><td>Exécution du contrat ; intérêt légitime à prévenir la fraude (art. 6.1.b et f)</td></tr>
<tr><td>Facture et comptabilité</td><td>Données de la facture.</td><td>Tenir notre comptabilité et nos obligations TVA.</td><td>Obligation légale (art. 6.1.c)</td></tr>
<tr><td>Compte client (facultatif)</td><td>E-mail, nom, adresses enregistrées, historique des commandes.</td><td>Vous permettre de suivre vos commandes.</td><td>Exécution du contrat (art. 6.1.b)</td></tr>
<tr><td>Service client, retours</td><td>Vos messages, numéro de commande, photos que vous nous envoyez.</td><td>Répondre, traiter un retour ou une garantie.</td><td>Exécution du contrat ; obligation légale (garantie)</td></tr>
<tr><td>Lettre d'information (si vous vous inscrivez)</td><td>Votre e-mail et la date de votre accord.</td><td>Vous envoyer notre lettre mensuelle.</td><td>Consentement (art. 6.1.a), retirable à tout moment</td></tr>
<tr><td>Fonctionnement et sécurité du site</td><td>Données techniques (adresse IP, navigateur), cookies strictement nécessaires.</td><td>Faire fonctionner le panier et la caisse, sécuriser le site.</td><td>Intérêt légitime (art. 6.1.f)</td></tr>
<tr><td>Mesure d'audience (seulement si vous l'acceptez)</td><td>Pages vues, interactions, données de cookies d'analyse.</td><td>Comprendre l'usage du site pour l'améliorer.</td><td>Consentement (art. 6.1.a)</td></tr>
</tbody>
</table>
<p>Nous ne prenons aucune décision automatisée qui produit des effets juridiques à votre égard, à l'exception de l'analyse antifraude automatique du prestataire de paiement, qui peut bloquer un paiement suspect. Vous pouvez alors nous contacter pour un examen humain.</p>
<h2>3. Qui reçoit vos données ?</h2>
<ul>
<li><strong>Shopify</strong>, qui héberge la boutique, traite les paiements et envoie les e-mails de commande (Shopify International Limited, Irlande, et ses sous-traitants) ;</li>
<li><strong>le transporteur</strong> qui livre votre colis (nom, adresse, e-mail ou téléphone pour l'avis de livraison) ;</li>
<li><strong>notre partenaire logistique établi dans l'Union européenne</strong>, qui prépare et expédie les commandes (nom et adresse de livraison seulement) ;</li>
<li><strong>notre comptable</strong> et, si la loi l'exige, les autorités.</li>
</ul>
<p>Certains sous-traitants de Shopify traitent des données hors de l'Union européenne, notamment au Canada (pays reconnu comme offrant une protection adéquate) et aux États-Unis. Ces transferts sont encadrés par les garanties prévues par le RGPD (décision d'adéquation ou clauses contractuelles types).</p>
<h2>4. Combien de temps ?</h2>
<ul>
<li>Données de commande et factures : pendant les délais légaux de conservation des documents comptables et fiscaux ;</li>
<li>compte client : tant que le compte existe, puis supprimé sur demande ou après 3 ans sans commande ;</li>
<li>messages au service client : 3 ans après le dernier échange, sauf litige en cours ;</li>
<li>lettre d'information : jusqu'à votre désinscription ;</li>
<li>cookies : voir notre <a href="/pages/cookies">politique de cookies</a>.</li>
</ul>
<h2>5. Vos droits</h2>
<p>Vous pouvez demander l'accès à vos données, leur rectification, leur effacement, la limitation du traitement et la portabilité, et vous opposer à un traitement fondé sur notre intérêt légitime. Vous pouvez retirer votre consentement à tout moment, sans effet sur ce qui a été fait avant. Écrivez à <a href="mailto:{email}">{email}</a> ; nous répondons dans un délai d'un mois. Nous pouvons vous demander de prouver votre identité.</p>
<p>Vous pouvez aussi introduire une plainte auprès de l'<strong>Autorité de protection des données</strong>, rue de la Presse 35, 1000 Bruxelles, <a href="https://www.autoriteprotectiondonnees.be">autoriteprotectiondonnees.be</a>.</p>
<h2>6. Modifications</h2>
<p>Nous mettons cette politique à jour si nos pratiques changent (par exemple l'ajout d'un outil de mesure d'audience). La date de version figure en haut de la page.</p>
""",
    "nl": """
<p><em>Versie van {date_nl}.</em></p>
<p>Wij verzamelen enkel de gegevens die nodig zijn om u onze producten te verkopen en te leveren, en om de wet na te leven. Wij verkopen uw gegevens nooit.</p>
<h2>1. Wie is verantwoordelijk voor uw gegevens?</h2>
<p>Deway BV (Qosmi), Ijsbergstraat 73, 1701 Dilbeek, België, ondernemingsnummer {bce}. Voor elke vraag over uw gegevens: <a href="mailto:{email}">{email}</a>.</p>
<h2>2. Welke gegevens, waarom en op welke rechtsgrond?</h2>
<table>
<thead><tr><th scope="col">Situatie</th><th scope="col">Gegevens</th><th scope="col">Waarom</th><th scope="col">Rechtsgrond (AVG)</th></tr></thead>
<tbody>
<tr><td>Bestelling</td><td>Naam, lever- en factuuradres, e-mail, gekochte producten, bedrag. Telefoon enkel als u die opgeeft (facultatief).</td><td>Uw bestelling verwerken, leveren en factureren; u de bevestiging en de tracking sturen.</td><td>Uitvoering van de overeenkomst (art. 6.1.b)</td></tr>
<tr><td>Betaling</td><td>Betaalgegevens, rechtstreeks verwerkt door de betaaldienst. Wij zien uw kaartgegevens nooit.</td><td>De betaling innen, fraude voorkomen.</td><td>Uitvoering van de overeenkomst; gerechtvaardigd belang om fraude te voorkomen (art. 6.1.b en f)</td></tr>
<tr><td>Factuur en boekhouding</td><td>Factuurgegevens.</td><td>Onze boekhouding en btw-verplichtingen.</td><td>Wettelijke verplichting (art. 6.1.c)</td></tr>
<tr><td>Klantenaccount (facultatief)</td><td>E-mail, naam, bewaarde adressen, bestelgeschiedenis.</td><td>U uw bestellingen laten opvolgen.</td><td>Uitvoering van de overeenkomst (art. 6.1.b)</td></tr>
<tr><td>Klantendienst, retours</td><td>Uw berichten, bestelnummer, foto's die u ons stuurt.</td><td>Antwoorden, een retour of garantie behandelen.</td><td>Uitvoering van de overeenkomst; wettelijke verplichting (garantie)</td></tr>
<tr><td>Nieuwsbrief (als u zich inschrijft)</td><td>Uw e-mail en de datum van uw toestemming.</td><td>U onze maandelijkse nieuwsbrief sturen.</td><td>Toestemming (art. 6.1.a), altijd intrekbaar</td></tr>
<tr><td>Werking en beveiliging van de website</td><td>Technische gegevens (IP-adres, browser), strikt noodzakelijke cookies.</td><td>Het winkelmandje en het afrekenen laten werken, de website beveiligen.</td><td>Gerechtvaardigd belang (art. 6.1.f)</td></tr>
<tr><td>Bezoekersstatistieken (enkel als u dat aanvaardt)</td><td>Bekeken pagina's, interacties, gegevens van analytische cookies.</td><td>Het gebruik van de website begrijpen om ze te verbeteren.</td><td>Toestemming (art. 6.1.a)</td></tr>
</tbody>
</table>
<p>Wij nemen geen geautomatiseerde beslissingen met rechtsgevolgen voor u, behalve de automatische fraudecontrole van de betaaldienst, die een verdachte betaling kan blokkeren. U kunt ons dan contacteren voor een menselijke beoordeling.</p>
<h2>3. Wie ontvangt uw gegevens?</h2>
<ul>
<li><strong>Shopify</strong>, dat de winkel host, de betalingen verwerkt en de bestelmails verstuurt (Shopify International Limited, Ierland, en zijn verwerkers);</li>
<li><strong>de vervoerder</strong> die uw pakket levert (naam, adres, e-mail of telefoon voor het leveringsbericht);</li>
<li><strong>onze logistieke partner in de Europese Unie</strong>, die de bestellingen klaarmaakt en verzendt (enkel naam en leveradres);</li>
<li><strong>onze boekhouder</strong> en, als de wet het vereist, de overheid.</li>
</ul>
<p>Sommige verwerkers van Shopify verwerken gegevens buiten de Europese Unie, onder meer in Canada (land met een erkend passend beschermingsniveau) en in de Verenigde Staten. Die doorgiften gebeuren met de waarborgen van de AVG (adequaatheidsbesluit of modelcontractbepalingen).</p>
<h2>4. Hoe lang?</h2>
<ul>
<li>Bestelgegevens en facturen: gedurende de wettelijke bewaartermijnen voor boekhoudkundige en fiscale documenten;</li>
<li>klantenaccount: zolang het account bestaat, daarna gewist op verzoek of na 3 jaar zonder bestelling;</li>
<li>berichten aan de klantendienst: 3 jaar na het laatste contact, behalve bij een lopend geschil;</li>
<li>nieuwsbrief: tot u zich uitschrijft;</li>
<li>cookies: zie ons <a href="/pages/cookies">cookiebeleid</a>.</li>
</ul>
<h2>5. Uw rechten</h2>
<p>U kunt inzage, verbetering of wissing van uw gegevens vragen, de beperking van de verwerking en overdraagbaarheid, en u kunt bezwaar maken tegen een verwerking op grond van ons gerechtvaardigd belang. U kunt uw toestemming altijd intrekken, zonder gevolg voor wat daarvoor gebeurde. Schrijf naar <a href="mailto:{email}">{email}</a>; wij antwoorden binnen een maand. Wij kunnen u vragen uw identiteit aan te tonen.</p>
<p>U kunt ook klacht indienen bij de <strong>Gegevensbeschermingsautoriteit</strong>, Drukpersstraat 35, 1000 Brussel, <a href="https://www.gegevensbeschermingsautoriteit.be">gegevensbeschermingsautoriteit.be</a>.</p>
<h2>6. Wijzigingen</h2>
<p>Wij passen dit beleid aan als onze werkwijze verandert (bijvoorbeeld als wij een tool voor bezoekersstatistieken toevoegen). De versiedatum staat bovenaan de pagina.</p>
""",
}

COOKIES = {
    "handle": "cookies", "handle_nl": "cookiebeleid",
    "titre": "Politique de cookies", "titre_nl": "Cookiebeleid",
    "fr": """
<p><em>Version du {date}.</em></p>
<p>Un cookie est un petit fichier que le site enregistre dans votre navigateur. Nous n'utilisons que les cookies strictement nécessaires sans votre accord. Les autres ne sont déposés que si vous les acceptez dans la bannière de cookies.</p>
<h2>Vos choix</h2>
<p>À votre première visite, la bannière vous propose d'accepter ou de refuser, aussi simplement l'un que l'autre, ou de choisir par catégorie. Vous pouvez changer d'avis à tout moment avec le lien <strong>« Préférences cookies »</strong> en bas de chaque page. Refuser n'empêche pas de commander.</p>
<h2>Les cookies utilisés</h2>
<table>
<thead><tr><th scope="col">Cookie</th><th scope="col">À quoi il sert</th><th scope="col">Catégorie</th><th scope="col">Durée</th></tr></thead>
<tbody>
<tr><td>_shopify_essential</td><td>Session, caisse et protection contre la fraude</td><td>Nécessaire</td><td>1 an</td></tr>
<tr><td>_shopify_cmp</td><td>Mémorise vos choix de cookies</td><td>Nécessaire</td><td>1 an</td></tr>
<tr><td>cart</td><td>Contenu de votre panier</td><td>Nécessaire</td><td>2 semaines</td></tr>
<tr><td>cart_currency</td><td>Devise du panier après une commande</td><td>Nécessaire</td><td>2 semaines</td></tr>
<tr><td>localization</td><td>Pays et langue de la boutique</td><td>Nécessaire</td><td>1 an</td></tr>
<tr><td>discount_code</td><td>Code de réduction reçu par un lien</td><td>Nécessaire</td><td>Session</td></tr>
<tr><td>_shopify_test</td><td>Vérifie que votre navigateur accepte les cookies</td><td>Nécessaire</td><td>1 minute</td></tr>
<tr><td>__Host-Http-shop_binding</td><td>Connexion avec Shop (si vous l'utilisez)</td><td>Nécessaire</td><td>3 heures</td></tr>
<tr><td>_shopify_analytics</td><td>Statistiques de visite de la boutique et de la caisse</td><td>Analyse (avec votre accord)</td><td>1 an</td></tr>
<tr><td>_shopify_marketing</td><td>Données marketing de la boutique et de la caisse</td><td>Marketing (avec votre accord)</td><td>1 an</td></tr>
</tbody>
</table>
<p>Ces cookies sont déposés par Shopify, la plateforme qui héberge notre boutique. Le prestataire de paiement peut aussi utiliser, pendant le paiement, des cookies nécessaires à la prévention de la fraude. Nous n'utilisons aujourd'hui aucun outil de publicité ni de réseau social (pas de pixel Meta, TikTok ou Google Ads). Si cela change, cette page et la bannière seront mises à jour avant.</p>
<h2>Bloquer les cookies dans votre navigateur</h2>
<p>Vous pouvez aussi supprimer ou bloquer les cookies dans les réglages de votre navigateur. Sans les cookies nécessaires, le panier et la caisse ne fonctionnent pas.</p>
<p>Questions : <a href="mailto:{email}">{email}</a>. Voir aussi notre <a href="/pages/confidentialite">politique de confidentialité</a>.</p>
""",
    "nl": """
<p><em>Versie van {date_nl}.</em></p>
<p>Een cookie is een klein bestand dat de website in uw browser bewaart. Zonder uw toestemming gebruiken wij enkel strikt noodzakelijke cookies. De andere worden pas geplaatst als u ze aanvaardt in de cookiebanner.</p>
<h2>Uw keuze</h2>
<p>Bij uw eerste bezoek kunt u in de banner aanvaarden of weigeren, het ene even eenvoudig als het andere, of per categorie kiezen. U kunt uw keuze altijd wijzigen via de link <strong>„Cookievoorkeuren”</strong> onderaan elke pagina. Weigeren belet u niet om te bestellen.</p>
<h2>De gebruikte cookies</h2>
<table>
<thead><tr><th scope="col">Cookie</th><th scope="col">Waarvoor</th><th scope="col">Categorie</th><th scope="col">Duur</th></tr></thead>
<tbody>
<tr><td>_shopify_essential</td><td>Sessie, afrekenen en fraudebescherming</td><td>Noodzakelijk</td><td>1 jaar</td></tr>
<tr><td>_shopify_cmp</td><td>Onthoudt uw cookiekeuzes</td><td>Noodzakelijk</td><td>1 jaar</td></tr>
<tr><td>cart</td><td>Inhoud van uw winkelmandje</td><td>Noodzakelijk</td><td>2 weken</td></tr>
<tr><td>cart_currency</td><td>Munt van het winkelmandje na een bestelling</td><td>Noodzakelijk</td><td>2 weken</td></tr>
<tr><td>localization</td><td>Land en taal van de winkel</td><td>Noodzakelijk</td><td>1 jaar</td></tr>
<tr><td>discount_code</td><td>Kortingscode ontvangen via een link</td><td>Noodzakelijk</td><td>Sessie</td></tr>
<tr><td>_shopify_test</td><td>Controleert of uw browser cookies aanvaardt</td><td>Noodzakelijk</td><td>1 minuut</td></tr>
<tr><td>__Host-Http-shop_binding</td><td>Aanmelden met Shop (als u dat gebruikt)</td><td>Noodzakelijk</td><td>3 uur</td></tr>
<tr><td>_shopify_analytics</td><td>Bezoekersstatistieken van de winkel en het afrekenen</td><td>Analytisch (met uw toestemming)</td><td>1 jaar</td></tr>
<tr><td>_shopify_marketing</td><td>Marketinggegevens van de winkel en het afrekenen</td><td>Marketing (met uw toestemming)</td><td>1 jaar</td></tr>
</tbody>
</table>
<p>Deze cookies worden geplaatst door Shopify, het platform dat onze winkel host. De betaaldienst kan tijdens de betaling ook cookies gebruiken die nodig zijn om fraude te voorkomen. Wij gebruiken vandaag geen reclame- of socialemediatools (geen pixel van Meta, TikTok of Google Ads). Verandert dat, dan worden deze pagina en de banner vooraf aangepast.</p>
<h2>Cookies blokkeren in uw browser</h2>
<p>U kunt cookies ook wissen of blokkeren in de instellingen van uw browser. Zonder de noodzakelijke cookies werken het winkelmandje en het afrekenen niet.</p>
<p>Vragen: <a href="mailto:{email}">{email}</a>. Zie ook ons <a href="/pages/confidentialite">privacybeleid</a>.</p>
""",
}

UTILISATION = {
    "handle": "conditions-d-utilisation", "handle_nl": "gebruiksvoorwaarden",
    "titre": "Conditions d'utilisation", "titre_nl": "Gebruiksvoorwaarden",
    "fr": """
<p><em>Version du {date}.</em></p>
<p>Ces conditions règlent l'utilisation du site qosmi.be, exploité par Deway BV ({bce}). Les achats sont régis par nos <a href="/pages/conditions-generales-de-vente">conditions générales de vente</a>.</p>
<h2>1. Accès au site</h2>
<p>Le site est accessible gratuitement. Nous faisons notre possible pour qu'il soit disponible et exact, mais une interruption (maintenance, panne) ou une erreur reste possible. Les prix et le stock affichés sont mis à jour régulièrement ; seuls font foi ceux confirmés au moment de la commande.</p>
<h2>2. Compte client</h2>
<p>Le compte client est facultatif. Vous êtes responsable de l'exactitude de vos données et de l'accès à votre adresse e-mail, qui sert à vous connecter. Prévenez-nous si vous pensez que quelqu'un utilise votre compte.</p>
<h2>3. Ce qui n'est pas permis</h2>
<ul>
<li>utiliser le site à des fins illégales ou frauduleuses ;</li>
<li>tenter de perturber, surcharger ou contourner la sécurité du site ;</li>
<li>copier le contenu propre du site (textes, mise en page, nom Qosmi, mascotte Mimi) pour un autre usage que personnel ;</li>
<li>acheter pour revendre à titre professionnel : nos ventes sont réservées aux consommateurs.</li>
</ul>
<h2>4. Assistants et agents d'intelligence artificielle</h2>
<p>Vous pouvez utiliser un assistant ou un agent d'IA pour consulter le site, comparer nos produits ou préparer une commande. Une commande passée par un tel outil l'est en votre nom : vous restez la personne qui conclut le contrat et vous gardez tous vos droits de consommateur, dont le droit de rétractation. L'accès automatisé doit rester raisonnable et ne pas surcharger le site.</p>
<h2>5. Contenu et liens</h2>
<p>Les descriptions des produits sont données à titre indicatif. Les marques et logos appartiennent à leurs titulaires. Les liens vers d'autres sites sont fournis pour votre confort ; nous ne sommes pas responsables de leur contenu.</p>
<h2>6. Responsabilité</h2>
<p>Notre responsabilité liée à l'utilisation du site est limitée aux dommages directs causés par notre faute. Cette limite ne s'applique pas en cas de dol, de faute lourde ou de dommage corporel, et ne réduit pas vos droits de consommateur.</p>
<h2>7. Modifications et droit applicable</h2>
<p>Nous pouvons modifier ces conditions ; la date de version figure en haut de la page. Le droit belge s'applique, sans vous priver de la protection des règles impératives de votre pays de résidence. Contact : <a href="mailto:{email}">{email}</a>.</p>
""",
    "nl": """
<p><em>Versie van {date_nl}.</em></p>
<p>Deze voorwaarden regelen het gebruik van de website qosmi.be, uitgebaat door Deway BV ({bce}). Aankopen vallen onder onze <a href="/pages/conditions-generales-de-vente">algemene verkoopsvoorwaarden</a>.</p>
<h2>1. Toegang tot de website</h2>
<p>De website is gratis toegankelijk. Wij doen ons best om ze beschikbaar en juist te houden, maar een onderbreking (onderhoud, storing) of een fout blijft mogelijk. Getoonde prijzen en voorraad worden regelmatig bijgewerkt; enkel die bevestigd bij de bestelling gelden.</p>
<h2>2. Klantenaccount</h2>
<p>Een klantenaccount is facultatief. U bent verantwoordelijk voor de juistheid van uw gegevens en voor de toegang tot uw e-mailadres, waarmee u zich aanmeldt. Laat het ons weten als u denkt dat iemand anders uw account gebruikt.</p>
<h2>3. Wat niet is toegestaan</h2>
<ul>
<li>de website gebruiken voor onwettige of frauduleuze doeleinden;</li>
<li>proberen de website te verstoren, te overbelasten of de beveiliging te omzeilen;</li>
<li>de eigen inhoud van de website (teksten, vormgeving, naam Qosmi, mascotte Mimi) kopiëren voor ander dan persoonlijk gebruik;</li>
<li>kopen om beroepsmatig door te verkopen: onze verkoop is voorbehouden aan consumenten.</li>
</ul>
<h2>4. AI-assistenten en -agenten</h2>
<p>U mag een AI-assistent of -agent gebruiken om de website te raadplegen, onze producten te vergelijken of een bestelling voor te bereiden. Een bestelling via zo'n tool gebeurt in uw naam: u blijft de persoon die de overeenkomst sluit en u behoudt al uw consumentenrechten, waaronder het herroepingsrecht. Geautomatiseerde toegang moet redelijk blijven en mag de website niet overbelasten.</p>
<h2>5. Inhoud en links</h2>
<p>Productbeschrijvingen zijn indicatief. Merken en logo's behoren toe aan hun eigenaars. Links naar andere websites zijn er voor uw gemak; wij zijn niet verantwoordelijk voor hun inhoud.</p>
<h2>6. Aansprakelijkheid</h2>
<p>Onze aansprakelijkheid voor het gebruik van de website is beperkt tot rechtstreekse schade door onze fout. Die beperking geldt niet bij bedrog, zware fout of lichamelijke schade, en beperkt uw consumentenrechten niet.</p>
<h2>7. Wijzigingen en toepasselijk recht</h2>
<p>Wij kunnen deze voorwaarden wijzigen; de versiedatum staat bovenaan de pagina. Het Belgisch recht is van toepassing, zonder dat u de bescherming verliest van de dwingende regels van uw land van verblijf. Contact: <a href="mailto:{email}">{email}</a>.</p>
""",
}

ACCESSIBILITE = {
    "handle": "accessibilite", "handle_nl": "toegankelijkheid",
    "titre": "Déclaration d'accessibilité", "titre_nl": "Toegankelijkheidsverklaring",
    "fr": """
<p><em>Version du {date}.</em></p>
<p>Nous voulons que chacun puisse découvrir et acheter nos produits, y compris avec un lecteur d'écran, au clavier seul, en agrandissant le texte ou avec un assistant numérique.</p>
<h2>Ce que nous faisons</h2>
<ul>
<li>Nous visons le niveau AA des règles WCAG 2.1, reprises dans la norme européenne EN 301 549.</li>
<li>Chaque photo de produit porte un texte de remplacement qui décrit le produit ; les images purement décoratives sont ignorées par les lecteurs d'écran.</li>
<li>Les couleurs du texte ont un contraste d'au moins 4,5:1 avec leur fond (3:1 pour les grands titres et les contours des champs).</li>
<li>Le site est utilisable au clavier, les boutons et liens ont un nom clair, et les pages ont des titres structurés.</li>
<li>Les informations des produits (marque, contenance, prix, disponibilité, code EAN) sont publiées aussi sous forme de données structurées, lisibles par les outils d'assistance et les agents numériques.</li>
</ul>
<h2>État de conformité</h2>
<p>Le site est <strong>partiellement conforme</strong> : il n'a pas encore fait l'objet d'un audit externe. Limites connues : certaines descriptions de produits reprennent des termes techniques du fabricant ; la page de paiement est fournie par notre plateforme (Shopify), dont nous ne contrôlons pas tout le contenu.</p>
<h2>Un problème ?</h2>
<p>Si un contenu vous est inaccessible, écrivez-nous à <a href="mailto:{email}">{email}</a> : nous vous répondons dans les 5 jours ouvrables et vous proposons une alternative (par exemple, passer la commande avec vous par e-mail). Vous pouvez aussi signaler un problème au SPF Économie via le <a href="https://pointdecontact.belgique.be">Point de contact</a>.</p>
""",
    "nl": """
<p><em>Versie van {date_nl}.</em></p>
<p>Wij willen dat iedereen onze producten kan ontdekken en kopen, ook met een schermlezer, enkel met het toetsenbord, met vergrote tekst of met een digitale assistent.</p>
<h2>Wat wij doen</h2>
<ul>
<li>Wij streven naar niveau AA van de WCAG 2.1-richtlijnen, opgenomen in de Europese norm EN 301 549.</li>
<li>Elke productfoto heeft een alternatieve tekst die het product beschrijft; louter decoratieve afbeeldingen worden door schermlezers overgeslagen.</li>
<li>Tekstkleuren hebben een contrast van minstens 4,5:1 met hun achtergrond (3:1 voor grote titels en de randen van invoervelden).</li>
<li>De website werkt met het toetsenbord, knoppen en links hebben een duidelijke naam en pagina's hebben gestructureerde titels.</li>
<li>Productinformatie (merk, inhoud, prijs, beschikbaarheid, EAN-code) wordt ook als gestructureerde gegevens gepubliceerd, leesbaar voor hulpmiddelen en digitale agenten.</li>
</ul>
<h2>Conformiteitsstatus</h2>
<p>De website is <strong>gedeeltelijk conform</strong>: ze werd nog niet extern geaudit. Gekende beperkingen: sommige productbeschrijvingen gebruiken technische termen van de fabrikant; de betaalpagina wordt geleverd door ons platform (Shopify), waarvan wij niet alle inhoud beheren.</p>
<h2>Een probleem?</h2>
<p>Is een inhoud voor u niet toegankelijk, schrijf ons dan op <a href="mailto:{email}">{email}</a>: wij antwoorden binnen 5 werkdagen en bieden u een alternatief (bijvoorbeeld de bestelling samen per e-mail plaatsen). U kunt een probleem ook melden bij de FOD Economie via het <a href="https://meldpunt.belgie.be">Meldpunt</a>.</p>
""",
}

REMBOURSEMENT_FR = """
<h2>Remboursement</h2>
<ul>
<li><strong>Ce qui est remboursé</strong> : le prix des produits retournés et les frais de livraison initiaux (si toute la commande est retournée, à hauteur du mode de livraison standard).</li>
<li><strong>Quand</strong> : au plus tard 14 jours après votre demande de rétractation ; nous pouvons attendre la réception du colis ou la preuve de son envoi.</li>
<li><strong>Comment</strong> : avec le moyen de paiement utilisé pour la commande, sans frais pour vous.</li>
<li><strong>Produit abîmé, défectueux ou erreur de notre part</strong> : remplacement ou remboursement complet, frais de retour à notre charge (garantie légale de deux ans).</li>
</ul>
"""
REMBOURSEMENT_NL = """
<h2>Terugbetaling</h2>
<ul>
<li><strong>Wat wordt terugbetaald</strong>: de prijs van de teruggestuurde producten en de oorspronkelijke verzendkosten (als de volledige bestelling wordt teruggestuurd, ten belope van de standaardlevering).</li>
<li><strong>Wanneer</strong>: uiterlijk 14 dagen na uw herroeping; wij mogen wachten tot wij het pakket of het bewijs van verzending ontvangen.</li>
<li><strong>Hoe</strong>: met het betaalmiddel van de bestelling, zonder kosten voor u.</li>
<li><strong>Beschadigd of defect product, of vergissing van onze kant</strong>: vervanging of volledige terugbetaling, retourkosten voor ons (wettelijke garantie van twee jaar).</li>
</ul>
"""


def _maj():
    for i, p in enumerate(PAGES):
        if p["handle"] == "confidentialite":
            PAGES[i] = CONFIDENTIALITE
        if p["handle"] == "retours":
            p["titre"], p["titre_nl"] = "Retours et remboursements", "Retourneren en terugbetalen"
            p["fr"] = p["fr"].replace("<h2>À savoir</h2>", REMBOURSEMENT_FR.strip() + "\n<h2>À savoir</h2>")
            p["nl"] = p["nl"].replace("<h2>Goed om te weten</h2>", REMBOURSEMENT_NL.strip() + "\n<h2>Goed om te weten</h2>")
        if p["handle"] == "conditions-generales-de-vente":
            p["fr"] = p["fr"].replace("Les textes, la mise en page, le nom Qosmi et la mascotte Mimi appartiennent à Deway BV.</p>",
                                      "Les textes, la mise en page, le nom Qosmi et la mascotte Mimi appartiennent à Deway BV. L'utilisation du site est régie par nos <a href=\"/pages/conditions-d-utilisation\">conditions d'utilisation</a>.</p>")
            p["nl"] = p["nl"].replace("De teksten, de vormgeving, de naam Qosmi en de mascotte Mimi behoren toe aan Deway BV.</p>",
                                      "De teksten, de vormgeving, de naam Qosmi en de mascotte Mimi behoren toe aan Deway BV. Het gebruik van de website valt onder onze <a href=\"/pages/conditions-d-utilisation\">gebruiksvoorwaarden</a>.</p>")
        if p["handle"] == "mentions-legales":
            p["fr"] = p["fr"].replace('<a href="/pages/confidentialite">politique de confidentialité</a>.</p>',
                                      '<a href="/pages/conditions-d-utilisation">conditions d\'utilisation</a> · <a href="/pages/confidentialite">politique de confidentialité</a> · <a href="/pages/cookies">politique de cookies</a> · <a href="/pages/accessibilite">déclaration d\'accessibilité</a>.</p>')
            p["nl"] = p["nl"].replace('<a href="/pages/confidentialite">privacybeleid</a>.</p>',
                                      '<a href="/pages/conditions-d-utilisation">gebruiksvoorwaarden</a> · <a href="/pages/confidentialite">privacybeleid</a> · <a href="/pages/cookies">cookiebeleid</a> · <a href="/pages/accessibilite">toegankelijkheidsverklaring</a>.</p>')
    PAGES.extend([UTILISATION, COOKIES, ACCESSIBILITE])


_maj()
