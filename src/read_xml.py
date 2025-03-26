"""
Tentative de lecture d'un fichier xml TELEPAC pour en extraire les informations.

Usage:
    python read_xml.py input_xml [--visu_folium] [--excel_filename FILE] [--output_dir OUTPUT_DIR]
"""

import argparse
import xml.etree.ElementTree as ET
import os
import pandas as pd
import geopandas as gpd
import folium

# Importer les fonctions d'extraction nécessaires
from extract_functions.extract_aides_pac import extract_aides_pac
from extract_functions.extract_animaux import extract_animaux
from extract_functions.extract_bio import extract_bio
from extract_functions.extract_demandeur import extract_demandeur
from extract_functions.extract_ilots import extract_ilots
from extract_functions.extract_maec import extract_maec
from extract_functions.extract_parcelles import extract_parcelles
from extract_functions.extract_sna import extract_sna
from extract_functions.extract_zdh import extract_zdh


def usage() -> argparse.Namespace:
    """Parse the options provided on the command line.

    Returns:
        argparse.Namespace: The parameters provided on the command line.
    """

    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "input_xml",
        type=str,
        action="store",
        help="nom du fichier XML Telepac à analyser",
    )
    required_args.add_argument(
        "--visu_folium",
        action="store_true",
        default=False,
        help="Création de html Folium pour la visualisation des géométries contenues dans le xml.",
    )
    required_args.add_argument(
        "--excel_filename",
        type=str,
        action=check_extension({"xlsx"}),
        default="output.xlsx",
        required=False,
        help="Nom du fichier excel contenant l'extraction du xml. Extension xlsx obligatoire",
    )
    required_args.add_argument(
        "--output_dir",
        type=str,
        action="store",
        default=os.getcwd(),
        required=False,
        help="Nom du répertoire de sortie permettant de stocker les visus et fichier excel",
    )
    return parser.parse_args()


def check_extension(choices):
    """
    Vérifier le type d'extension parmi une liste définie lors du parsage des arguments
    """

    class Act(argparse.Action):
        def __call__(self, pars, namespace, fname, option_string=None):
            ext = os.path.splitext(fname)[1][1:]
            if ext not in choices:
                option_string = f"({option_string})" if option_string else ""
                pars.error(f"file doesn't end with {choices}{option_string}")
            else:
                setattr(namespace, self.dest, fname)

    return Act


def visu_folium(
    gdf, geo_name="geometry", fillcolor="red", color="black", html_output="output.html"
):
    """
    Visualisation dynamique avec Folium
    """
    if not gdf.empty:
        # Calcul du centroïd des géométries pour centrer l'affichage
        union = gdf.union_all()
        centroid = union.centroid

        m = folium.Map(
            location=(centroid.y, centroid.x), zoom_start=12, tiles="CartoDB positron"
        )
        for _, r in gdf.iterrows():
            sim_geo = gpd.GeoSeries(r[geo_name])
            geo_j = sim_geo.to_json()
            geo_j = folium.GeoJson(
                data=geo_j,
                style_function=lambda x: {
                    "fillColor": fillcolor,
                    "color": color,
                },
            ).add_to(m)
        m.save(html_output)


def ajouter_onglet(data, excel_file, onglet):
    """
    Ajout d'un nouvel onglet à la feuille Excel
    uniquement si le tableau n'est pas vide
    """
    if not data.empty:
        data.to_excel(excel_file, sheet_name=onglet, index=False)


if __name__ == "__main__":

    # Import des paramètres
    args = usage()
    XML_FILE = args.input_xml
    OUTPUT_DIR = args.output_dir
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    EXCEL_FILENAME = f"{args.output_dir}/{args.excel_filename}"
    CREATE_VISU_HTML = args.visu_folium

    # Définition des namespace
    NAMESPACE = "{urn:x-telepac:fr.gouv.agriculture.telepac:echange-producteur}"
    NAMESPACE_GML = "{http://www.opengis.net/gml}"

    # Traitements des ilots
    xml = ET.parse(XML_FILE).getroot()
    gdf_ilots = extract_ilots(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des parcelles
    gdf_parcelles = extract_parcelles(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des éléments bio
    gdf_bio = extract_bio(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des maec - elements surfaciques
    gdf_maec = extract_maec(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des sna-declaree
    gdf_sna = extract_sna(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des zdh-declaree
    gdf_zdh = extract_zdh(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des animaux
    df_animaux = extract_animaux(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des informations du demandeur
    df_demandeur = extract_demandeur(xml, NAMESPACE, NAMESPACE_GML)

    # Traitements des demandes d'aide
    df_aide_pac = extract_aides_pac(xml, NAMESPACE, NAMESPACE_GML)

    if CREATE_VISU_HTML:
        # Création de visu dynamique avec Folium
        visu_folium(gdf_ilots, fillcolor="red", html_output=f"{OUTPUT_DIR}/ilots.html")
        visu_folium(
            gdf_parcelles, fillcolor="blue", html_output=f"{OUTPUT_DIR}/parcelles.html"
        )
        visu_folium(gdf_bio, fillcolor="green", html_output=f"{OUTPUT_DIR}/bio.html")
        visu_folium(gdf_maec, fillcolor="green", html_output=f"{OUTPUT_DIR}/maec.html")
        visu_folium(gdf_sna, fillcolor="orange", html_output=f"{OUTPUT_DIR}/sna.html")
        visu_folium(gdf_zdh, fillcolor="orange", html_output=f"{OUTPUT_DIR}/zdh.html")

    if EXCEL_FILENAME is not None:
        # Création d'un fichier excel en sortie
        with pd.ExcelWriter(EXCEL_FILENAME) as writer:
            ajouter_onglet(data=df_demandeur, excel_file=writer, onglet="Exploitation")
            ajouter_onglet(data=df_animaux, excel_file=writer, onglet="Animaux")
            ajouter_onglet(data=df_aide_pac, excel_file=writer, onglet="Aides PAC")
            ajouter_onglet(data=gdf_ilots, excel_file=writer, onglet="Ilots")
            ajouter_onglet(data=gdf_parcelles, excel_file=writer, onglet="Parcelles")
            ajouter_onglet(
                data=gdf_bio, excel_file=writer, onglet="Elements Bio par ilot"
            )
            ajouter_onglet(
                data=gdf_maec, excel_file=writer, onglet="Elements MAEC par ilot"
            )
            ajouter_onglet(
                data=gdf_sna, excel_file=writer, onglet="Elements SNA déclarés"
            )
            ajouter_onglet(
                data=gdf_zdh, excel_file=writer, onglet="Elements ZDH déclarés"
            )

    # Améliorations :
    # - pouvoir extraire uniquement les infos relatifs à un champ
    #   (ex: que les zdh, que les zna ...)
    # - nombre stocke sous forme de texte dans excel
    # - on ne récupère pas les coordonnées bancaire (iban/bic/titulaire)
    # - on ne traite pas les données de pièces jointes
