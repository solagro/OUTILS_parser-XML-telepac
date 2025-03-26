"""
Module contenant les fonctions pour extraire les informations sur les SNA déclarées.
"""

import xml.etree.ElementTree as ET
import geopandas as gpd
import shapely
from osgeo import ogr


def extract_sna(xml_root, ns, ns_gml):
    """
    Extrait les informations sur les SNA déclarées à partir d'un document XML.
    """
    list_sna = []
    geometries = []

    for sna in xml_root.findall(f".//{ns}sna-declaree"):
        # Extraire les informations principales du SNA
        numeroSna = next((num.text for num in sna.findall(f".//{ns}numeroSna")), None)
        surfaceGraphique = next(
            (surf.text for surf in sna.findall(f".//{ns}surfaceGraphique")), None
        )
        dateMiseAjour = next(
            (date.text for date in sna.findall(f".//{ns}dateMiseAjour")), None
        )
        datePrivatisation = next(
            (dateP.text for dateP in sna.findall(f".//{ns}datePrivatisation")), None
        )
        categorieSna = next(
            (cat.text for cat in sna.findall(f".//{ns}categorieSna")), None
        )
        typeSna = next((typ.text for typ in sna.findall(f".//{ns}typeSna")), None)
        largeur = next((larg.text for larg in sna.findall(f".//{ns}largeur")), None)
        largeurcalc = next(
            (largcalc.text for largcalc in sna.findall(f".//{ns}largeur-calculee")),
            None,
        )

        # Géométrie du SNA
        for geom in sna.findall(f".//{ns_gml}Point"):
            xmlstr = ET.tostring(geom, encoding="unicode")
            geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
            point = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
            geometries.append(point)

        for geom in sna.findall(f".//{ns_gml}Polygon"):
            xmlstr = ET.tostring(geom, encoding="unicode")
            geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
            polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
            geometries.append(polygon)

        # Intersection avec les ilots
        intersectionSnaIlot = []
        for inters_ilots in sna.findall(f".//{ns}intersectionsSnaIlots"):
            for inter_ilot in inters_ilots.findall(f".//{ns}intersectionSnaIlot"):
                intersectionSnaIlot.append(
                    {
                        "numero-ilot": next(
                            (
                                num.text
                                for num in inter_ilot.findall(f".//{ns}numeroIlot")
                            ),
                            None,
                        ),
                        "largeur": next(
                            (
                                large.text
                                for large in inter_ilot.findall(f".//{ns}largeur")
                            ),
                            None,
                        ),
                    }
                )

        # Intersection avec les parcelles
        intersectionSnaParcelle = []
        for inters_parcelles in sna.findall(f".//{ns}intersectionsSnaParcelles"):
            for inter_parcell in inters_parcelles.findall(
                f".//{ns}intersectionSnaParcelle"
            ):
                intersectionSnaParcelle.append(
                    {
                        "numero-ilot": next(
                            (
                                num_ilot.text
                                for num_ilot in inter_parcell.findall(
                                    f".//{ns}numeroIlot"
                                )
                            ),
                            None,
                        ),
                        "numero-parcelle": next(
                            (
                                num_parcelle.text
                                for num_parcelle in inter_parcell.findall(
                                    f".//{ns}numeroParcelle"
                                )
                            ),
                            None,
                        ),
                        "longueur-sie": next(
                            (
                                longueur.text
                                for longueur in inter_parcell.findall(
                                    f".//{ns}longueur-sie"
                                )
                            ),
                            None,
                        ),
                        "longueur-iae": next(
                            (
                                longueur.text
                                for longueur in inter_parcell.findall(
                                    f".//{ns}longueur-iae"
                                )
                            ),
                            None,
                        ),
                    }
                )

        # Ajouter les données du SNA à la liste
        list_sna.append(
            {
                "numero-sna-declaree": numeroSna,
                "categorieSna": categorieSna,
                "surfaceGraphique": surfaceGraphique,
                "dateMiseAjour": dateMiseAjour,
                "datePrivatisation": datePrivatisation,
                "typeSna": typeSna,
                "largeur": largeur,
                "largeur-calculée": largeurcalc,
                "intersectionsSna_Ilots": intersectionSnaIlot,
                "intersectionSna_Parcelles": intersectionSnaParcelle,
            }
        )

    # Créer un GeoDataFrame avec les géométries
    gdf = gpd.GeoDataFrame(list_sna, geometry=geometries, crs="EPSG:2154")
    return gdf.to_crs(crs="EPSG:4326")
