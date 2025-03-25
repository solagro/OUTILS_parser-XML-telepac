"""
Tentative de lecture d'un fichier xml
"""

import argparse
import xml.etree.ElementTree as ET
import os
import pandas as pd
import geopandas as gpd
import shapely
import folium
from osgeo import ogr


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
    """Vérifier le type d'extension parmi une liste définie lors du parsage des arguments"""

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
    """Visualisation dynamique avec Folium"""
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


def extract_ilots(xml_root, ns, ns_gml):
    """
    TBD
    """
    list_ilots = list()

    for ilot in xml_root.findall(f".//{ns}ilot"):
        for c in ilot.findall(f".//{ns}commune"):
            commune = c.text
        for geom in ilot.findall(f".//{ns_gml}Polygon"):
            xmlstr = ET.tostring(geom, encoding="unicode")
            geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
            polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
            break

        list_ilots.append(
            {
                "numero-ilot": ilot.attrib["numero-ilot"],
                "numero-ilot-reference": ilot.attrib["numero-ilot-reference"],
                "commune": commune,
                "geometry": polygon,
            }
        )

    gdf = gpd.GeoDataFrame(list_ilots, crs="EPSG:2154")
    gdf = gdf.to_crs(crs="EPSG:4326")
    return gdf


def extract_parcelles(xml_root, ns, ns_gml):
    """
    TBD
    """
    list_parcelles = list()
    geometries = list()
    for ilot in xml_root.findall(f".//{ns}ilot"):
        for parcelles in ilot.findall(f".//{ns}parcelles"):
            dict_parcell = dict()
            for parcelle in parcelles.findall(f".//{ns}parcelle"):
                dict_parcell = dict()
                dict_parcell["numero-ilot-reference"] = ilot.attrib[
                    "numero-ilot-reference"
                ]
                for z in parcelle.findall(f".//{ns}descriptif-parcelle"):
                    # num_parcelle = z.attrib["numero-parcelle"]
                    for k, v in z.attrib.items():
                        dict_parcell[k] = v
                for d in parcelle.findall(f".//{ns}culture-principale"):
                    # prod = d.attrib["production-semences"]
                    for k, v in d.attrib.items():
                        dict_parcell[f"culture-principale_{k}"] = v

                    # if "production-fermiers" in d.attrib.keys():
                    #     prod = d.attrib["production-fermiers"]
                    # prod = d.attrib["deshydratation"]
                    # prod = d.attrib["date-plantation"]
                    # prod = d.attrib["derogation-ukraine"]
                    # prod = d.attrib["inter-rang"]
                    # prod = d.attrib["couvert-forestier"]
                    # prod = d.attrib["accident-culture"]
                    # prod = d.attrib["culture-secondaire"]
                    # prod = d.attrib["date-labour"]
                # cond_bio = None
                # cond_maraichage = None
                if parcelle.findall(f".//{ns}agri-bio"):
                    for d in parcelle.findall(f".//{ns}agri-bio"):
                        # cond_bio = d.attrib["conduite-bio"]
                        # cond_maraichage = d.attrib["conduite-maraichage"]
                        for k, v in d.attrib.items():
                            dict_parcell[f"agri-bio_{k}"] = v
                for d in parcelle.findall(f".//{ns}engagements-maec"):
                    # surface_cible = d.attrib["surface-cible"]
                    for k, v in d.attrib.items():
                        dict_parcell[f"engagements-maec_{k}"] = v
                    # elevage = d.attrib["elevage-monogastrique"]
                #  print(parcelle.attrib["culture-principale"])
                #  print(parcelle.attrib["agri-bio"])
                #  print(parcelle.attrib["engagements-maec"])
                if parcelle.findall(f".//{ns}precision"):
                    for d in parcelle.findall(f".//{ns}precision"):
                        dict_parcell["precision"] = d.text

                if parcelle.findall(f".//{ns}reconversion-pp"):
                    for d in parcelle.findall(f".//{ns}reconversion-pp"):
                        dict_parcell["reconversion-pp"] = d.text

                if parcelle.findall(f".//{ns}retournement-pp"):
                    for d in parcelle.findall(f".//{ns}retournement-pp"):
                        dict_parcell["retournement-pp"] = d.text

                if parcelle.findall(f".//{ns}obligation-reimplantation-pp"):
                    for d in parcelle.findall(f".//{ns}obligation-reimplantation-pp"):
                        dict_parcell["obligation-reimplantation-pp"] = d.text

                if parcelle.findall(f".//{ns}portee"):
                    for portee in parcelle.findall(f".//{ns}portee"):
                        dict_parcell["portee"] = portee.text

                if parcelle.findall(f".//{ns}longueur-bordure"):
                    for long in parcelle.findall(f".//{ns}longueur-bordure"):
                        dict_parcell["longueur-bordure"] = long.text

                for d in parcelle.findall(f".//{ns}code-culture"):
                    dict_parcell["code-culture"] = d.text

                for surfad in parcelle.findall(f".//{ns}surface-admissible"):
                    dict_parcell["surface-admissible"] = surfad.text

                for geom in parcelle.findall(f".//{ns_gml}Polygon"):
                    xmlstr = ET.tostring(geom, encoding="unicode")
                    geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                    polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                    geometries.append(polygon)

                list_parcelles.append(
                    dict_parcell
                    # list_parcelles.append(
                    #     {
                    #         "numero-ilot-reference": ilot.attrib["numero-ilot-reference"],
                    #         "numero-parcelle": num_parcelle,
                    #         "culture-principale_production-semences": prod,
                    #         "agri-bio_conduite-bio": cond_bio,
                    #         "agri-bio_conduite-maraichage": cond_maraichage,
                    #         "engagements-maec_surface_cible": surface_cible,
                    #         "precision": precision,
                    #         "code-culture": culture,
                    #     }
                )

    gdf = gpd.GeoDataFrame(list_parcelles, geometry=geometries, crs="EPSG:2154")
    gdf = gdf.to_crs(crs="EPSG:4326")
    return gdf


