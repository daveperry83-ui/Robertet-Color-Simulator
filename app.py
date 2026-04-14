import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Renderizado web estable
matplotlib.use('Agg') 

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Robertet R&D Dashboard", layout="wide")

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
# ==========================================

# 2. DICCIONARIOS MULTILINGÜES (Formateados para evitar errores de GitHub)
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])

if lang == "Español":
    T = {
        "title": "🔬 Dashboard de Inteligencia de Color R&D",
        "t1": "🔥 Proceso Térmico", "t2": "📅 Vida de Anaquel",
        "p1": "Muestra A (Principal)", "p2": "Muestra B (Comparativa)",
        "pigment": "Pigmento", "matrix": "Matriz Base", "app": "Aplicación Final",
        "temp": "Temp. Proceso (°C)", "ph": "Nivel de pH", "alc": "Alcohol (%)",
        "storage": "Temp. Almacén (°C)", "pkg": "Empaque (Filtro UV)", "months": "Objetivo (Meses)",
        "compare": "Activar Comparación", "ret": "Retención",
        "uv_opts": ["Transparente (UV Alto)", "Semi-Opaco", "Opaco/Lata (Sin UV)"],
        "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "Nota Técnica R&D:"
    }
else:
    T = {
        "title": "🔬 R&D Color Intelligence Dashboard",
        "t1": "🔥 Thermal Processing", "t2": "📅 Shelf Life",
        "p1": "Sample A (Primary)", "p2": "Sample B (Comparative)",
        "pigment": "Pigment", "matrix": "Base Matrix", "app": "Target Application",
        "temp": "Process Temp (°C)", "ph": "pH Level", "alc": "Alcohol (%)",
        "storage": "Storage Temp (°C)", "pkg": "Packaging (UV Filter)", "months": "Target (Months)",
        "compare": "Enable Comparison", "ret": "Retention",
        "uv_opts": ["Clear (High UV)", "Semi-Opaque", "Opaque/Can (No UV)"],
        "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "R&D Technical Note:"
    }

pigments_list = [
    "Beta-carotene", "Annato", "Paprika", "Norbixin", 
    "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"
]

# 3. BARRA LATERAL (CONTROLES)
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=180)
st.sidebar.markdown(f"### 1. {T['p1']}")
p1_name = st.sidebar.selectbox(f"{T['pigment']} (A)", pigments_list, key="p1")
p1_matrix = st.sidebar.radio(f"{T['matrix']} (A)", ["Water", "Milk", "Oil"], horizontal=True, key="m1")

compare_mode = st.sidebar.checkbox(T["compare"])
p2_name = None
p2_matrix = None

if compare_mode:
    st.sidebar.markdown(f"--- \n### 2. {T['p2']}")
    p2_name = st.sidebar.selectbox(f"{T['pigment']} (B)", pigments_list, key="p2")
    p2_matrix = st.sidebar.radio(f"{T['matrix']} (B
