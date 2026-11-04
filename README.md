# Qosmi — mise à jour automatique du site

Dépôt **privé** de Deway BV. Toutes les heures (à h+17), GitHub Actions :

1. lit la liste du compte grossiste SoleLuna (wholesale-perfumes.eu) ;
2. regroupe les formats par parfum (une fiche, plusieurs formats : 30 ml / 50 ml / 100 ml – testeur…) ;
3. compare avec la boutique Shopify et n'envoie que les différences : stock, prix et coût par format,
   nouveaux formats, nouveaux parfums (en brouillon tant que le site n'est pas ouvert) ; un format qui
   disparaît passe à stock 0, rien n'est jamais supprimé.

Si la liste est illisible ou anormalement courte, rien n'est modifié. Le passage s'arrête si le dépôt devient public.

## Accès (Settings → Secrets and variables → Actions)
`SOLELUNA_EMAIL`, `SOLELUNA_PASSWORD`, `SHOPIFY_BOUTIQUE`, `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET`,
`WF_URL` (liste Wholesale-Fragrances, pour les photos des nouveaux produits).

## Réglages
`config/site.json` : prix provisoires (envoi, bénéfice, TVA), délai affiché, statut des nouvelles fiches
(`DRAFT` avant l'ouverture, `ACTIVE` ensuite).

## Lancer à la main
Onglet **Actions** → « Qosmi - mise a jour du site » → **Run workflow** (case « Essai » pour ne rien envoyer).
Le résumé de chaque passage s'affiche sur la page du passage ; le détail est dans l'artefact « journal ».