def extract_bio(xml_root, ns, ns_gml):
    """
    TBD
    """
    # boucle sur éléments-bio
    # boucle sur élément-bio
    # numero-element
    # code-mesure
    # geometrie
    # premiere-campagne
    # derniere-campagne
    list_bio = list()
    geometries = list()
    for ilot in xml_root.findall(f".//{ns}ilot"):
        # vérifie la présence d'éléments bio dans le fichier xml
        if ilot.findall(f".//{ns}elements-bio"):
            for d in ilot.findall(f".//{ns}elements-bio"):
                for e in d.findall(f".//{ns}element-bio"):
                    for num in e.findall(f".//{ns}numero-element"):
                        numeroelement = num.text
                    for code in e.findall(f".//{ns}code-mesure"):
                        codemesure = code.text
                    for geom in e.findall(f".//{ns_gml}Polygon"):
                        xmlstr = ET.tostring(geom, encoding="unicode")
                        geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                        polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                        geometries.append(polygon)
                    premcampagne = None
                    if e.findall(f".//{ns}premiere-campagne"):
                        for prem in e.findall(f".//{ns}premiere-campagne"):
                            premcampagne = prem.text
                    dercampagne = None
                    if e.findall(f".//{ns}derniere-campagne"):
                        for der in e.findall(f".//{ns}derniere-campagne"):
                            dercampagne = der.text

                    list_bio.append(
                        {
                            "numero-ilot-reference": ilot.attrib[
                                "numero-ilot-reference"
                            ],
                            "numero-element-bio": numeroelement,
                            "code-mesure": codemesure,
                            "premiere-campagne": premcampagne,
                            "derniere-campagne": dercampagne,
                        }
                    )

    gdf = gpd.GeoDataFrame(list_bio, geometry=geometries, crs="EPSG:2154")
    gdf = gdf.to_crs(crs="EPSG:4326")
    return gdf


