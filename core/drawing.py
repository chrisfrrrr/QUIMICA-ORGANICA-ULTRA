from rdkit import Chem
import urllib.parse


def mol_to_image(mol, size=(500, 350)):
    """
    Versión compatible con Streamlit Cloud.
    No usa rdkit.Chem.Draw porque puede fallar en la nube.
    Devuelve una URL PNG generada por PubChem a partir del SMILES.
    """
    if mol is None:
        return None

    try:
        smiles = Chem.MolToSmiles(mol)
        encoded = urllib.parse.quote(smiles, safe="")
        width, height = size
        return f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{encoded}/PNG?image_size={width}x{height}"
    except Exception:
        return None
