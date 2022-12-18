import os
import json


# Répertoire à scanner
dossier = './source/descriptions'

# Obtenir la liste des fichiers dans le répertoire
fichiers = os.listdir(dossier)

# Parcourir chaque fichier de la liste
for fichier in fichiers:
    # Extraire le nom du fichier sans l'extension
    group = os.path.splitext(fichier)[0]
    with open(dossier+'/'+fichier, 'r') as g:
    # Lire le contenu du fichier
        contenu = g.read()

    # Afficher le nom du fichier
    # Charger le tableau JSON à partir d'un fichier
    with open('groups.json', 'r') as f:
        tableau = json.load(f)

    index = -1  # Valeur par défaut si l'élément n'est pas trouvé
    for i, elem in enumerate(tableau):
        if elem['name'] == group:
            index = i
            break

    # Afficher l'index trouvé
    if index >= 0:
        print(group)
        print('L\'élément a été trouvé à l\'index ' + str(index))
        print(contenu)
        print('---')
        tableau[index]['description'] =  contenu
        with open('groups.json', 'w') as h:
            json.dump(tableau, h)


