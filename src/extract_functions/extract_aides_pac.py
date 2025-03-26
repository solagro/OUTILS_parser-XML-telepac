"""
Module contenant la fonction extract_aides_pac.
"""

import pandas as pd


def extract_aides_pac(xml_root, ns, ns_gml):
    """
    Extrait les informations relatives aux aides PAC à partir d'un document XML.
    """
    list_aides = []

    # Dictionnaire pour stocker les informations extraites
    dict_aides = {}

    # Extrait les informations des demandes d'aides Pilier 1 et AR
    for aides1 in xml_root.findall(f".//{ns}demandes-aides-pilier1-et-AR"):
        dict_aides.update(aides1.attrib)

        # Option BCAE8
        for opt in aides1.findall(f".//{ns}bcae8//{ns}option-BCAE8"):
            dict_aides["option_bcae8"] = opt.text

        # Demandes d'aides découpées
        for dem1 in aides1.findall(f".//{ns}demande-aides-decouplees"):
            dict_aides.update(dem1.attrib)

        # Autres demandes d'aides
        for dem2 in aides1.findall(f".//{ns}demande-aide-ecoregime"):
            dict_aides.update(dem2.attrib)
        for dem3 in aides1.findall(f".//{ns}demande-legumineuses-fourrageres"):
            dict_aides.update(dem3.attrib)
        for dem4 in aides1.findall(f".//{ns}demande-legumineuses-graines"):
            dict_aides.update(dem4.attrib)
        for dem5 in aides1.findall(f".//{ns}demande-assurance-recolte"):
            dict_aides.update(dem5.attrib)

    # Extrait les informations des demandes d'aides Pilier 2
    for aides2 in xml_root.findall(f".//{ns}demandes-aides-pilier2"):
        dict_aides.update(aides2.attrib)

        # Demandes d'ichn (Indemnités compensatoires)
        for dem1 in aides2.findall(f".//{ns}ichn"):
            dict_aides.update(dem1.attrib)

    # Extrait les informations des autres obligations
    for oblig in xml_root.findall(f".//{ns}autres-obligations"):
        dict_aides.update(oblig.attrib)

    # Ajout des informations dans la liste
    list_aides.append(dict_aides)

    # Retourner les données sous forme de DataFrame
    return pd.DataFrame(data=list_aides)
