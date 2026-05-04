from rdkit import Chem


def _canonical(smiles):
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(mol) if mol else smiles


def predict_products(mol, reagent_text, classification):
    r = reagent_text.lower().replace(" ", "")
    substrate_smiles = Chem.MolToSmiles(mol)
    rxn_type = classification.get("reaction_type", "")
    products = []

    if substrate_smiles == "C=C" and "hbr" in r:
        products.append({"label": "Bromoetano", "smiles": "CCBr", "note": "Adición de HBr al eteno."})
    if substrate_smiles == "C=C" and "br2" in r:
        products.append({"label": "1,2-dibromoetano", "smiles": "BrCCBr", "note": "Adición de Br2 al doble enlace."})
    if substrate_smiles == "c1ccccc1" and "br2" in r and ("febr3" in r or "fe" in r):
        products.append({"label": "Bromobenceno", "smiles": "Brc1ccccc1", "note": "Sustitución electrofílica aromática."})
    if substrate_smiles == "CCO" and "pcc" in r:
        products.append({"label": "Acetaldehído", "smiles": "CC=O", "note": "Oxidación suave de alcohol primario."})
    if substrate_smiles == "CCO" and ("kmno4" in r or "k2cr2o7" in r or "jones" in r):
        products.append({"label": "Ácido acético", "smiles": "CC(=O)O", "note": "Oxidación fuerte de alcohol primario."})
    if substrate_smiles == "CC(C)=O" and ("nabh4" in r or "lialh4" in r):
        products.append({"label": "2-propanol", "smiles": "CC(O)C", "note": "Reducción de cetona a alcohol secundario."})
    if "SN2" in rxn_type and ("oh" in r or "naoh" in r or "koh" in r):
        replaced = substrate_smiles.replace("Br", "O").replace("Cl", "O").replace("I", "O")
        pmol = Chem.MolFromSmiles(replaced)
        if pmol:
            products.append({"label": "Alcohol por sustitución", "smiles": Chem.MolToSmiles(pmol), "note": "Reemplazo simplificado del halógeno por OH."})
    if "E2" in rxn_type and substrate_smiles == "CC(C)(C)Br":
        products.append({"label": "2-metilpropeno", "smiles": "CC(C)=C", "note": "Eliminación beta desde tert-butil bromuro."})

    unique = []
    seen = set()
    for p in products:
        key = _canonical(p["smiles"])
        if key not in seen:
            seen.add(key)
            p["smiles"] = key
            unique.append(p)
    return unique
