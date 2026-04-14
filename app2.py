import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import colorsys
import matplotlib.colors as mcolors

# Renderizado web estable
matplotlib.use('Agg') 

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Robertet R&D Color Intelligence", layout="wide")

# ==========================================
# 🔒 SEGURIDAD (PIN: LatAm2026)
# ==========================================
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=300)
        st.markdown("### 🔒 R&D Portal - Latin America")
        clave = st.text_input("PIN de Acceso / Access PIN:", type="password")
        if st.button("Unlock Simulator"):
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
        "compare": "Modo Comparativo", "ret": "Retención Final",
        "uv": "Empaque (Filtro UV)", "uv_opts": ["Transparente (UV Alto)", "Semi-Opaco", "Opaco/Lata (Sin UV)"],
        "app": "Aplicación Final", "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "Nota Técnica R&D:", "beta_msg": "🧪 VERSIÓN BETA: Algoritmo predictivo en fase
