import requests
import urllib.parse
from rdkit import Chem

LOCAL_NAME_TO_SMILES = {
    "benzene": "c1ccccc1",
    "benzoic acid": "O=C(O)c1ccccc1",
    "ethanol": "CCO",
    "acetone": "CC(=O)C",
    "acetic acid": "CC(=O)O",
    "bromoethane": "CCBr",
    "2-bromobutane": "CCC(Br)C",
    "tert-butyl bromide": "CC(C)(C)Br",
    "geranial": "O=C/C=C(\\C)CC/C=C(\\C)C",
    "(e)-3,7-dimethyl-2,6-octadienal": "O=C/C=C(\\C)CC/C=C(\\C)C",
    "(e)-3,7-dimethylocta-2,6-dienal": "O=C/C=C(\\C)CC/C=C(\\C)C",
    "methyl ferulate": "COC(=O)/C=C/c1ccc(O)c(OC)c1",
    "methyl (e)-3-(4-hydroxy-3-methoxyphenyl)prop-2-enoate": "COC(=O)/C=C/c1ccc(O)c(OC)c1",
    "benceno": "c1ccccc1",
    "etanol": "CCO",
    "acetona": "CC(=O)C",
    "acido acetico": "CC(=O)O",
    "ácido acético": "CC(=O)O",
    "bromoetano": "CCBr",
    "2-bromobutano": "CCC(Br)C",
    "tert-butil bromuro": "CC(C)(C)Br",
}


def normalize_name(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )


def try_parse_as_smiles(text: str):
    """Detecta si el usuario escribió un SMILES aunque esté en la pestaña IUPAC."""
    try:
        mol = Chem.MolFromSmiles(text.strip())
        if mol is None:
            return None
        Chem.SanitizeMol(mol)
        return Chem.MolToSmiles(mol, isomericSmiles=True)
    except Exception:
        return None


def pubchem_name_to_smiles(name: str):
    try:
        encoded = urllib.parse.quote(name.strip(), safe="")
        url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
            f"{encoded}/property/IsomericSMILES,CanonicalSMILES/JSON"
        )
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None, f"PubChem nombre HTTP {r.status_code}"
        props = r.json().get("PropertyTable", {}).get("Properties", [])
        if not props:
            return None, "PubChem no devolvió propiedades."
        smiles = props[0].get("IsomericSMILES") or props[0].get("CanonicalSMILES")
        if not smiles:
            return None, "PubChem no devolvió SMILES."
        return smiles, "PubChem por nombre"
    except Exception as e:
        return None, f"Error PubChem nombre: {e}"


def cactus_name_to_smiles(name: str):
    try:
        encoded = urllib.parse.quote(name.strip(), safe="")
        url = f"https://cactus.nci.nih.gov/chemical/structure/{encoded}/smiles"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None, f"NCI/Cactus HTTP {r.status_code}"
        smiles = r.text.strip()
        if not smiles or "Page not found" in smiles:
            return None, "NCI/Cactus no devolvió SMILES."
        if Chem.MolFromSmiles(smiles) is None:
            return None, "NCI/Cactus devolvió SMILES inválido."
        return smiles, "NCI/Cactus"
    except Exception as e:
        return None, f"Error NCI/Cactus: {e}"


def resolve_name_to_smiles(name: str, use_pubchem: bool = True):
    """
    Resolver PRO:
    1. Si la entrada ya es SMILES, la acepta directamente.
    2. Busca en diccionario local.
    3. Consulta PubChem por nombre.
    4. Consulta NCI/Cactus como respaldo.
    """
    if not name or not name.strip():
        return None, "Entrada vacía."

    raw = name.strip()

    smiles_detected = try_parse_as_smiles(raw)
    if smiles_detected:
        return smiles_detected, "SMILES detectado automáticamente"

    key = normalize_name(raw)
    if key in LOCAL_NAME_TO_SMILES:
        return LOCAL_NAME_TO_SMILES[key], "Diccionario local"

    if not use_pubchem:
        return None, "No encontrado localmente y PubChem está desactivado."

    smiles, source = pubchem_name_to_smiles(raw)
    if smiles:
        return smiles, source

    smiles, source2 = cactus_name_to_smiles(raw)
    if smiles:
        return smiles, source2

    return None, f"No se pudo resolver la entrada. Detalles: {source} | {source2}"
