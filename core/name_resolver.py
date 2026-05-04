import requests
from rdkit import Chem

LOCAL_NAME_TO_SMILES = {
    # Hidrocarburos simples
    "methane": "C",
    "ethane": "CC",
    "propane": "CCC",
    "butane": "CCCC",
    "pentane": "CCCCC",
    "hexane": "CCCCCC",
    "ethene": "C=C",
    "ethylene": "C=C",
    "propene": "CC=C",
    "cyclohexane": "C1CCCCC1",
    "cyclohexene": "C1=CCCCC1",
    "cyclopenta-1,3-diene": "C1C=CC=C1",
    "benzene": "c1ccccc1",
    "toluene": "Cc1ccccc1",
    "phenol": "Oc1ccccc1",
    "aniline": "Nc1ccccc1",
    "benzoic acid": "O=C(O)c1ccccc1",

    # Alcoholes
    "methanol": "CO",
    "ethanol": "CCO",
    "propan-1-ol": "CCCO",
    "1-propanol": "CCCO",
    "propan-2-ol": "CC(O)C",
    "2-propanol": "CC(O)C",
    "isopropanol": "CC(O)C",
    "butan-1-ol": "CCCCO",
    "butan-2-ol": "CCC(O)C",
    "tert-butanol": "CC(C)(C)O",
    "lactic acid": "CC(O)C(=O)O",

    # Carbonilos y ácidos
    "methanal": "C=O",
    "formaldehyde": "C=O",
    "ethanal": "CC=O",
    "acetaldehyde": "CC=O",
    "propanone": "CC(=O)C",
    "propan-2-one": "CC(=O)C",
    "acetone": "CC(=O)C",
    "ethanoic acid": "CC(=O)O",
    "acetic acid": "CC(=O)O",
    "ethyl ethanoate": "CC(=O)OCC",
    "ethyl acetate": "CC(=O)OCC",

    # Halogenuros
    "bromoethane": "CCBr",
    "ethyl bromide": "CCBr",
    "chloroethane": "CCCl",
    "2-bromobutane": "CCC(Br)C",
    "tert-butyl bromide": "CC(C)(C)Br",
    "2-chloropropane": "CC(Cl)C",

    # Español frecuente
    "benceno": "c1ccccc1",
    "tolueno": "Cc1ccccc1",
    "fenol": "Oc1ccccc1",
    "anilina": "Nc1ccccc1",
    "etanol": "CCO",
    "metanol": "CO",
    "isopropanol": "CC(O)C",
    "acetona": "CC(=O)C",
    "formaldehido": "C=O",
    "formaldehído": "C=O",
    "acetaldehido": "CC=O",
    "acetaldehído": "CC=O",
    "acido acetico": "CC(=O)O",
    "ácido acético": "CC(=O)O",
    "acetato de etilo": "CC(=O)OCC",
    "bromoetano": "CCBr",
    "cloroetano": "CCCl",
    "2-bromobutano": "CCC(Br)C",
    "tert-butil bromuro": "CC(C)(C)Br",
}


def normalize_name(name: str) -> str:
    return name.strip().lower()


def resolve_name_to_smiles(name: str, use_pubchem: bool = True):
    """
    Convierte nombre común o IUPAC a SMILES.
    Primero usa diccionario local. Si no aparece y use_pubchem=True, consulta PubChem.
    """
    key = normalize_name(name)
    if key in LOCAL_NAME_TO_SMILES:
        return LOCAL_NAME_TO_SMILES[key], "Diccionario local"

    if not use_pubchem:
        return None, "No encontrado en diccionario local"

    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{requests.utils.quote(name)}/property/IsomericSMILES/JSON"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, f"PubChem no encontró el compuesto. Código HTTP: {response.status_code}"

        data = response.json()
        props = data.get("PropertyTable", {}).get("Properties", [])
        if not props:
            return None, "PubChem no devolvió propiedades."

        smiles = props[0].get("IsomericSMILES")
        if not smiles:
            return None, "PubChem no devolvió SMILES."

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None, "PubChem devolvió un SMILES que RDKit no pudo interpretar."

        return smiles, "PubChem"
    except Exception as e:
        return None, f"No se pudo consultar PubChem: {e}"
