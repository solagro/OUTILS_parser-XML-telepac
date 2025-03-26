"""
Module qui contient la fonction extract_zdh.
"""

import xml.etree.ElementTree as ET
import geopandas as gpd
import shapely
from osgeo import ogr


def extract_zdh(xml_root, ns, ns_gml):
    """
    Extrait les informations sur les ZDH déclarées à partir d'un document XML.
    """
    list_zdh = []
    geometries = []

    for zdh in xml_root.findall(f".//{ns}zdh-declaree"):
        # Extraction des informations du ZDH
        numeroZdh = next((num.text for num in zdh.findall(f".//{ns}numeroZdh")), None)
        numeroZdhcreationTas = next(
            (numC.text for numC in zdh.findall(f".//{ns}numeroZdhcreationTas")), None
        )
        densiteVegetation = next(
            (dens.text for dens in zdh.findall(f".//{ns}densiteVegetation")), None
        )

        # Extraction des géométries
        for geom in zdh.findall(f".//{ns_gml}Polygon"):
            xmlstr = ET.tostring(geom, encoding="unicode")
            geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
            polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
            geometries.append(polygon)

        # Ajouter les données du ZDH à la liste
        list_zdh.append(
            {
                "numero-zdh-declaree": numeroZdh,
                "numero-zdh-creationTas": numeroZdhcreationTas,
                "densiteVegetation": densiteVegetation,
            }
        )

    # Créer un GeoDataFrame avec les géométries
    gdf = gpd.GeoDataFrame(list_zdh, geometry=geometries, crs="EPSG:2154")
    return gdf.to_crs(crs="EPSG:4326")
