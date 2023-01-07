#!/bin/bash

# Définition de la racine de l'arborescence
root_dir="./docs/ransomware_notes/"

# Initialisation du compteur à 0
count=0

# Parcours de l'arborescence avec la commande "find"
find "$root_dir" -type f | while read f; do
  # Pour chaque fichier trouvé, on incrémente le compteur
  ((count++))
done

# Affichage du résultat
echo "Le nombre de fichiers dans l'arborescence est de $count"
