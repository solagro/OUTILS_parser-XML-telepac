"""
Extrait les informations du demandeur et de ses associés à partir d'un fichier XML.
"""

import pandas as pd


def extract_demandeur(xml_root, ns, ns_gml):
    """
    Extrait les informations du demandeur et de ses associés à partir d'un fichier XML.
    """
    list_demandeur = []
    list_associe = []

    # Récupérer le numéro de pacage du producteur
    numero_pacage = None
    for prod in xml_root.findall(f".//{ns}producteur"):
        numero_pacage = prod.attrib.get("numero-pacage")
        if numero_pacage:  # On quitte dès qu'on trouve le numéro de pacage
            break

    if not numero_pacage:
        print("Aucun numéro de pacage trouvé.")

    # Extraction des informations du demandeur
    for d in xml_root.findall(f".//{ns}demandeur"):
        dict_demandeur = d.attrib.copy()

        # Ajout du numéro de pacage dans dict_demandeur
        dict_demandeur["numero-pacage"] = numero_pacage

        # Ajout des informations supplémentaires
        dict_demandeur["siret"] = d.findtext(f".//{ns}siret")
        dict_demandeur["courriel"] = d.findtext(f".//{ns}courriel")
        dict_demandeur["exploitation"] = d.findtext(
            f".//{ns}identification-societe//{ns}exploitation"
        )

        # Ajouter le dict_demandeur à la liste des demandeurs
        list_demandeur.append(dict_demandeur)

        # Extraction des informations des associés
        for associe in d.findall(
            f".//{ns}identification-societe//{ns}associes//{ns}associe"
        ):
            dict_associe = dict_demandeur.copy()
            dict_associe["numero-pacage-associe"] = associe.attrib.get("numero-pacage")
            dict_associe["civilite"] = associe.findtext(f".//{ns}civilite")
            dict_associe["nom"] = associe.findtext(f".//{ns}nom")
            dict_associe["prenom"] = associe.findtext(f".//{ns}prenoms")

            # Ajouter l'associé à la liste des associés
            list_associe.append(dict_associe)

    # Si des associés ont été trouvés, retourner la liste des associés sous forme de DataFrame
    if list_associe:
        df = pd.DataFrame(data=list_associe)
    else:
        # Si aucun associé, retourner la liste des demandeurs
        df = pd.DataFrame(data=list_demandeur)

    return df
