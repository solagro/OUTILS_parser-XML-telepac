"""
Scan d'un fichier xml : affiche la liste des élements
"""

import argparse
import xml.etree.ElementTree as ET
import pickle
from pathlib import Path


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
        "--pickle_diff",
        action="store_true",
        default=False,
        help="Affiche les éléments différents de ceux déjà connus et listés dans un pickle. "
        "Si un élément est nouveau, il n'est sans doute pas pris en charge dans read_xml !",
    )
    required_args.add_argument(
        "--pickle_create",
        action="store_true",
        default=False,
        help="Permet la création ou l'ajout d'information au fichier pickle "
        "stockant les éléments connus des données Telepac de xml.",
    )
    return parser.parse_args()


def create_liste_elements(xml_filename):
    """
    Création d'une liste d'éléments de l'arbre du fichier xml
    """
    NAMESPACE = "{urn:x-telepac:fr.gouv.agriculture.telepac:echange-producteur}"
    xml = ET.parse(xml_filename)
    root = xml.getroot()
    list_elem = list()
    list_attrib = list()
    for elem in root.iter():
        i = elem.tag.find("}")
        if i >= 0:
            list_elem.append(elem.tag[i + 1 :])
            # print(elem.tag[i + 1 :])
            # print(elem.text)

        # On ajoute également les attributs (éventuels) de chaque élément
        for j in xml.findall(f".//{NAMESPACE}{elem.tag[i + 1 :]}"):
            if j.attrib.keys():
                for at, at_val in j.attrib.items():
                    if at not in list_attrib:
                        list_attrib.append(at)

    list_elem = list_elem + list_attrib
    return list_elem


def create_pickle(pkl_filename, list_elem_uniq):
    """
    Création d'un fichier pickle contenant les éléments uniques du fichier xml
    """
    # si le fichier existe on le complete avec les nouveaux éléments
    fileObj = Path(pkl_filename)
    if fileObj.is_file():
        with open(pkl_filename, "rb") as f:
            data_loaded = pickle.load(f)
        set_difference = set(list_elem_uniq).symmetric_difference(
            set(data_loaded["list_elements_connus"])
        )
        data = {
            "list_elements_connus": data_loaded["list_elements_connus"]
            + list(set_difference)
        }
    # sinon on ajoute les éléments unique
    else:
        data = {"list_elements_connus": list_elem_uniq}
    with open(pkl_filename, "wb") as f:
        pickle.dump(data, f)


def show_pickle_diff(pkl_filename, list_elem_uniq):
    """
    Affiche la différence entre les éléments du fichier xml et ceux du pickle
    """
    with open(pkl_filename, "rb") as f:
        data_loaded = pickle.load(f)
    set_difference = set(list_elem_uniq).difference(
        set(data_loaded["list_elements_connus"])
    )
    if not list(set_difference):
        print("PICKLE_DIFF : Pas de nouveaux éléments")
    else:
        print("PICKLE_DIFF :")
        print(list(set_difference))


if __name__ == "__main__":
    # Import des paramètres
    args = usage()
    XML_FILE = args.input_xml
    PICKLE_DIFF = args.pickle_diff
    PICKLE_CREATE = args.pickle_create

    # Création d'une liste d'éléments du tree xml
    list_elements = create_liste_elements(XML_FILE)
    list_unique_elements = sorted(list(set(list_elements)))

    # Affichage des éléments uniques du tree xml
    if not PICKLE_DIFF:
        for element in list_unique_elements:
            nb = list_elements.count(element)
            print(f"{element} - #{nb}")

    # Gestion du pickle
    PICKLE_FILENAME = "elements_connus.pkl"

    # Création/ajout de données dans le pickle
    if PICKLE_CREATE:
        create_pickle(PICKLE_FILENAME, list_unique_elements)

    # Affiche la différence entre xml et liste connu (pickle)
    if PICKLE_DIFF:
        show_pickle_diff(PICKLE_FILENAME, list_unique_elements)