def extract_maec(xml_root, ns, ns_gml):
    """
    TBD
    """
    list_maec = list()
    geometries = list()
    for ilot in xml_root.findall(f".//{ns}ilot"):
        # vérifie la présence d'éléments bio dans le fichier xml
        if ilot.findall(f".//{ns}elements-maec-S"):
            for d in ilot.findall(f".//{ns}element-surfacique"):
                for num in d.findall(f".//{ns}numero-element"):
                    numeroelement = num.text
                for code in d.findall(f".//{ns}code-mesure"):
                    codemesure = code.text
                ssgeom = None
                if d.findall(f".//{ns}sous-type-geometrie"):
                    for ss in d.findall(f".//{ns}sous-type-geometrie"):
                        ssgeom = ss.text
                for geom in d.findall(f".//{ns_gml}Polygon"):
                    xmlstr = ET.tostring(geom, encoding="unicode")
                    geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                    polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                    geometries.append(polygon)
                premcampagne = None
                if d.findall(f".//{ns}premiere-campagne"):
                    for prem in d.findall(f".//{ns}premiere-campagne"):
                        premcampagne = prem.text
                dercampagne = None
                if d.findall(f".//{ns}derniere-campagne"):
                    for der in d.findall(f".//{ns}derniere-campagne"):
                        dercampagne = der.text

                list_maec.append(
                    {
                        "numero-ilot-reference": ilot.attrib["numero-ilot-reference"],
                        "numero-element-maec": numeroelement,
                        "code-mesure": codemesure,
                        "premiere-campagne": premcampagne,
                        "derniere-campagne": dercampagne,
                        "sous-type-geometrie": ssgeom,
                    }
                )

    gdf = gpd.GeoDataFrame(list_maec, geometry=geometries, crs="EPSG:2154")
    gdf = gdf.to_crs(crs="EPSG:4326")
    return gdf


def extract_sna(xml_root, ns, ns_gml):
    """
    TBD
    """
    #     numeroSna
    #     categorieSna
    #     typeSna
    #     geometrie
    #     optionnel :
    #   intersectionsSnaIlots
    # intersectionSnaIlot
    # numeroIlot
    # largeur
    #   intersectionsSnaParcelles
    # intersectionSnaParcelle
    # numeroIlot
    # numeroParcelle
    # longueur-sie
    list_sna = list()
    geometries = list()
    for sna in xml_root.findall(f".//{ns}sna-declaree"):
        for num in sna.findall(f".//{ns}numeroSna"):
            numeroSna = num.text
        surfaceGraphique = None
        if sna.findall(f".//{ns}surfaceGraphique"):
            for surf in sna.findall(f".//{ns}surfaceGraphique"):
                surfaceGraphique = surf.text
        dateMiseAjour = None
        if sna.findall(f".//{ns}dateMiseAjour"):
            for date in sna.findall(f".//{ns}dateMiseAjour"):
                dateMiseAjour = date.text
        datePrivatisation = None
        if sna.findall(f".//{ns}datePrivatisation"):
            for dateP in sna.findall(f".//{ns}datePrivatisation"):
                datePrivatisation = dateP.text
        for cat in sna.findall(f".//{ns}categorieSna"):
            categorieSna = cat.text
        for typ in sna.findall(f".//{ns}typeSna"):
            typeSna = typ.text
        largeur = None
        if sna.findall(f".//{ns}largeur"):
            for larg in sna.findall(f".//{ns}largeur"):
                largeur = larg.text
        largeurcalc = None
        if sna.findall(f".//{ns}largeur-calculee"):
            for largcalc in sna.findall(f".//{ns}largeur-calculee"):
                largeurcalc = largcalc.text

        if sna.findall(f".//{ns_gml}Point"):
            for geom in sna.findall(f".//{ns_gml}Point"):
                xmlstr = ET.tostring(geom, encoding="unicode")
                geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                point = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                geometries.append(point)
        if sna.findall(f".//{ns_gml}Polygon"):
            for geom in sna.findall(f".//{ns_gml}Polygon"):
                xmlstr = ET.tostring(geom, encoding="unicode")
                geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
                polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
                geometries.append(polygon)

        # Partie optionnelle
        intersectionSnaIlot_numeroIlot = None
        intersectionSnaIlot_largeur = None
        intersectionSnaIlot = None
        if sna.findall(f".//{ns}intersectionsSnaIlots"):
            intersectionSnaIlot = list()
            for inters_ilots in sna.findall(f".//{ns}intersectionsSnaIlots"):
                for inter_ilot in inters_ilots.findall(f".//{ns}intersectionSnaIlot"):
                    for num in inter_ilot.findall(f".//{ns}numeroIlot"):
                        intersectionSnaIlot_numeroIlot = num.text
                    for large in inter_ilot.findall(f".//{ns}largeur"):
                        intersectionSnaIlot_largeur = large.text
                    intersectionSnaIlot.append(
                        {
                            "numero-ilot": intersectionSnaIlot_numeroIlot,
                            "largeur": intersectionSnaIlot_largeur,
                        }
                    )

        intersectionSnaParcelle_ilot = None
        intersectionSnaParcelle_parcelle = None
        longueur_sie = None
        longueur_iae = None
        intersectionSnaParcelle = None
        if sna.findall(f".//{ns}intersectionsSnaParcelles"):
            intersectionSnaParcelle = list()
            for inters_parcelles in sna.findall(f".//{ns}intersectionsSnaParcelles"):
                for inter_parcell in inters_parcelles.findall(
                    f".//{ns}intersectionSnaParcelle"
                ):
                    for num_ilot in inter_parcell.findall(f".//{ns}numeroIlot"):
                        intersectionSnaParcelle_ilot = num_ilot.text
                    for num_parcelle in inter_parcell.findall(f".//{ns}numeroParcelle"):
                        intersectionSnaParcelle_parcelle = num_parcelle.text
                    if sna.findall(f".//{ns}longueur-sie"):
                        for longueur in inter_parcell.findall(f".//{ns}longueur-sie"):
                            longueur_sie = longueur.text

                    if sna.findall(f".//{ns}longueur-iae"):
                        for longueur in inter_parcell.findall(f".//{ns}longueur-iae"):
                            longueur_iae = longueur.text

                    intersectionSnaParcelle.append(
                        {
                            "numero-ilot": intersectionSnaParcelle_ilot,
                            "numero-parcelle": intersectionSnaParcelle_parcelle,
                            "longueur-sie": longueur_sie,
                            "longueur-iae": longueur_iae,
                        }
                    )
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
    # print(list_sna)
    # print(len(list_sna))
    # print(len(geometries))
    # on peut avoir le cas d'une sna avec plusieurs géométries (mais le meme gml)
    # qui définissent les contour intérieur/extérieur d'un polygone par exemple.
    gdf = gpd.GeoDataFrame(list_sna, geometry=geometries, crs="EPSG:2154")
    gdf = gdf.to_crs(crs="EPSG:4326")
    return gdf


