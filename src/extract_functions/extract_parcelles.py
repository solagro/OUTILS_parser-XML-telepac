"""
Module contenant la fonction extract_parcelles.
"""

import xml.etree.ElementTree as ET
import geopandas as gpd
import shapely
from osgeo import ogr


def extract_parcelles(xml_root, ns, ns_gml):
    """
    Extrait les informations sur les parcelles d'un document XML.
    """
    list_parcelles = []
    geometries = []

    for ilot in xml_root.findall(f".//{ns}ilot"):
        numero_ilot_ref = ilot.attrib.get("numero-ilot-reference")

        for parcelles in ilot.findall(f".//{ns}parcelles"):
            for parcelle in parcelles.findall(f".//{ns}parcelle"):
                dict_parcell = {"numero-ilot-reference": numero_ilot_ref}

                # Récupérer les éléments descriptifs de la parcelle
                for z in parcelle.findall(f".//{ns}descriptif-parcelle"):
                    dict_parcell.update(z.attrib)

                # Ajouter les informations sur la culture principale
                for d in parcelle.findall(f".//{ns}culture-principale"):
                    dict_parcell.update(
                        {f"culture-principale_{k}": v for k, v in d.attrib.items()}
                    )

                # Informations sur l'agriculture biologique
                for d in parcelle.findall(f".//{ns}agri-bio"):
                    dict_parcell.update(
                        {f"agri-bio_{k}": v for k, v in d.attrib.items()}
                    )

                # Informations sur les engagements MAEC
                for d in parcelle.findall(f".//{ns}engagements-maec"):
                    dict_parcell.update(
                        {f"engagements-maec_{k}": v for k, v in d.attrib.items()}
                    )

                # Ajouter d'autres champs spécifiques
                for tag, field in [
                    ("precision", "precision"),
                    ("reconversion-pp", "reconversion-pp"),
                    ("retournement-pp", "retournement-pp"),
                    ("obligation-reimplantation-pp", "obligation-reimplantation-pp"),
                    ("portee", "portee"),
                    ("longueur-bordure", "longueur-bordure"),
                    ("code-culture", "code-culture"),
                    ("surface-admissible", "surface-admissible"),
                ]:
                    value = parcelle.find(f".//{ns}{tag}")
                    if value is not None:
                        dict_parcell[field] = value.text

                # Géométrie de la parcelle
                for geom in parcelle.findall(f".//{ns_gml}Polygon"):
                    xmlstr = ET.tostring(geom, encoding="unicode")
                    geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                    polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                    geometries.append(polygon)

                list_parcelles.append(dict_parcell)

    # Créer un GeoDataFrame
    gdf = gpd.GeoDataFrame(list_parcelles, geometry=geometries, crs="EPSG:2154")
    return gdf.to_crs(crs="EPSG:4326")
