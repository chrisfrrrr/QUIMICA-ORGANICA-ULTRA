from rdkit.Chem import Draw


def mol_to_image(mol, size=(500, 350)):
    return Draw.MolToImage(mol, size=size)
