from rdkit import Chem


def stereochemistry_report(mol):
    Chem.AssignStereochemistry(mol, force=True, cleanIt=True)
    centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True, useLegacyImplementation=False)
    iso = Chem.MolToSmiles(mol, isomericSmiles=True)

    if centers:
        explanation = (
            "Se detectaron centros quirales. R/S indica configuración definida; '?' indica centro potencial sin definir."
        )
    else:
        explanation = "No se detectaron centros quirales tetraédricos con las reglas actuales."

    return {
        "chiral_centers": [{"atom_index": idx, "configuration": config} for idx, config in centers],
        "isomeric_smiles": iso,
        "explanation": explanation,
    }


def compare_molecules(mol1, mol2):
    can1 = Chem.MolToSmiles(mol1, isomericSmiles=False)
    can2 = Chem.MolToSmiles(mol2, isomericSmiles=False)
    iso1 = Chem.MolToSmiles(mol1, isomericSmiles=True)
    iso2 = Chem.MolToSmiles(mol2, isomericSmiles=True)

    centers1 = Chem.FindMolChiralCenters(mol1, includeUnassigned=True, useLegacyImplementation=False)
    centers2 = Chem.FindMolChiralCenters(mol2, includeUnassigned=True, useLegacyImplementation=False)

    if iso1 == iso2:
        relationship = "Idénticos"
        explanation = "Tienen la misma conectividad y la misma estereoquímica."
    elif can1 == can2 and iso1 != iso2:
        if len(centers1) == len(centers2) == 1:
            relationship = "Enantiómeros probables"
            explanation = "Misma conectividad y configuración opuesta en un centro quiral."
        else:
            relationship = "Diastereómeros o estereoisómeros probables"
            explanation = "Misma conectividad, pero diferente información estereoquímica."
    else:
        relationship = "Compuestos constitucionales diferentes"
        explanation = "La conectividad molecular no coincide."

    return {
        "canonical_A_no_stereo": can1,
        "canonical_B_no_stereo": can2,
        "isomeric_A": iso1,
        "isomeric_B": iso2,
        "chiral_centers_A": centers1,
        "chiral_centers_B": centers2,
        "relationship": relationship,
        "explanation": explanation,
    }