def extract_zdh(xml_root, ns, ns_gml):
    """
    TBD
    """
    # numeroZdh
    # densiteVegetation
    # geometrie
    list_zdh = list()
    geometries = list()
    for zdh in xml_root.findall(f".//{ns}zdh-declaree"):
        numeroZdh = None
        if zdh.findall(f".//{ns}numeroZdh"):
            for num in zdh.findall(f".//{ns}numeroZdh"):
                numeroZdh = num.text
        numeroZdhcreationTas = None
        if zdh.findall(f".//{ns}numeroZdhcreationTas"):
            for numC in zdh.findall(f".//{ns}numeroZdhcreationTas"):
                numeroZdhcreationTas = numC.text
        for dens in zdh.findall(f".//{ns}densiteVegetation"):
            densiteVegetation = dens.text
        for geom in zdh.findall(f".//{ns_gml}Polygon"):
            xmlstr = ET.tostring(geom, encoding="unicode")
            geom_gdal = ogr.CreateGeometryFromGML(xmlstr)
            polygon = shapely.wkb.loads(bytes(geom_gdal.ExportToIsoWkb()))
            geometries.append(polygon)

            list_zdh.append(
                {
                    "numero-zdh-declaree": numeroZdh,
                    "numero-zdh-creationTas": numeroZdhcreationTas,
                    "densiteVegetation": densiteVegetation,
                }
            )
    gdf = gpd.GeoDataFrame(list_zdh, geometry=geometries, crs="EPSG:2154")
    gdf = gdf.to_crs(crs="EPSG:4326")
    return gdf


