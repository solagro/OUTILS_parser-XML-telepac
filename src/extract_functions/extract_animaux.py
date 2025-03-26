"""
Module qui contient la fonction extract_animaux.
"""

import pandas as pd


def extract_animaux(xml_root, ns, ns_gml):
    """
    Extrait les informations sur les effectifs d'animaux à partir d'un document XML.
    """
    list_animaux = []

    # Recherche des effectifs d'animaux dans le XML
    for animo in xml_root.findall(f".//{ns}effectifs-animaux"):
        for animal in animo.findall(f".//{ns}effectif-animal"):
            # Extraction des informations sur chaque type d'animal
            typeanimal = next(
                (typ.text for typ in animal.findall(f".//{ns}type-animal-1")), None
            )
            nbanimaux = next(
                (nb.text for nb in animal.findall(f".//{ns}nb-animaux-1")), None
            )

            list_animaux.append(
                {
                    "type-animal": typeanimal,
                    "nb-animaux-1": nbanimaux,
                }
            )

    # Retourner les résultats sous forme de DataFrame
    return pd.DataFrame(data=list_animaux)
