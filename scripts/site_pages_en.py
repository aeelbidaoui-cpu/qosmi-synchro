"""Pages légales Qosmi — version anglaise (22/11/2026, Amine : « oui vasy », version anglaise du site).
Traduction fidèle des pages françaises de scripts/site_pages_contenu.py (le texte français fait foi en cas de doute).
Les valeurs entre {accolades} viennent de config/site.json et de ENTREPRISE (site_pages_contenu.py)."""

ADRESSE_EN = "Ijsbergstraat 73, 1701 Dilbeek, Belgium"

PAGES_EN = {
    # ------------------------------------------------------------------ CGV
    "conditions-generales-de-vente": {
        "handle_en": "terms-and-conditions-of-sale", "titre_en": "Terms and conditions of sale",
        "en": """
<p><em>Version of {date_en}.</em></p>
<p><em>This English version is provided for convenience. In case of doubt, the French version prevails.</em></p>
<h2>1. Who are we?</h2>
<p>1.1 The website qosmi.be (“the site”) is operated by <strong>Deway BV</strong>, a private limited company under Belgian law, {adresse_en}, company number {bce}, VAT {tva} (“Qosmi”, “we”). Qosmi is the fragrance and cosmetics shop of Deway BV.</p>
<p>1.2 Customer service: <a href="mailto:{email}">{email}</a>. We reply within 2 working days.</p>
<p>1.3 These terms apply to every order placed on the site by a consumer, i.e. a natural person buying for private purposes. By placing an order, you accept them. The applicable version is the one in force at the time of your order; you can save or print it.</p>
<p>1.4 To order, you must be at least 18 years old or act with the consent of your legal representative.</p>

<h2>2. Our products</h2>
<p>2.1 All our products are <strong>genuine, brand-new</strong> branded products, bought from distributors and trade suppliers established in the European Union. Unless stated otherwise, Qosmi is not an authorised retailer of the brands and is not affiliated with any of them.</p>
<p>2.2 <strong>Testers.</strong> Products whose name contains “tester” are genuine, brand-new products with the same contents as the boxed version, but delivered in plain packaging, sometimes without a cap and with a mention such as “demonstration” or “not for sale”. Their price reflects this presentation.</p>
<p>2.3 Photos and descriptions are for guidance only. Packaging may vary between the brand's production batches, without the contents changing.</p>
<p>2.4 Products are offered while stocks last. They are shipped from our logistics partner's warehouse in the European Union.</p>
<p>2.5 If an ordered product turns out to be unavailable, we will inform you without delay. You can wait, choose another product or cancel; if you cancel, you will be refunded within 14 days at the latest.</p>
<p>2.6 Fragrances are flammable products. Keep them away from heat and light and use them as indicated on the packaging. Check the list of ingredients before use if you are prone to allergies.</p>

<h2>3. Prices, ordering and payment</h2>
<p>3.1 Prices are shown in euros, <strong>including VAT</strong>, excluding delivery costs. Delivery costs are shown before you confirm your order. The applicable price is the one displayed at the time of ordering.</p>
<p>3.2 In the event of an obvious pricing error (a price unrelated to the product's value, due to a technical or input error), we may cancel the order and refund you in full; you will be informed without delay.</p>
<p>3.3 The contract is concluded when you confirm your order and payment after checking the summary (products, prices, delivery costs, total). You receive an order confirmation by email.</p>
<p>3.4 We may refuse or cancel an order for a legitimate reason: suspected fraud, a previous payment dispute, quantities that are abnormal for private use. You will be informed and refunded in full.</p>
<p>3.5 Payment is made online, when ordering, using the methods offered at checkout (for example Bancontact, Visa, Mastercard, Apple Pay, Google Pay). Payments are processed by a secure payment provider; we never have access to your card details.</p>
<p>3.6 The invoice is sent by email. Products remain our property until full payment.</p>

<h2>4. Delivery</h2>
<p>4.1 We deliver to <strong>Belgium</strong>, the <strong>Netherlands</strong>, <strong>Luxembourg</strong>, <strong>France</strong>, <strong>Spain</strong>, <strong>Portugal</strong>, <strong>Italy</strong>, <strong>Germany</strong> and <strong>Poland</strong>. Delivery costs per order, including VAT:</p>
<ul>
<li><strong>Belgium</strong>: Mondial Relay pick-up point {frais_livraison_en}, free from 2 items in the same order; home delivery €6.95;</li>
<li><strong>Netherlands</strong>: Mondial Relay pick-up point €3.95, free from 2 items in the same order;</li>
<li><strong>Luxembourg</strong>: Mondial Relay pick-up point €3.95, free from 2 items in the same order; home delivery €12.95;</li>
<li><strong>France</strong>: Mondial Relay pick-up point €4.95; home delivery €12.95;</li>
<li><strong>Spain and Portugal</strong>: Mondial Relay pick-up point €5.95; home delivery €12.95;</li>
<li><strong>Italy</strong>: Mondial Relay pick-up point €5.95;</li>
<li><strong>Germany</strong>: Mondial Relay pick-up point €7.95; home delivery €12.95;</li>
<li><strong>Poland</strong>: Mondial Relay pick-up point €7.95.</li>
</ul>
<p>A parcel for pick-up point delivery is left at the Mondial Relay pick-up point closest to the delivery address provided.</p>
<p>4.2 Delivery time: <strong>{delai_total_en}</strong> in Belgium, <strong>{delai_etranger_en}</strong> in the Netherlands, Luxembourg and France, <strong>{delai_lointain_en}</strong> in the other countries, from confirmation of payment. Your order's delivery time is confirmed in the order confirmation email. Unless another time has been agreed, delivery takes place no later than 30 days after the contract is concluded.</p>
<p>4.3 If delivery is late beyond the agreed time, you may ask us to deliver within a reasonable additional period; failing that, you may cancel the order and be refunded without delay.</p>
<p>4.4 The parcel is handed over by a carrier with tracking, at the address you provide. Please check it carefully: a parcel returned because of a wrong address or not collected may be re-sent for new delivery costs.</p>
<p>4.5 The risk of loss or damage passes to you when you, or a person you designate other than the carrier, take physical possession of the parcel. A visibly damaged parcel should, where possible, be refused or accepted with reservations, and reported to us quickly with photos.</p>

<h2>5. Right of withdrawal</h2>
<p>5.1 You have <strong>14 calendar days</strong> to withdraw, without giving a reason and without penalty. This period runs from the day you, or a person you designate other than the carrier, take physical possession of the product; for an order delivered in several parcels, from receipt of the last one.</p>
<p>5.2 To exercise this right, inform us of your decision before the period ends by a clear statement, by email to <a href="mailto:{email}">{email}</a> or by post, for example using the form on the <a href="/pages/retours">Returns</a> page (its use is not mandatory).</p>
<p>5.3 Send the products back without undue delay, no later than 14 days after informing us of your decision, to the address given in article 1.1. <strong>Return costs are borne by you.</strong> The products travel at your risk; tracked shipping is recommended.</p>
<p>5.4 We refund all payments received, including the original delivery costs, no later than 14 days after being informed of your withdrawal, using the payment method used, at no cost to you. We may withhold the refund until we receive the products or proof that they have been sent, whichever is earlier.</p>
<p>5.5 <strong>Exception: unsealed products.</strong> For reasons of hygiene and health protection, the right of withdrawal does not apply to sealed products (plastic film, seal or other closure) whose seal you have removed after delivery (article VI.53, 5° of the Belgian Code of Economic Law).</p>
<p>5.6 <strong>Testers and unsealed products.</strong> The right of withdrawal applies. Only handle the product as far as necessary to establish its nature and characteristics. A sprayed or used product loses value: you are then liable for this loss of value, which may amount to the full value of the product and is deducted from the refund.</p>

<h2>6. Legal guarantee and liability</h2>
<p>6.1 Products benefit from the <strong>two-year legal guarantee of conformity</strong> from delivery (articles 1649bis and following of the former Belgian Civil Code). A defect appearing within two years is presumed to have existed at delivery, unless proven otherwise.</p>
<p>6.2 Report the defect to <a href="mailto:{email}">{email}</a> within <strong>two months</strong> of the day you noticed it, with a description and, if possible, photos. Under the legal conditions, you are entitled to a replacement of the product, or otherwise to a price reduction or a refund.</p>
<p>6.3 The following are not defects of conformity: normal evaporation of an opened product, deterioration due to improper storage (heat, light), improper use, or a personal sensitivity to an ingredient listed on the packaging.</p>
<p>6.4 We are responsible for the proper performance of the contract. We cannot be held liable for indirect damage or in the event of force majeure. These limits do not apply in the event of fraud, gross negligence or bodily injury, and do not reduce the rights granted to you by law.</p>

<h2>7. Personal data, complaints and applicable law</h2>
<p>7.1 We process your data to fulfil your order, provide customer service and comply with our legal obligations, as explained in our <a href="/pages/confidentialite">privacy policy</a>.</p>
<p>7.2 Brand names and logos belong to their owners and are only used to identify the products sold. The texts, layout, the Qosmi name and the Mimi mascot belong to Deway BV. Use of the site is governed by our <a href="/pages/conditions-d-utilisation">terms of use</a>.</p>
<p>7.3 Any complaint should be sent to <a href="mailto:{email}">{email}</a>. We reply within 5 working days.</p>
<p>7.4 If no amicable solution is found, you can contact the Belgian <strong>Consumer Mediation Service</strong> free of charge, boulevard du Roi Albert II 8 bte 1, 1000 Brussels, <a href="https://mediationconsommateur.be">mediationconsommateur.be</a>.</p>
<p>7.5 These terms and the sales concluded on the site are governed by Belgian law, without depriving you of the protection of the mandatory rules of the country where you habitually reside. Disputes fall under the courts with jurisdiction according to the legal rules, including those of your place of residence.</p>
<p>7.6 If a clause is declared void, the others remain applicable.</p>
"""},
    # ------------------------------------------------------------------ Livraison
    "livraison": {
        "handle_en": "shipping", "titre_en": "Shipping",
        "en": """
<figure class="qk-page-image"><img src="{img_livraison_colis}" alt="Qosmi parcels in kraft cardboard ready to ship" width="2400" height="1018" loading="eager" style="width:100%;height:auto;border-radius:12px"></figure>
<p><strong>We deliver to 9 European countries, to a Mondial Relay pick-up point or to your door.</strong> With pick-up point delivery, the parcel is left at the pick-up point closest to your address.</p>
<table>
<thead><tr><th>Country</th><th>Pick-up point</th><th>Home delivery</th><th>Delivery time</th></tr></thead>
<tbody>
<tr><td>Belgium</td><td>{frais_livraison_en}, free from 2 items</td><td>€6.95</td><td>{delai_total_en}</td></tr>
<tr><td>Netherlands</td><td>€3.95, free from 2 items</td><td>–</td><td>{delai_etranger_en}</td></tr>
<tr><td>Luxembourg</td><td>€3.95, free from 2 items</td><td>€12.95</td><td>{delai_etranger_en}</td></tr>
<tr><td>France</td><td>€4.95</td><td>€12.95</td><td>{delai_etranger_en}</td></tr>
<tr><td>Spain</td><td>€5.95</td><td>€12.95</td><td>{delai_lointain_en}</td></tr>
<tr><td>Portugal</td><td>€5.95</td><td>€12.95</td><td>{delai_lointain_en}</td></tr>
<tr><td>Italy</td><td>€5.95</td><td>–</td><td>{delai_lointain_en}</td></tr>
<tr><td>Germany</td><td>€7.95</td><td>€12.95</td><td>{delai_lointain_en}</td></tr>
<tr><td>Poland</td><td>€7.95</td><td>–</td><td>{delai_lointain_en}</td></tr>
</tbody>
</table>
<p>Prices include VAT, per order.</p>
<h2>Delivery times</h2>
<p>Delivery times are counted in working days from confirmation of payment.</p>
<p>Your order's delivery time is confirmed in the order confirmation email.</p>
<h2>Tracking</h2>
<p>As soon as your parcel ships, you receive an email with the tracking link.</p>
<h2>A problem with your parcel?</h2>
<p>Damaged, late or incomplete parcel: write to us at <a href="mailto:{email}">{email}</a> with your order number and, if possible, photos. Details are in our <a href="/pages/conditions-generales-de-vente">terms and conditions of sale</a> (article 4).</p>
"""},
    # ------------------------------------------------------------------ Retours
    "retours": {
        "handle_en": "returns", "titre_en": "Returns and refunds",
        "en": """
<p>You have <strong>14 days</strong> after receipt to change your mind.</p>
<h2>How to return a product</h2>
<ol>
<li>Write to us at <a href="mailto:{email}">{email}</a> with your order number and the product(s) concerned (or send the form below).</li>
<li>Send the parcel back within the following 14 days, at your own cost, to the address given in the form below. Tracked shipping is recommended.</li>
<li>We refund you, including the original delivery costs, no later than 14 days after your request, once we receive the parcel or proof that it has been sent.</li>
</ol>
<h2>Refund</h2>
<ul>
<li><strong>What is refunded</strong>: the price of the returned products and the original delivery costs (if the whole order is returned, up to the cost of the standard delivery method).</li>
<li><strong>When</strong>: no later than 14 days after your withdrawal request; we may wait until we receive the parcel or proof that it has been sent.</li>
<li><strong>How</strong>: using the payment method used for the order, at no cost to you.</li>
<li><strong>Damaged or faulty product, or a mistake on our part</strong>: replacement or full refund, with return costs paid by us (two-year legal guarantee).</li>
</ul>
<h2>Good to know</h2>
<ul>
<li>A <strong>sealed</strong> product (film, seal) whose seal has been removed cannot be taken back, for hygiene reasons.</li>
<li>A sprayed or used product loses value: this loss of value may be deducted from the refund.</li>
<li>Faulty product or a mistake on our part: write to us, return costs are then paid by us.</li>
</ul>
<h2>Withdrawal form</h2>
<p>(Complete and return only if you wish to withdraw from the contract.)</p>
<p>To Deway BV (Qosmi), {adresse_en}, {email}:<br>
I hereby give notice that I withdraw from my contract for the sale of the following product(s):<br>
Ordered on / received on:<br>
Order number:<br>
Name:<br>
Address:<br>
Signature (only if this form is sent on paper):<br>
Date:</p>
"""},
    # ------------------------------------------------------------------ Confidentialité
    "confidentialite": {
        "handle_en": "privacy-policy", "titre_en": "Privacy policy",
        "en": """
<p><em>Version of {date_en}.</em></p>
<p><em>This English version is provided for convenience. In case of doubt, the French version prevails.</em></p>
<p>We only collect the data needed to sell and deliver our products to you, and to comply with the law. We never sell your data.</p>
<h2>1. Who is responsible for your data?</h2>
<p>Deway BV (Qosmi), company number {bce}. For any question about your data: <a href="mailto:{email}">{email}</a>.</p>
<h2>2. Which data, why, and on what legal basis?</h2>
<table>
<thead><tr><th scope="col">Situation</th><th scope="col">Data</th><th scope="col">Why</th><th scope="col">Legal basis (GDPR)</th></tr></thead>
<tbody>
<tr><td>Order</td><td>Name, delivery and billing address, email, products bought, amount. Phone number only if you give it (optional).</td><td>Process, deliver and invoice your order; send you the confirmation and tracking.</td><td>Performance of the contract (art. 6.1.b)</td></tr>
<tr><td>Payment</td><td>Payment data, processed directly by the payment provider. We never see your card details.</td><td>Collect payment, prevent fraud.</td><td>Performance of the contract; legitimate interest in preventing fraud (art. 6.1.b and f)</td></tr>
<tr><td>Invoice and accounting</td><td>Invoice data.</td><td>Keep our accounts and meet our VAT obligations.</td><td>Legal obligation (art. 6.1.c)</td></tr>
<tr><td>Customer account (optional)</td><td>Email, name, saved addresses, order history.</td><td>Let you follow your orders.</td><td>Performance of the contract (art. 6.1.b)</td></tr>
<tr><td>Customer service, returns</td><td>Your messages, order number, photos you send us.</td><td>Reply, handle a return or a guarantee claim.</td><td>Performance of the contract; legal obligation (guarantee)</td></tr>
<tr><td>Site chat (if you use it)</td><td>Your messages and the replies, the page viewed and the contents of your cart during the conversation; your name and email if you ask to talk to a team member.</td><td>Answer your questions and advise you. The first replies are written automatically by Shopify's artificial intelligence assistant based on the shop's public information; a team member can take over the conversation.</td><td>Pre-contractual measures and performance of the contract; legitimate interest in answering visitors (art. 6.1.b and f)</td></tr>
<tr><td>Newsletter (if you sign up)</td><td>Your email and the date of your consent.</td><td>Send you our monthly newsletter.</td><td>Consent (art. 6.1.a), which you can withdraw at any time</td></tr>
<tr><td>Site operation and security</td><td>Technical data (IP address, browser), strictly necessary cookies.</td><td>Make the cart and checkout work, secure the site.</td><td>Legitimate interest (art. 6.1.f)</td></tr>
<tr><td>Audience measurement (only if you accept it)</td><td>Pages viewed, interactions, analytics cookie data.</td><td>Understand how the site is used in order to improve it.</td><td>Consent (art. 6.1.a)</td></tr>
<tr><td>Advertising on Facebook and Instagram (only if you accept marketing cookies)</td><td>Pages and products viewed, additions to cart, purchases (products, amount), cookie identifiers, IP address and browser. When you buy, your email and phone number are sent in encrypted (hashed) form, never in plain text.</td><td>Measure the results of our ads and show them to people likely to be interested.</td><td>Consent (art. 6.1.a), which you can withdraw at any time via the “Cookie preferences” link</td></tr>
</tbody>
</table>
<p>We make no automated decisions with legal effects concerning you, except the payment provider's automatic fraud analysis, which may block a suspicious payment. You can then contact us for a human review.</p>
<p>The chat's automatic replies may contain errors: they do not replace our terms and conditions or our policies, which prevail. The assistant has no access to your payment data. Do not share sensitive data in it (health, bank details, passwords).</p>
<h2>3. Who receives your data?</h2>
<ul>
<li><strong>Shopify</strong>, which hosts the shop, processes payments, sends order emails and provides the site chat and its artificial intelligence assistant (Shopify International Limited, Ireland, and its sub-processors);</li>
<li><strong>the carrier</strong> delivering your parcel (name, address, email or phone number for the delivery notice);</li>
<li><strong>our logistics partner established in the European Union</strong>, which prepares and ships orders (name and delivery address only);</li>
<li><strong>our accountant</strong> and, where required by law, the authorities;</li>
<li><strong>Meta Platforms Ireland Limited</strong> (Facebook, Instagram), only if you accept marketing cookies. For the collection of this data on our site, Meta and we are joint controllers; Meta alone is responsible for what it does with it afterwards, under its <a href="https://www.facebook.com/privacy/policy">privacy policy</a>. You can also manage this data in the “Off-Meta activity” settings of your Facebook or Instagram account.</li>
</ul>
<p>Some of Shopify's sub-processors process data outside the European Union, in particular in Canada (a country recognised as offering adequate protection) and in the United States. These transfers are covered by the safeguards provided for by the GDPR (adequacy decision or standard contractual clauses). Meta may transfer data to the United States under the EU-U.S. Data Privacy Framework.</p>
<h2>4. For how long?</h2>
<ul>
<li>Order data and invoices: for the legal retention periods for accounting and tax documents;</li>
<li>customer account: as long as the account exists, then deleted on request or after 3 years without an order;</li>
<li>messages to customer service and chat conversations: 3 years after the last exchange, unless a dispute is ongoing;</li>
<li>newsletter: until you unsubscribe;</li>
<li>cookies: see our <a href="/pages/cookies">cookie policy</a>.</li>
</ul>
<h2>5. Your rights</h2>
<p>You can request access to your data, its rectification, its erasure, restriction of processing and portability, and object to processing based on our legitimate interest. You can withdraw your consent at any time, without affecting what was done before. Write to <a href="mailto:{email}">{email}</a>; we reply within one month. We may ask you to prove your identity.</p>
<p>You can also lodge a complaint with the Belgian <strong>Data Protection Authority</strong>, rue de la Presse 35, 1000 Brussels, <a href="https://www.autoriteprotectiondonnees.be">autoriteprotectiondonnees.be</a>.</p>
<h2>6. Changes</h2>
<p>We update this policy if our practices change (for example, adding a new measurement or advertising tool). The version date is shown at the top of the page.</p>
"""},
    # ------------------------------------------------------------------ Mentions légales
    "mentions-legales": {
        "handle_en": "legal-notice", "titre_en": "Legal notice",
        "en": """
<p><strong>Qosmi</strong> is the online fragrance and cosmetics shop of:</p>
<p><strong>Deway BV</strong><br>
Private limited company under Belgian law<br>
Registered office: {adresse_en}<br>
Company number (BCE/KBO): {bce} – RPR Brussels<br>
VAT: {tva}<br>
Email: <a href="mailto:{email}">{email}</a></p>
<p><strong>Hosting</strong>: Shopify International Limited, Victoria Buildings, 2nd Floor, 1-2 Haddington Road, Dublin 4, D04 XN32, Ireland.</p>
<p>Product brands and logos belong to their owners. The Qosmi name, the Mimi mascot, and the site's texts and layout belong to Deway BV.</p>
<p>See also: <a href="/pages/conditions-generales-de-vente">terms and conditions of sale</a> · <a href="/pages/conditions-d-utilisation">terms of use</a> · <a href="/pages/confidentialite">privacy policy</a> · <a href="/pages/cookies">cookie policy</a> · <a href="/pages/accessibilite">accessibility statement</a>.</p>
"""},
    # ------------------------------------------------------------------ Conditions d'utilisation
    "conditions-d-utilisation": {
        "handle_en": "terms-of-use", "titre_en": "Terms of use",
        "en": """
<p><em>Version of {date_en}.</em></p>
<p>These terms govern the use of the website qosmi.be, operated by Deway BV ({bce}). Purchases are governed by our <a href="/pages/conditions-generales-de-vente">terms and conditions of sale</a>.</p>
<h2>1. Access to the site</h2>
<p>The site is free to access. We do our best to keep it available and accurate, but an interruption (maintenance, outage) or an error remains possible. Prices and stock shown are updated regularly; only those confirmed at the time of ordering are binding.</p>
<h2>2. Customer account</h2>
<p>The customer account is optional. You are responsible for the accuracy of your data and for access to your email address, which is used to log in. Let us know if you think someone is using your account.</p>
<h2>3. What is not allowed</h2>
<ul>
<li>using the site for illegal or fraudulent purposes;</li>
<li>trying to disrupt, overload or bypass the site's security;</li>
<li>copying the site's own content (texts, layout, the Qosmi name, the Mimi mascot) for any use other than personal;</li>
<li>buying for professional resale: our sales are reserved for consumers.</li>
</ul>
<h2>4. Artificial intelligence assistants and agents</h2>
<p>You may use an AI assistant or agent to browse the site, compare our products or prepare an order. An order placed through such a tool is placed in your name: you remain the person who concludes the contract and you keep all your consumer rights, including the right of withdrawal. Automated access must remain reasonable and must not overload the site.</p>
<h2>5. Content and links</h2>
<p>Product descriptions are for guidance only. Brands and logos belong to their owners. Links to other sites are provided for your convenience; we are not responsible for their content.</p>
<h2>6. Liability</h2>
<p>Our liability related to the use of the site is limited to direct damage caused by our fault. This limit does not apply in the event of fraud, gross negligence or bodily injury, and does not reduce your consumer rights.</p>
<h2>7. Changes and applicable law</h2>
<p>We may change these terms; the version date is shown at the top of the page. Belgian law applies, without depriving you of the protection of the mandatory rules of your country of residence. Contact: <a href="mailto:{email}">{email}</a>.</p>
"""},
    # ------------------------------------------------------------------ Cookies
    "cookies": {
        "handle_en": "cookie-policy", "titre_en": "Cookie policy",
        "en": """
<p><em>Version of {date_en}.</em></p>
<p>A cookie is a small file that the site stores in your browser. Without your consent, we only use strictly necessary cookies. The others are only placed if you accept them in the cookie banner.</p>
<h2>Your choices</h2>
<p>On your first visit, the banner lets you accept or refuse, just as easily, or choose by category. You can change your mind at any time with the <strong>“Cookie preferences”</strong> link at the bottom of every page. Refusing does not prevent you from ordering.</p>
<h2>Cookies used</h2>
<table>
<thead><tr><th scope="col">Cookie</th><th scope="col">What it is for</th><th scope="col">Category</th><th scope="col">Duration</th></tr></thead>
<tbody>
<tr><td>_shopify_essential</td><td>Session, checkout and fraud protection</td><td>Necessary</td><td>1 year</td></tr>
<tr><td>_shopify_cmp</td><td>Remembers your cookie choices</td><td>Necessary</td><td>1 year</td></tr>
<tr><td>cart</td><td>Contents of your cart</td><td>Necessary</td><td>2 weeks</td></tr>
<tr><td>cart_currency</td><td>Cart currency after an order</td><td>Necessary</td><td>2 weeks</td></tr>
<tr><td>localization</td><td>Shop country and language</td><td>Necessary</td><td>1 year</td></tr>
<tr><td>discount_code</td><td>Discount code received via a link</td><td>Necessary</td><td>Session</td></tr>
<tr><td>_shopify_test</td><td>Checks that your browser accepts cookies</td><td>Necessary</td><td>1 minute</td></tr>
<tr><td>__Host-Http-shop_binding</td><td>Connection with Shop (if you use it)</td><td>Necessary</td><td>3 hours</td></tr>
<tr><td>_shopify_analytics</td><td>Visit statistics for the shop and checkout</td><td>Analytics (with your consent)</td><td>1 year</td></tr>
<tr><td>_shopify_marketing</td><td>Marketing data for the shop and checkout</td><td>Marketing (with your consent)</td><td>1 year</td></tr>
<tr><td>_fbp</td><td>Meta pixel: recognises your browser to measure our Facebook and Instagram ads</td><td>Marketing (with your consent)</td><td>3 months</td></tr>
<tr><td>_fbc</td><td>Meta pixel: remembers that you arrived through one of our ads</td><td>Marketing (with your consent)</td><td>3 months</td></tr>
</tbody>
</table>
<p>The “_shopify” and cart cookies are placed by Shopify, the platform that hosts our shop. The “_fbp” and “_fbc” cookies belong to Meta's pixel (Facebook, Instagram); they are only placed, and no data is sent to Meta from the site, if you accept marketing cookies. During payment, the payment provider may also use cookies needed to prevent fraud. If we add another tool, this page and the banner will be updated beforehand.</p>
<h2>Blocking cookies in your browser</h2>
<p>You can also delete or block cookies in your browser settings. Without the necessary cookies, the cart and checkout do not work.</p>
<p>Questions: <a href="mailto:{email}">{email}</a>. See also our <a href="/pages/confidentialite">privacy policy</a>.</p>
"""},
    # ------------------------------------------------------------------ Accessibilité
    "accessibilite": {
        "handle_en": "accessibility-statement", "titre_en": "Accessibility statement",
        "en": """
<p><em>Version of {date_en}.</em></p>
<p>We want everyone to be able to discover and buy our products, including with a screen reader, with the keyboard only, by enlarging the text or with a digital assistant.</p>
<h2>What we do</h2>
<ul>
<li>We aim for level AA of the WCAG 2.1 guidelines, included in the European standard EN 301 549.</li>
<li>Every product photo has alternative text describing the product; purely decorative images are ignored by screen readers.</li>
<li>Text colours have a contrast of at least 4.5:1 with their background (3:1 for large headings and field outlines).</li>
<li>The site can be used with the keyboard, buttons and links have clear names, and pages have structured headings.</li>
<li>Product information (brand, size, price, availability, EAN code) is also published as structured data, readable by assistive tools and digital agents.</li>
</ul>
<h2>Compliance status</h2>
<p>The site is <strong>partially compliant</strong>: it has not yet been externally audited. Known limitations: some product descriptions use the manufacturer's technical terms; the checkout page is provided by our platform (Shopify), and we do not control all of its content.</p>
<h2>A problem?</h2>
<p>If some content is inaccessible to you, write to us at <a href="mailto:{email}">{email}</a>: we will reply within 5 working days and offer an alternative (for example, placing the order with you by email). You can also report a problem to the Belgian FPS Economy via the <a href="https://pointdecontact.belgique.be">Contact Point</a>.</p>
"""},
}
