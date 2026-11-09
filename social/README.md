# Réseaux sociaux Qosmi

- `lot1/` : lot n°1 (30 publications du 16/11 au 15/12/2026), avec les visuels finaux en 1080 × 1350 et `lot1.json` (dates, légendes, liste des visuels).
- `visuels_base.py`, `visuels_lot1.py` : génération des visuels (HTML → PNG avec Playwright, police Jost).
  - Ils ont besoin des flacons détourés, des photos de matières et des portraits ; ceux-ci restent dans le scratchpad de la session, à reprendre pour le lot 2.
- `legendes_lot1.py` : calendrier et légendes du lot.

**Sources** :
- les faits viennent d'Olfastory, qui autorise Qosmi à utiliser son site ;
- les photos de matières et les portraits viennent aussi d'Olfastory ;
- les flacons viennent des photos des fiches Qosmi.

**Publication** : elle se fera par l'API Meta, avec le secret `META_TOKEN`, pas encore créé.
