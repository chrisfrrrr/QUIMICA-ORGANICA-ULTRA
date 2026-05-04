from rdkit import Chem
import urllib.parse
import requests
from PIL import Image
from io import BytesIO


def mol_to_image(mol, size=(500, 350)):
    """
    Dibuja moléculas sin usar rdkit.Chem.Draw.
    Compatible con Streamlit Cloud.
    Usa NCI/Cactus como generador de imagen y PubChem como respaldo.
    """
    if mol is None:
        return None

    try:
        smiles = Chem.MolToSmiles(mol, isomericSmiles=True)
        encoded = urllib.parse.quote(smiles, safe="")

        # Opción 1: NCI/Cactus, mejor para SMILES complejos
        cactus_url = f"https://cactus.nci.nih.gov/chemical/structure/{encoded}/image"
        r = requests.get(cactus_url, timeout=15)

        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            return Image.open(BytesIO(r.content)).convert("RGB")

        # Opción 2: PubChem como respaldo
        pubchem_url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
            f"{encoded}/PNG?image_size={size[0]}x{size[1]}"
        )
        r = requests.get(pubchem_url, timeout=15)

        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            return Image.open(BytesIO(r.content)).convert("RGB")

        return None

    except Exception:
        return None