def extract_demandeur(xml_root, ns, ns_gml):
    """
    TBD
    """
    list_demandeur = list()
    dict_demandeur = dict()
    for prod in xml_root.findall(f".//{ns}producteur"):
        dict_demandeur["numero-pacage"] = prod.attrib["numero-pacage"]
    for d in xml_root.findall(f".//{ns}demandeur"):
        for k, v in d.attrib.items():
            dict_demandeur[k] = v
            # A FINIR !!!!
        for s in d.findall(f".//{ns}siret"):
            dict_demandeur["siret"] = s.text
        for c in d.findall(f".//{ns}courriel"):
            dict_demandeur["courriel"] = c.text
        for k in d.findall(f".//{ns}identification-societe"):
            for l in k.findall(f".//{ns}exploitation"):
                dict_demandeur["exploitation"] = l.text

            list_demandeur.append(dict_demandeur)

            list_associe = None
            if k.findall(f".//{ns}associes"):
                list_associe = list()
                for m in k.findall(f".//{ns}associes"):
                    for n in m.findall(f".//{ns}associe"):
                        dict_associe = dict()
                        dict_associe.update(dict_demandeur)
                        dict_associe["numero-pacage-associe"] = n.attrib[
                            "numero-pacage"
                        ]
                        for o in n.findall(f".//{ns}civilite"):
                            dict_associe["civilité"] = o.text
                        for p in n.findall(f".//{ns}nom"):
                            dict_associe["nom"] = p.text
                        for q in n.findall(f".//{ns}prenoms"):
                            dict_associe["prenom"] = q.text
                        list_associe.append(dict_associe)

    if list_associe:
        df = pd.DataFrame(data=list_associe)
    else:
        df = pd.DataFrame(data=list_demandeur)
    return df


def extract_animaux(xml_root, ns, ns_gml):
    """
    TBD
    """
    list_animaux = list()
    if xml_root.findall(f".//{ns}effectifs-animaux"):
        for animo in xml.findall(f".//{ns}effectifs-animaux"):
            for animal in animo.findall(f".//{ns}effectif-animal"):
                for typ in animal.findall(f".//{ns}type-animal-1"):
                    typeanimal = typ.text
                for nb in animal.findall(f".//{ns}nb-animaux-1"):
                    nbanimaux = nb.text
                list_animaux.append(
                    {
                        "type-animal": typeanimal,
                        "nb-animaux-1": nbanimaux,
                    }
                )
    df = pd.DataFrame(data=list_animaux)
    return df


def extract_aides_pac(xml_root, ns, ns_gml):
    """
    TBD
    """
    list_aides = list()
    dict_aides = dict()
    if xml_root.findall(f".//{ns}demandes-aides-pilier1-et-AR"):
        for aides1 in xml_root.findall(f".//{ns}demandes-aides-pilier1-et-AR"):
            for k, v in aides1.attrib.items():
                dict_aides[k] = v
            for bcae8 in aides1.findall(f".//{ns}bcae8"):
                for opt in bcae8.findall(f".//{ns}option-BCAE8"):
                    dict_aides["option_bcae8"] = opt.text
            for dem1 in aides1.findall(f".//{ns}demande-aides-decouplees"):
                for k, v in dem1.attrib.items():
                    dict_aides[k] = v
            for dem2 in aides1.findall(f".//{ns}demande-aide-ecoregime"):
                for k, v in dem2.attrib.items():
                    dict_aides[k] = v
            for dem3 in aides1.findall(f".//{ns}demande-legumineuses-fourrageres"):
                for k, v in dem3.attrib.items():
                    dict_aides[k] = v
            for dem4 in aides1.findall(f".//{ns}demande-legumineuses-graines"):
                for k, v in dem4.attrib.items():
                    dict_aides[k] = v
            for dem5 in aides1.findall(f".//{ns}demande-assurance-recolte"):
                for k, v in dem5.attrib.items():
                    dict_aides[k] = v

    if xml_root.findall(f".//{ns}demandes-aides-pilier2"):
        for aides2 in xml_root.findall(f".//{ns}demandes-aides-pilier2"):
            for k, v in aides2.attrib.items():
                dict_aides[k] = v
                for dem1 in aides2.findall(f".//{ns}ichn"):
                    for k, v in dem1.attrib.items():
                        dict_aides[k] = v

    if xml_root.findall(f".//{ns}autres-obligations"):
        for oblig in xml_root.findall(f".//{ns}autres-obligations"):
            for k, v in oblig.attrib.items():
                dict_aides[k] = v

    list_aides.append(dict_aides)
    df = pd.DataFrame(data=list_aides)
    return df


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
