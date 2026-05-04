from rdkit.Chem import rdMolDescriptors


def aromaticity_report(mol):
    aromatic_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
    aromatic_rings = rdMolDescriptors.CalcNumAromaticRings(mol)
    total_rings = rdMolDescriptors.CalcNumRings(mol)

    if aromatic_rings > 0:
        classification = "Aromático"
        explanation = (
            "Se detecta al menos un anillo aromático. En química orgánica esto se asocia "
            "con sistemas cíclicos conjugados que cumplen una distribución tipo 4n+2 electrones pi."
        )
    elif total_rings > 0:
        classification = "No aromático o antiaromático probable"
        explanation = (
            "Hay anillos, pero RDKit no detecta aromaticidad. Para antiaromaticidad debe revisarse "
            "si el sistema es cíclico, plano, completamente conjugado y con 4n electrones pi."
        )
    else:
        classification = "No aromático"
        explanation = "No se detecta un sistema cíclico aromático."

    return {
        "classification": classification,
        "aromatic_atoms": aromatic_atoms,
        "aromatic_rings": aromatic_rings,
        "total_rings": total_rings,
        "explanation": explanation,
    }
