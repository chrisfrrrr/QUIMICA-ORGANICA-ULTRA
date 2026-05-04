import json
from pathlib import Path

import pandas as pd
import streamlit as st
from rdkit import Chem

from core.molecule_parser import parse_molecule
from core.name_resolver import resolve_name_to_smiles
from core.descriptors import molecular_report
from core.functional_groups import detect_functional_groups
from core.aromaticity import aromaticity_report
from core.stereochemistry import stereochemistry_report, compare_molecules
from core.reaction_classifier import classify_reaction
from core.reaction_engine import predict_products
from core.mechanism_explainer import explain_mechanism
from core.drawing import mol_to_image
from core.gemini_helper import gemini_explanation


st.set_page_config(page_title="IA Química Orgánica ULTRA", page_icon="🧪", layout="wide")

EXAMPLES = json.loads(Path("data/examples.json").read_text(encoding="utf-8"))


def example_select(section, label="Ejemplos precargados"):
    items = EXAMPLES[section]
    labels = [x["label"] for x in items]
    selected = st.selectbox(label, labels, key=f"example_{section}")
    return items[labels.index(selected)]


def input_controls(prefix, default_mode="Nombre / IUPAC", default_value="ethanol"):
    mode = st.selectbox("Tipo de entrada", ["SMILES", "Nombre / IUPAC"], index=1 if default_mode != "SMILES" else 0, key=f"{prefix}_mode")
    value = st.text_input("Molécula", default_value, key=f"{prefix}_value")
    use_pubchem = st.checkbox("Permitir consulta a PubChem si el nombre no está en el diccionario local", value=True, key=f"{prefix}_pubchem")
    return mode, value, use_pubchem


st.title("🧪 IA de Química Orgánica ULTRA")
st.caption("Con estructura desde IUPAC/nombre, ejemplos precargados, RDKit, reglas químicas y Gemini opcional.")

tabs = st.tabs([
    "🏠 Inicio",
    "✍️ IUPAC → estructura",
    "🔬 Analizador molecular",
    "🧪 Reacciones",
    "🌐 Aromaticidad",
    "🧬 Estereoquímica",
    "⚖️ Comparar compuestos",
    "🤖 Gemini opcional"
])

with tabs[0]:
    st.header("Panel principal")
    st.write("""
    Esta versión permite trabajar con SMILES o con nombres comunes/IUPAC. 
    Si el nombre no está en el diccionario local, la app puede consultar PubChem para obtener el SMILES y dibujar la estructura.
    """)
    st.subheader("Qué puedes hacer")
    st.markdown("""
    - Dibujar estructuras desde nombre IUPAC.
    - Analizar propiedades moleculares.
    - Detectar grupos funcionales.
    - Clasificar reacciones orgánicas.
    - Estimar productos básicos.
    - Analizar aromaticidad y estereoquímica.
    - Comparar compuestos.
    """)
    st.subheader("Ejemplos rápidos")
    st.dataframe(pd.DataFrame(EXAMPLES["reacciones"]), use_container_width=True)

with tabs[1]:
    st.header("✍️ Dibujar estructura desde nombre IUPAC o nombre común")
    ex = example_select("iupac")
    name = st.text_input("Nombre IUPAC / común", ex["name"], key="iupac_name")
    use_pubchem = st.checkbox("Usar PubChem si no está localmente", value=True, key="iupac_pubchem")

    if st.button("Convertir y dibujar", key="btn_iupac"):
        smiles, source = resolve_name_to_smiles(name, use_pubchem=use_pubchem)
        if not smiles:
            st.error(source)
        else:
            mol = Chem.MolFromSmiles(smiles)
            st.success(f"Estructura encontrada. Fuente: {source}")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(mol_to_image(mol), caption=name, width=380)
            with c2:
                st.write("**SMILES isomérico/canónico obtenido:**")
                st.code(smiles, language="text")
                st.write("**SMILES canónico RDKit:**")
                st.code(Chem.MolToSmiles(mol, isomericSmiles=True), language="text")
                st.write("**Grupos funcionales detectados:**")
                groups = detect_functional_groups(mol)
                st.write(", ".join(groups) if groups else "No detectados.")

with tabs[2]:
    st.header("🔬 Analizador molecular")
    ex = example_select("analizador")
    mode = ex["input_mode"]
    mol_text = ex["molecule"]
    input_mode = st.selectbox("Tipo de entrada", ["SMILES", "Nombre / IUPAC"], index=0 if mode == "SMILES" else 1, key="an_mode")
    molecule = st.text_input("Molécula", mol_text, key="an_mol")
    use_pubchem = st.checkbox("Permitir PubChem", value=True, key="an_pubchem")

    if st.button("Analizar molécula", key="btn_analyze"):
        mol, msg, resolved_smiles = parse_molecule(molecule, input_mode, use_pubchem=use_pubchem)
        if mol is None:
            st.error(msg)
        else:
            st.success(msg)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(mol_to_image(mol), caption="Estructura", width=350)
                st.code(resolved_smiles or Chem.MolToSmiles(mol), language="text")
            with c2:
                report = molecular_report(mol)
                groups = detect_functional_groups(mol)
                st.subheader("Propiedades moleculares")
                st.dataframe(pd.DataFrame(report.items(), columns=["Propiedad", "Valor"]), use_container_width=True)
                st.subheader("Grupos funcionales")
                st.write(", ".join(groups) if groups else "No detectados.")

