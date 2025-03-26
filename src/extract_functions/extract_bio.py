"""
Module contenant les fonctions d'extraction des éléments bio d'un fichier XML.
"""

import xml.etree.ElementTree as ET
import geopandas as gpd
import shapely
from osgeo import ogr


def extract_bio(xml_root, ns, ns_gml):
    """
    Extrait les informations sur les éléments bio d'un document XML.
    """
    list_bio = []
    geometries = []

    for ilot in xml_root.findall(f".//{ns}ilot"):
        # Vérifie la présence d'éléments bio dans le fichier XML
        for d in ilot.findall(f".//{ns}elements-bio"):
            for e in d.findall(f".//{ns}element-bio"):
                # Extraire les données des éléments bio
                numeroelement = next(
                    (num.text for num in e.findall(f".//{ns}numero-element")), None
                )
                codemesure = next(
                    (code.text for code in e.findall(f".//{ns}code-mesure")), None
                )

                # Géométrie de l'élément bio
                for geom in e.findall(f".//{ns_gml}Polygon"):
                    xmlstr = ET.tostring(geom, encoding="unicode")
                    geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                    polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                    geometries.append(polygon)

                # Extraire les informations sur les campagnes
                premcampagne = next(
                    (prem.text for prem in e.findall(f".//{ns}premiere-campagne")), None
                )
                dercampagne = next(
                    (der.text for der in e.findall(f".//{ns}derniere-campagne")), None
                )

                # Ajouter les données à la liste
                list_bio.append(
                    {
                        "numero-ilot-reference": ilot.attrib.get(
                            "numero-ilot-reference"
                        ),
                        "numero-element-bio": numeroelement,
                        "code-mesure": codemesure,
                        "premiere-campagne": premcampagne,
                        "derniere-campagne": dercampagne,
                    }
                )

    # Créer un GeoDataFrame
    gdf = gpd.GeoDataFrame(list_bio, geometry=geometries, crs="EPSG:2154")
    return gdf.to_crs(crs="EPSG:4326")
