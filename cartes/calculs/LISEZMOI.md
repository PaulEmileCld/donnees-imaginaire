# Calculs intermédiaires (pour ne pas tout recalculer)

- `data_niv.json.gz` : données de la carte 3D par l'usage (15 096 mots rangés par pertinence, positions t-SNE, 11 niveaux de communautés, associations).
- `vecteurs_svd.npz` : empreinte de 150 nombres par mot (PPMI + SVD). `Z` dans l'ordre de `keep` (indices dans la liste triée des Id de `resultats_usage/noeuds.csv`), `Z_ordre` dans l'ordre de `data_niv`.
- `fa2np_15096.json.gz` : positions ForceAtlas2 de la carte hybride (sol de proximité), 27 minutes de calcul.
- `arbres.json.gz`, `arbres_pos.json.gz` : arbre couvrant maximal et Pathfinder (2 000 mots) avec leurs positions.
- `faisceaux.json.gz` : liens regroupés en faisceaux (2 000 mots).
- `niveaux_gephi.json.gz` : appartenance aux communautés pour chaque résolution.
