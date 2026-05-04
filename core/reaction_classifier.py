from rdkit import Chem
from core.functional_groups import detect_functional_groups


def has_substructure(mol, smarts: str) -> bool:
    pattern = Chem.MolFromSmarts(smarts)
    return bool(pattern and mol.HasSubstructMatch(pattern))


def alkyl_halide_degree(mol):
    patt = Chem.MolFromSmarts("[CX4][Cl,Br,I,F]")
    matches = mol.GetSubstructMatches(patt)
    if not matches:
        return None
    carbon_idx = matches[0][0]
    carbon = mol.GetAtomWithIdx(carbon_idx)
    carbon_neighbors = [n for n in carbon.GetNeighbors() if n.GetAtomicNum() == 6]
    degree = len(carbon_neighbors)
    if degree <= 1:
        return "primario"
    if degree == 2:
        return "secundario"
    return "terciario"


def alcohol_degree(mol):
    patt = Chem.MolFromSmarts("[CX4][OX2H]")
    matches = mol.GetSubstructMatches(patt)
    if not matches:
        return None
    carbon_idx = matches[0][0]
    carbon = mol.GetAtomWithIdx(carbon_idx)
    c_neighbors = [n for n in carbon.GetNeighbors() if n.GetAtomicNum() == 6]
    degree = len(c_neighbors)
    if degree <= 1:
        return "primario"
    if degree == 2:
        return "secundario"
    return "terciario"


def detect_substrate_type(mol):
    groups = detect_functional_groups(mol)
    if "Halogenuro de alquilo" in groups:
        deg = alkyl_halide_degree(mol)
        return f"halogenuro de alquilo {deg}" if deg else "halogenuro de alquilo"
    if "Alcohol" in groups:
        deg = alcohol_degree(mol)
        return f"alcohol {deg}" if deg else "alcohol"
    if "Aldehído" in groups:
        return "aldehído"
    if "Cetona" in groups:
        return "cetona"
    if "Ácido carboxílico" in groups:
        return "ácido carboxílico"
    if "Éster" in groups:
        return "éster"
    if "Alqueno" in groups:
        return "alqueno"
    if "Alquino" in groups:
        return "alquino"
    if "Anillo aromático" in groups:
        return "aromático"
    if "Nitrilo" in groups:
        return "nitrilo"
    return "orgánico no clasificado"


def detect_reagent_role(reagent_text: str):
    r = reagent_text.lower().replace(" ", "").replace("-", "")
    strong_bases = ["naoh", "koh", "naome", "meona", "etona", "naoet", "nh2", "nah"]
    bulky_bases = ["tbuok", "tertbuok", "lda"]
    strong_acids = ["hbr", "hcl", "hi", "h2so4", "h3o+", "h+"]
    oxidants = ["kmno4", "cro3", "pcc", "jones", "k2cr2o7", "na2cr2o7"]
    mild_oxidants = ["pcc"]
    strong_oxidants = ["kmno4", "cro3", "jones", "k2cr2o7", "na2cr2o7"]
    reducers = ["nabh4", "lialh4", "h2pd", "h2/ni", "h2pt"]
    grignard = ["mgbr", "mgcl", "rmgx", "ch3mgbr", "phmgbr"]
    electrophilic_aromatic = ["br2febr3", "br2/fe", "cl2fecl3", "hno3h2so4", "so3h2so4", "ch3clalcl3"]
    heat_terms = ["calor", "heat", "∆", "delta"]
    weak_nucleophiles = ["h2o", "roh", "meoh", "etoh"]

    if any(x in r for x in electrophilic_aromatic):
        return "electrófilo para sustitución aromática"
    if any(x in r for x in grignard):
        return "organometálico tipo Grignard"
    if any(x in r for x in mild_oxidants):
        return "oxidante suave"
    if any(x in r for x in strong_oxidants):
        return "oxidante fuerte"
    if any(x in r for x in oxidants):
        return "oxidante"
    if any(x in r for x in reducers):
        return "reductor"
    if any(x in r for x in bulky_bases):
        return "base fuerte voluminosa"
    if any(x in r for x in strong_bases):
        if any(x in r for x in heat_terms):
            return "base fuerte con calor"
        return "base fuerte / nucleófilo fuerte"
    if any(x in r for x in strong_acids):
        return "ácido fuerte / electrófilo"
    if "br2" in r or "cl2" in r:
        return "halogenante"
    if any(x in r for x in weak_nucleophiles):
        return "nucleófilo débil / solvente prótico"
    return "reactivo no clasificado"


