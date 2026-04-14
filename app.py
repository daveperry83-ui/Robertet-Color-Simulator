import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg') 

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Robertet Color Intelligence", layout="wide")

# ==========================================
# 🔒 SEGURIDAD (PIN: LatAm2026)
# ==========================================
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=300)
        st.markdown("### 🔒 Portal de Ingredientes R&D")
        pin_secreto = "LatAm2026" 
        clave = st.text_input("PIN de Acceso:", type="password")
        if st.button("Desbloquear"):
            if clave == pin_secreto:
                st.session_state.acceso_concedido = True
                st.rerun()
            else:
                st.error("PIN Incorrecto.")
    st.stop() 

# 2. DICCIONARIO MULTILINGÜE
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])
T = {
    "Español": {
        "title": "🔬 Dashboard de Inteligencia de Color",
        "tab1": "🔥 Procesamiento Térmico", "tab2": "📅 Vida de Anaquel",
        "p1": "Muestra A", "p2": "Muestra B (Comparación)",
        "pigment": "Seleccionar Pigmento", "matrix": "Matriz Base", "app": "Aplicación",
        "temp": "Temp. de Proceso (°C)", "ph": "Nivel de pH", "alc": "Contenido Alcohol (%)",
        "storage": "Temp. Almacenamiento (°C)", "pkg": "Barrera de Luz (UV)", "months": "Objetivo (Meses)",
        "results": "Resultados de Análisis", "retention": "Retención Final",
        "compare": "Activar Comparación", "uv_options": ["Claro (UV Alto)", "Semi-Opaco", "Opaco/Foil (Sin UV)"],
        "status_ok": "RECOMENDADO", "status_warn": "PÉRDIDA MODERADA", "status_err": "ALTO RIESGO",
        "time_min": "Tiempo (Minutos)", "time_days": "Tiempo en Mercado (Días)", "ret_pct": "% Retención"
    },
    "English": {
        "title": "🔬 Color Intelligence Dashboard",
        "tab1": "🔥 Thermal Processing", "tab2": "📅 Shelf Life Projection",
        "p1": "Sample A", "p2": "Sample B (Comparison)",
        "pigment": "Select Pigment", "matrix": "Base Matrix", "app": "Application",
        "temp": "Processing Temp (°C)", "ph": "pH Level", "alc": "Alcohol Content (%)",
        "storage": "Storage Temp (°C)", "pkg": "Light Barrier (UV)", "months": "Target (Months)",
        "results": "Analysis Results", "retention": "Final Retention",
        "compare": "Enable Comparison", "uv_options": ["Clear (High UV)", "Semi-Opaque", "Opaque/Foil (No UV)"],
        "status_ok": "RECOMMENDED", "status_warn": "MODERATE LOSS", "status_err": "HIGH RISK",
        "time_min": "Time (Minutes)", "time_days": "Time in Market (Days)", "ret_pct": "% Retention"
    }
}[lang]

# 3. BARRA LATERAL (CONTROLES)
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=180)
st.sidebar.markdown(f"### 1. {T['p1']}")
pigments = ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"]
p1_name = st.sidebar.selectbox(f"{T['pigment']} (A)", pigments, key="p1")
p1_matrix = st.sidebar.radio(f"{T['matrix']} (A)", ["Water", "Milk", "Oil"], horizontal=True, key="m1")

compare_mode = st.sidebar.checkbox(T["compare"])
p2_name, p2_matrix = None, None
if compare_mode:
    st.sidebar.markdown(f"--- \
