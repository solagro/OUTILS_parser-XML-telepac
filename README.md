# OUTILS_telepac-xml-reader

## Table des matières

- 🪧 [À propos](#à-propos)
- 📦 [Prérequis](#pré-requis)
- 🚀 [Installation](#installation)
- 🛠️ [Utilisation](#utilisation)
- 🤝 [Contribution](#contribution)
- 📚 [Documentation](#documentation)
- 🏷️ [Gestion des versions](#gestion-des-versions)
- 📝 [Licence](#licence)


## À propos
L'objectif de ce code est de pouvoir extraire les informations d'un fichier XML telepac d'un agriculteur.

## Pré-requis
[Liste des éléments nécessaires au bon fonctionnement du projet - éventuellement façon de les installer]

## Installation
[Étapes des commandes à lancer pour installer le projet en local]
1. Clone the repository
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```

2. Install packages
   ```sh
   brew install package
   ```

## Utilisation
### scan_xml.py
Outil de scan du fichier xml.
Affiche la liste des éléments du Tree xml.
```bash
usage:
  scan_xml.py [-h] [--precise] input_xml

optional arguments:
  -h, --help  show this help message and exit

required arguments:
  input_xml   nom du fichier XML Telepac à analyser
  --precise   Scan détaillé du fichier xml. TBD.

example:
  python src/scan_xml.py data/telepac_filename.xml
```

### read_xml.py
Outil d'extraction des données du xml vers un fichier excel.
Possible de visualiser les géométries à l'aide de Folium.
```bash
usage:
  read_xml.py [-h] [--visu_folium] --excel_filename EXCEL_FILENAME input_xml

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  input_xml             nom du fichier XML Telepac à analyser
  --visu_folium         Création de fichiers html pour la visualisation des géométries contenus dans le xml.
  --excel_filename      EXCEL_FILENAME

example:
  python read_xml.py data/telepac_filename.xml --visu_folium --excel_filename="output_excel.xlsx"
```


## Contribution
[Qui maintient, contribue au projet, qui est le responsable]

## Documentation
[Lien vers documentations externes ou documentation embarquée ici avec table des matières]

## Gestion des versions
[Page des Releases]

## Licence
[Voir le fichier [LICENSE](./LICENSE.md) du dépôt. https://choosealicense.com/]
