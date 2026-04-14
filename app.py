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
            if clave == "LatAm2026": 
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
_ = t[lang] 

st.title(_["title"])
st.markdown("---")

# --- LÓGICA DE COLOR Y CINÉTICA ---
def get_color(name, ph):
    # Lista formateada verticalmente para evitar errores al copiar
    colors = {
        "Beta-carotene": "#FFB300", 
        "Annato": "#FF8C00", 
        "Paprika": "#E63900", 
        "Norbixin": "#D2691E", 
        "Curcumin": "#FFEA00", 
        "Natural Chlorophyll": "#228B22", 
        "Red Beet": "#C71585", 
        "Spirulina": "#4169E1"
    }
    c = colors[name]
    if name == "Red Beet" and ph > 7.0: c = "#8B008B"
    if name == "Red Beet" and ph > 8.5: c = "#5D4037"
    if name == "Curcumin" and ph > 8.0: c = "#FF4500"
    if name == "Natural Chlorophyll" and ph < 5.0: c = "#6B8E23"
    return c

def calc_stab(name, temp, ph, matrix):
    time = np.linspace(0, 60, 100)
    # Lista formateada verticalmente
    rates = {
        "Beta-carotene": 0.001, 
        "Annato": 0.002, 
        "Paprika": 0.003, 
        "Norbixin": 0.005
