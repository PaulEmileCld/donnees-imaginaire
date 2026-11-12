# Ouvrir la carte dans Gephi

Trois fichiers, à importer avec **Fichier → Importer un tableur (CSV)** :

1. `noeuds.csv` → « Table des nœuds ». 15 096 mots : catégorie, fréquence, rang de pertinence, oral/écrit, époque, vues Wikipédia, position t-SNE (x, y), et une colonne de communauté par résolution (`communaute_res_0_1` … `communaute_res_7_0`).
2. **Un des deux fichiers de liens**, en « Table des liens », en choisissant « Ajouter à l'espace de travail existant » :
   - `liens_associations.csv` : 150 874 associations JeuxDeMots (les 10 plus fortes de chaque mot, orientées, poids = force donnée par les joueurs).
   - `liens_proximite.csv` : 112 279 liens entre mots au profil d'associations semblable (10 voisins par mot, non orientés, poids = ressemblance de 0 à 1).

Conseils de mise en page :
- Associations : ForceAtlas2 avec **LinLog** et **Dissuade Hubs** cochés, sinon les mots-domaines (médecine, droit, linguistique) aspirent tout. Filtrer d'abord les liens de poids < 100 allège beaucoup.
- Proximité : ForceAtlas2 normal, gravité 1, échelle 2 à 10. Les grappes (vêtements, cuisine, culte, musique…) se détachent seules.
- Couleur : Apparence → Nœuds → Partition → une colonne `communaute_res_…`.

Les aperçus `apercu_gephi_*.png` ont été calculés hors de Gephi, avec le même algorithme, sur les 5 000 mots les plus pertinents.

Tout le réseau (30 078 mots, 2,36 millions de liens) est dans `resultats_usage/noeuds.csv` et `resultats_usage/liens.csv.gz` : trop lourd pour Gephi d'un coup.