with tabs[3]:
    st.header("🧪 Clasificador y predictor de reacciones")
    ex = example_select("reacciones")
    col1, col2, col3 = st.columns(3)
    with col1:
        rxn_mode = st.selectbox("Tipo de entrada", ["SMILES", "Nombre / IUPAC"], index=0 if ex["input_mode"] == "SMILES" else 1, key="rxn_mode")
    with col2:
        substrate_text = st.text_input("Sustrato", ex["substrate"], key="rxn_substrate")
    with col3:
        reagent_text = st.text_input("Reactivo / condiciones", ex["reagent"], key="rxn_reagent")
    use_pubchem = st.checkbox("Permitir PubChem", value=True, key="rxn_pubchem")

    if st.button("Clasificar reacción", key="btn_rxn"):
        mol, msg, resolved_smiles = parse_molecule(substrate_text, rxn_mode, use_pubchem=use_pubchem)
        if mol is None:
            st.error(msg)
        else:
            result = classify_reaction(mol, substrate_text, reagent_text)
            products = predict_products(mol, reagent_text, result)
            explanation = explain_mechanism(result)

            left, right = st.columns([1, 2])
            with left:
                st.image(mol_to_image(mol), caption="Sustrato", width=350)
                st.code(resolved_smiles or Chem.MolToSmiles(mol), language="text")
            with right:
                st.subheader("Diagnóstico")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Sustrato", result["substrate_type"])
                c2.metric("Reactivo", result["reagent_role"])
                c3.metric("Reacción", result["reaction_type"])
                c4.metric("Confianza", result["confidence"])
                st.write(result["reasoning"])

            st.subheader("Producto(s) estimado(s)")
            if products:
                cols = st.columns(min(len(products), 3))
                for i, p in enumerate(products):
                    pmol = Chem.MolFromSmiles(p["smiles"])
                    with cols[i % len(cols)]:
                        if pmol:
                            st.image(mol_to_image(pmol), caption=p["label"], width=300)
                        st.code(p["smiles"], language="text")
                        st.caption(p["note"])
            else:
                st.warning("Aún no hay transformación programada para esta combinación.")

            st.subheader("Explicación")
            st.write(explanation)

with tabs[4]:
    st.header("🌐 Clasificador de aromaticidad")
    ex = example_select("aromaticidad")
    ar_mode = st.selectbox("Tipo de entrada", ["SMILES", "Nombre / IUPAC"], index=0 if ex["input_mode"] == "SMILES" else 1, key="ar_mode")
    ar_text = st.text_input("Molécula", ex["molecule"], key="ar_text")
    use_pubchem = st.checkbox("Permitir PubChem", value=True, key="ar_pubchem")

    if st.button("Analizar aromaticidad", key="btn_ar"):
        mol, msg, _ = parse_molecule(ar_text, ar_mode, use_pubchem=use_pubchem)
        if mol is None:
            st.error(msg)
        else:
            report = aromaticity_report(mol)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(mol_to_image(mol), caption="Molécula", width=350)
            with c2:
                st.metric("Clasificación", report["classification"])
                st.write(report["explanation"])
                st.json(report)

with tabs[5]:
    st.header("🧬 Estereoquímica")
    ex = example_select("estereoquimica")
    st_mode = st.selectbox("Tipo de entrada", ["SMILES", "Nombre / IUPAC"], index=0 if ex["input_mode"] == "SMILES" else 1, key="st_mode")
    st_text = st.text_input("Molécula", ex["molecule"], key="st_text")
    use_pubchem = st.checkbox("Permitir PubChem", value=True, key="st_pubchem")

    if st.button("Analizar estereoquímica", key="btn_st"):
        mol, msg, _ = parse_molecule(st_text, st_mode, use_pubchem=use_pubchem)
        if mol is None:
            st.error(msg)
        else:
            report = stereochemistry_report(mol)
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(mol_to_image(mol), caption="Molécula", width=350)
            with c2:
                st.metric("Centros quirales", len(report["chiral_centers"]))
                st.code(report["isomeric_smiles"])
                st.json(report["chiral_centers"])
                st.write(report["explanation"])

with tabs[6]:
    st.header("⚖️ Comparar compuestos")
    ex = example_select("comparar")
    col1, col2 = st.columns(2)
    with col1:
        cmp1 = st.text_input("Compuesto A en SMILES", ex["a"])
    with col2:
        cmp2 = st.text_input("Compuesto B en SMILES", ex["b"])

    if st.button("Comparar", key="btn_cmp"):
        m1 = Chem.MolFromSmiles(cmp1)
        m2 = Chem.MolFromSmiles(cmp2)
        if m1 is None:
            st.error("No se pudo interpretar el compuesto A.")
        elif m2 is None:
            st.error("No se pudo interpretar el compuesto B.")
        else:
            report = compare_molecules(m1, m2)
            c1, c2 = st.columns(2)
            with c1:
                st.image(mol_to_image(m1), caption="Compuesto A", width=300)
            with c2:
                st.image(mol_to_image(m2), caption="Compuesto B", width=300)
            st.metric("Relación aproximada", report["relationship"])
            st.write(report["explanation"])
            st.json(report)

with tabs[7]:
    st.header("🤖 Explicación con Gemini opcional")
    ex = example_select("gemini")
    prompt = st.text_area("Pregunta química", ex["prompt"])
    if st.button("Consultar Gemini", key="btn_gemini"):
        st.write(gemini_explanation(prompt))
