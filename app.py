import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg') 

st.set_page_config(page_title="Robertet R&D Simulator", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🔒 CANDADO DE SEGURIDAD
# ==========================================
if "acceso_concedido" not in st.session_state: st.session_state.acceso_concedido = False
if not st.session_state.acceso_concedido:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=250)
        st.markdown("### 🔒 R&D Portal Access")
        clave = st.text_input("PIN:", type="password")
        if st.button("Unlock"):
            if clave == "LatAm2026": # Tu contraseña
                st.session_state.acceso_concedido = True
                st.rerun()
            else: st.error("❌ Access Denied.")
    st.stop()

# ==========================================
# 🌐 DICCIONARIO MULTILINGÜE
# ==========================================
t = {
    "English": {
        "title": "🔬 Comparative R&D Dashboard",
        "scen_a": "Scenario A", "scen_b": "Scenario B",
        "pigment": "Select Pigment", "matrix": "Base Matrix", 
        "temp": "Processing Temp (°C)", "ph": "pH Level",
        "chart": "Thermal Degradation Comparison", "time": "Time (Minutes)",
        "retention": "Final Retention", "warning": "High Loss", "success": "Recommended"
    },
    "Español": {
        "title": "🔬 Dashboard Comparativo I+D",
        "scen_a": "Escenario A", "scen_b": "Escenario B",
        "pigment": "Seleccionar Pigmento", "matrix": "Matriz Base", 
        "temp": "Temp. de Proceso (°C)", "ph": "Nivel de pH",
        "chart": "Comparativa de Degradación Térmica", "time": "Tiempo (Minutos)",
        "retention": "Retención Final", "warning": "Pérdida Alta", "success": "Recomendado"
    },
    "Português": {
        "title": "🔬 Dashboard Comparativo P&D",
        "scen_a": "Cenário A", "scen_b": "Cenário B",
        "pigment": "Selecionar Pigmento", "matrix": "Matriz Base", 
        "temp": "Temp. de Processo (°C)", "ph": "Nível de pH",
        "chart": "Comparação de Degradação Térmica", "time": "Tempo (Minutos)",
        "retention": "Retenção Final", "warning": "Alta Perda", "success": "Recomendado"
    }
}

st.markdown("""
    <style>
    .color-box { height: 100px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; text-shadow: 1px 1px 2px black; margin-bottom: 15px;}
    .stMetric { border: 1px solid #d1d8e0; padding: 10px; border-radius: 10px; background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: LENGUAJE ---
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=180)
lang = st.sidebar.radio("🌐 Language / Idioma", ["English", "Español", "Português"])
_ = t[lang] # Selector de idioma activo

st.title(_["title"])
st.markdown("---")

# --- LÓGICA DE COLOR Y CINÉTICA ---
def get_color(name, ph):
    colors = {"Beta-carotene": "#FFB300", "Annato": "#FF8C00", "Paprika": "#E63900", "Norbixin": "#D2691E", "Curcumin": "#FFEA00", "Natural Chlorophyll": "#228B22", "Red Beet": "#C
