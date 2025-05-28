"""
Module qui contient la fonction extract_ilots.
"""

import xml.etree.ElementTree as ET
import geopandas as gpd
import shapely
from osgeo import ogr


def extract_ilots(xml_root, ns, ns_gml):
    """
    Extrait les informations sur les ilots à partir d'un document XML.
    """
    list_ilots = []

    for ilot in xml_root.findall(f".//{ns}ilot"):
        commune = next((c.text for c in ilot.findall(f".//{ns}commune")), None)
        geom = next((g for g in ilot.findall(f".//{ns_gml}Polygon")), None)

        if geom:
            xmlstr = ET.tostring(geom, encoding="unicode")
            geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
            polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))

            list_ilots.append(
                {
                    "numero-ilot": ilot.attrib.get("numero-ilot"),
                    "numero-ilot-reference": ilot.attrib.get("numero-ilot-reference"),
                    "commune": commune,
                    "geometry": polygon,
                }
            )

    gdf = gpd.GeoDataFrame(list_ilots, crs="EPSG:2154")
    return gdf.to_crs(crs="EPSG:4326")
