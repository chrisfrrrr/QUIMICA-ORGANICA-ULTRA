# IA de Química Orgánica ULTRA

Versión ampliada de la app de química orgánica.

## Mejoras principales

- Conversión de nombre IUPAC o nombre común a estructura usando:
  1. Diccionario local.
  2. PubChem si hay internet.
- Ejemplos precargados en cada pestaña.
- Analizador molecular con propiedades, grupos funcionales y estructura.
- Clasificación de reacciones orgánicas.
- Predicción básica de productos.
- Aromaticidad.
- Estereoquímica.
- Comparación de compuestos.
- Generador de estructura desde nombre IUPAC.
- Explicación local y Gemini opcional.

## Instalación en PowerShell

```powershell
cd IA_Quimica_Organica_ULTRA
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Si PowerShell bloquea el entorno virtual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

## API Key de Gemini opcional

Crea un archivo `.env`:

```text
GEMINI_API_KEY=TU_API_KEY_AQUI
```

## Importante

La conversión IUPAC → estructura usa PubChem cuando hay internet. Si no hay internet, funcionará con el diccionario local de ejemplos.