def classify_reaction(mol, molecule_input: str, reagent_text: str):
    substrate = detect_substrate_type(mol)
    reagent_role = detect_reagent_role(reagent_text)
    reaction_type = "No determinada"
    confidence = "baja"
    reasoning = "No se encontró una regla suficientemente específica para esta combinación."

    s = substrate.lower()

    if "halogenuro de alquilo primario" in s and reagent_role == "base fuerte / nucleófilo fuerte":
        reaction_type = "SN2 probable"
        confidence = "alta"
        reasoning = "Halogenuros primarios con nucleófilos fuertes favorecen sustitución SN2."
    elif "halogenuro de alquilo secundario" in s and reagent_role == "base fuerte / nucleófilo fuerte":
        reaction_type = "SN2/E2 en competencia"
        confidence = "media"
        reasoning = "En sustratos secundarios compiten sustitución y eliminación."
    elif "halogenuro de alquilo terciario" in s and reagent_role in ["base fuerte / nucleófilo fuerte", "base fuerte con calor", "base fuerte voluminosa"]:
        reaction_type = "E2 probable"
        confidence = "alta"
        reasoning = "El impedimento estérico bloquea SN2 y la base favorece eliminación."
    elif "halogenuro de alquilo terciario" in s and reagent_role == "nucleófilo débil / solvente prótico":
        reaction_type = "SN1/E1 probable"
        confidence = "media"
        reasoning = "Sustrato terciario puede formar carbocatión en medio prótico."
    elif "halogenuro de alquilo" in s and reagent_role == "base fuerte con calor":
        reaction_type = "E2 probable"
        confidence = "media"
        reasoning = "Base fuerte y calor favorecen eliminación beta."
    elif "alcohol primario" in s and reagent_role == "oxidante suave":
        reaction_type = "Oxidación a aldehído"
        confidence = "alta"
        reasoning = "PCC suele oxidar alcoholes primarios hasta aldehídos."
    elif "alcohol primario" in s and reagent_role == "oxidante fuerte":
        reaction_type = "Oxidación a ácido carboxílico"
        confidence = "alta"
        reasoning = "Oxidantes fuertes llevan alcohol primario hasta ácido carboxílico."
    elif "alcohol secundario" in s and "oxidante" in reagent_role:
        reaction_type = "Oxidación a cetona"
        confidence = "alta"
        reasoning = "Alcoholes secundarios se oxidan a cetonas."
    elif "alcohol terciario" in s and "oxidante" in reagent_role:
        reaction_type = "Sin oxidación común"
        confidence = "media"
        reasoning = "Alcoholes terciarios no se oxidan fácilmente sin ruptura C-C."
    elif s in ["aldehído", "cetona"] and reagent_role == "reductor":
        reaction_type = "Reducción de carbonilo a alcohol"
        confidence = "alta"
        reasoning = "El hidruro ataca al carbono carbonílico."
    elif s in ["aldehído", "cetona"] and reagent_role == "organometálico tipo Grignard":
        reaction_type = "Adición de Grignard a carbonilo"
        confidence = "media"
        reasoning = "Grignard actúa como nucleófilo carbonado sobre el carbonilo."
    elif s == "alqueno" and reagent_role == "ácido fuerte / electrófilo":
        reaction_type = "Adición electrofílica a alqueno"
        confidence = "media"
        reasoning = "El enlace pi ataca al electrófilo."
    elif s == "alqueno" and reagent_role == "halogenante":
        reaction_type = "Halogenación de alqueno"
        confidence = "media"
        reasoning = "Br2 o Cl2 se adicionan al doble enlace."
    elif s == "aromático" and reagent_role == "electrófilo para sustitución aromática":
        reaction_type = "Sustitución electrofílica aromática"
        confidence = "media"
        reasoning = "El anillo aromático reacciona con electrófilo y recupera aromaticidad."
    elif s == "ácido carboxílico" and "roh" in reagent_text.lower():
        reaction_type = "Esterificación de Fischer probable"
        confidence = "media"
        reasoning = "Ácido carboxílico y alcohol en medio ácido forman éster."
    elif s == "éster" and ("h2o" in reagent_text.lower() or "oh" in reagent_text.lower()):
        reaction_type = "Hidrólisis de éster probable"
        confidence = "media"
        reasoning = "Los ésteres se hidrolizan en medio ácido o básico."

    return {
        "substrate_type": substrate,
        "reagent_role": reagent_role,
        "reaction_type": reaction_type,
        "confidence": confidence,
        "reasoning": reasoning,
        "input_molecule": molecule_input,
        "input_reagent": reagent_text
    }
