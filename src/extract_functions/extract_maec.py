"""
Module pour extraire les informations sur les éléments MAEC d'un document XML.
"""

import xml.etree.ElementTree as ET
import geopandas as gpd
import shapely
from osgeo import ogr


def extract_maec(xml_root, ns, ns_gml):
    """
    Extrait les informations sur les éléments MAEC d'un document XML.
    """
    list_maec = []
    geometries = []

    for ilot in xml_root.findall(f".//{ns}ilot"):
        # Vérifie la présence d'éléments MAEC dans le fichier XML
        for d in ilot.findall(f".//{ns}element-surfacique"):
            # Extraire les données des éléments MAEC
            numeroelement = next(
                (num.text for num in d.findall(f".//{ns}numero-element")), None
            )
            codemesure = next(
                (code.text for code in d.findall(f".//{ns}code-mesure")), None
            )

            # Sous-type de géométrie
            ssgeom = next(
                (ss.text for ss in d.findall(f".//{ns}sous-type-geometrie")), None
            )

            # Géométrie de l'élément MAEC
            for geom in d.findall(f".//{ns_gml}Polygon"):
                xmlstr = ET.tostring(geom, encoding="unicode")
                geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                geometries.append(polygon)

            # Informations sur les campagnes
            premcampagne = next(
                (prem.text for prem in d.findall(f".//{ns}premiere-campagne")), None
            )
            dercampagne = next(
                (der.text for der in d.findall(f".//{ns}derniere-campagne")), None
            )

            # Ajouter les données à la liste
            list_maec.append(
                {
                    "numero-ilot-reference": ilot.attrib.get("numero-ilot-reference"),
                    "numero-element-maec": numeroelement,
                    "code-mesure": codemesure,
                    "premiere-campagne": premcampagne,
                    "derniere-campagne": dercampagne,
                    "sous-type-geometrie": ssgeom,
                }
            )

    # Créer un GeoDataFrame
    gdf = gpd.GeoDataFrame(list_maec, geometry=geometries, crs="EPSG:2154")
    return gdf.to_crs(crs="EPSG:4326")
