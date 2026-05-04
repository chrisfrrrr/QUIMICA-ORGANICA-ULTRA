from rdkit.Chem import Descriptors, rdMolDescriptors, Crippen, Lipinski


def molecular_report(mol):
    return {
        "Fórmula molecular": rdMolDescriptors.CalcMolFormula(mol),
        "Masa molecular promedio": round(Descriptors.MolWt(mol), 4),
        "Masa exacta": round(Descriptors.ExactMolWt(mol), 4),
        "LogP estimado": round(Crippen.MolLogP(mol), 4),
        "TPSA": round(rdMolDescriptors.CalcTPSA(mol), 4),
        "Donadores de H": Lipinski.NumHDonors(mol),
        "Aceptores de H": Lipinski.NumHAcceptors(mol),
        "Anillos totales": rdMolDescriptors.CalcNumRings(mol),
        "Anillos aromáticos": rdMolDescriptors.CalcNumAromaticRings(mol),
        "Enlaces rotables": Lipinski.NumRotatableBonds(mol),
        "Fracción Csp3": round(rdMolDescriptors.CalcFractionCSP3(mol), 4),
        "Átomos pesados": mol.GetNumHeavyAtoms(),
    }
