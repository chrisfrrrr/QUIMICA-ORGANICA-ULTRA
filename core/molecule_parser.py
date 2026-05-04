from rdkit import Chem
from core.name_resolver import resolve_name_to_smiles


def parse_molecule(user_input: str, input_mode: str, use_pubchem: bool = True):
    if not user_input or not user_input.strip():
        return None, "No se ingresó ningún compuesto.", None

    clean_input = user_input.strip()
    source = "SMILES directo"

    if input_mode in ["Nombre / IUPAC", "Nombre común limitado"]:
        smiles, source = resolve_name_to_smiles(clean_input, use_pubchem=use_pubchem)
        if not smiles:
            return None, source, None
        mol = Chem.MolFromSmiles(smiles)
    else:
        mol = Chem.MolFromSmiles(clean_input)
        smiles = clean_input

    if mol is None:
        return None, "RDKit no pudo interpretar la molécula.", None

    Chem.SanitizeMol(mol)
    return mol, f"Molécula interpretada correctamente. Fuente: {source}", smiles
