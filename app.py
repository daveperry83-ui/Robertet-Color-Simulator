import streamlit as st
import numpy as np
import plotly.graph_objects as go
import colorsys
import matplotlib.colors as mcolors

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Robertet R&D Color Intelligence", layout="wide", initial_sidebar_state="expanded")

# --- DISEÑO CSS LIMPIO ---
st.markdown("""
    <style>
    /* Recuadros de Color Visual */
    .color-card {
        height: 90px; border-radius: 12px; display: flex; align-items: center; 
        justify-content: center; color: white; font-weight: 600; font-size: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔒 SEGURIDAD (PIN: LatAm2026)
# ==========================================
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try:
            st.image("logo.png", width=300)
        except:
            st.warning("⚠️ Sube el archivo 'logo.png' a GitHub para visualizar el logotipo.")
        st.markdown("### 🔒 R&D Portal - Latin America")
        clave = st.text_input("PIN de Acceso / Access PIN:", type="password")
        if st.button("Unlock Simulator", use_container_width=True):
            if clave == "LatAm2026":
                st.session_state.acceso_concedido = True
                st.rerun()
            else:
                st.error("❌ Access Denied")
    st.stop() 

# 2. DICCIONARIOS MULTILINGÜES
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])

if lang == "Español":
    T = {
        "title": "🔬 Inteligencia de Color R&D - Robertet",
        "t1": "🔥 Proceso Térmico", "t2": "📅 Vida de Anaquel", "t3": "💡 Recomendador (BETA)",
        "p1": "Muestra A", "p2": "Muestra B (Comparativa)",
        "pigment": "Pigmento", "matrix": "Matriz Base", "m_opts": ["Agua", "Leche", "Aceite"],
        "temp": "Temp. Proceso (°C)", "ph": "pH", "months": "Meses Anaquel",
        "storage": "Temp. Almacén (°C)",
        "compare": "Modo Comparativo", "ret": "Retención Final",
        "uv": "Empaque (Filtro UV)", "uv_opts": ["Transparente (UV Alto)", "Semi-Opaco", "Opaco/Lata (Sin UV)"],
        "app": "Aplicación Final", "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "Nota Técnica R&D:", "beta_msg": "🧪 VERSIÓN BETA: Algoritmo predictivo en fase de calibración.",
        "time_m": "Tiempo (Minutos)", "time_d":
