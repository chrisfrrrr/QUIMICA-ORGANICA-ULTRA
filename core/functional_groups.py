from rdkit import Chem

FUNCTIONAL_GROUPS = {
    "Alcano": "[CX4]",
    "Alqueno": "C=C",
    "Alquino": "C#C",
    "Alcohol": "[OX2H][CX4]",
    "Fenol": "[OX2H]c",
    "Éter": "[OD2]([#6])[#6]",
    "Aldehído": "[CX3H1](=O)[#6,#1]",
    "Cetona": "[#6][CX3](=O)[#6]",
    "Ácido carboxílico": "[CX3](=O)[OX2H1]",
    "Éster": "[CX3](=O)[OX2][#6]",
    "Amida": "[NX3][CX3](=O)",
    "Amina": "[NX3;H2,H1,H0;!$(NC=O)]",
    "Halogenuro de alquilo": "[CX4][F,Cl,Br,I]",
    "Halogenuro de arilo": "a[F,Cl,Br,I]",
    "Nitrilo": "[CX2]#N",
    "Nitro": "[$([NX3](=O)=O),$([NX3+](=O)[O-])]",
    "Anillo aromático": "a",
    "Epóxido": "C1OC1",
    "Tiol": "[SX2H]",
    "Sulfuro": "[SX2]([#6])[#6]",
    "Anhídrido": "[CX3](=O)O[CX3](=O)",
    "Cloruro de acilo": "[CX3](=O)Cl",
}


def detect_functional_groups(mol):
    detected = []
    for name, smarts in FUNCTIONAL_GROUPS.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt and mol.HasSubstructMatch(patt):
            detected.append(name)
    return detected
