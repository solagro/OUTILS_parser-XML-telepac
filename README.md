# Project Overview
Comment exploiter un fichier Telepac en .xml ?

# Installation Instructions
TBD

# Usage Guide



## scan_xml.py
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
  python read_xml.py telepac_filename.xml
```




## read_xml.py
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
  --excel_filename EXCEL_FILENAME

example:
  python read_xml.py telepac_filename.xml --visu_folium --excel_filename="output_excel.xlsx"
```
