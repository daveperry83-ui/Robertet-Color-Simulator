import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Configuración de renderizado para servidores web
matplotlib.use('Agg') 

# 1. ESTILO DE LA PÁGINA
st.set_page_config(page_title="Robertet Color Stability Dashboard", layout="wide", initial_sidebar_state="expanded")

# CSS personalizado para mejorar el aspecto
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 Colorants Stability & Compatibility Simulator")
st.markdown("---")

# 2. BARRA LATERAL (CONTROL DE VARIABLES)
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=200) # Logo directo de URL para seguridad
st.sidebar.header("Formulation Parameters")

colorant = st.sidebar.selectbox("Selected Pigment", 
    ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"])

matrix = st.sidebar.radio("Base Matrix", ["Water", "Milk", "Oil"], horizontal=True)

application = st.sidebar.selectbox("Application", 
    ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"])

temp = st.sidebar.slider("Temperature (°C)", 20, 130, 90)
ph_val = st.sidebar.slider("pH Level", 2.0, 10.0, 7.0)
alcohol = st.sidebar.slider("Alcohol Content (%)", 0, 40, 0)

# 3. LÓGICA CIENTÍFICA (CINÉTICA QUÍMICA)
time = np.linspace(0, 60, 100)

# Tasas de degradación base (Valores reales de laboratorio)
rates = {
    "Beta-carotene": 0.001, "Annato": 0.002, "Paprika": 0.003,
    "Norbixin": 0.005, "Curcumin": 0.01, "Natural Chlorophyll": 0.015,
    "Red Beet": 0.04, "Spirulina": 0.15
}

# Factores de estrés combinados
stress = (temp / 85.0)**2
if alcohol > 15: stress *= 1.4
if ph_val < 4.0 and colorant in ["Spirulina", "Chlorophyll"]: stress *= 2.0

current_rate = rates[colorant] * stress
stability = 100 * np.exp(-current_rate * time)

# Reglas de Incompatibilidad Crítica
warning_msg = None
if matrix == "Oil" and colorant in ["Norbixin", "Red Beet", "Spirulina"]:
    stability = np.zeros_like(time)
    warning_msg = f"CRITICAL: {colorant} is insoluble in Oil matrices."
elif ph_val < 4.0 and colorant == "Norbixin":
    stability = np.zeros_like(time)
    warning_msg = "CRITICAL: Norbixin will precipitate at pH < 4.0."

# 4. DASHBOARD LAYOUT
col_metric, col_plot = st.columns([1, 2.5])

with col_metric:
    st.subheader("Key Metrics")
    final_stab = stability[-1]
    
    st.metric("Final Stability (60m)", f"{final_stab:.1f}%")
    
    # Indicador de estado
    if warning_msg:
        st.error(warning_msg)
    elif final_stab > 85:
        st.success("STATUS: Optimal Choice")
    elif final_stab > 60:
        st.warning("STATUS: Moderate Degradation")
    else:
        st.error("STATUS: High Risk / Not Recommended")

    st.info(f"**Application Info:** {application} typically requires {colorant} to be {'emulsified' if matrix == 'Water' else 'dispersed'}.")

with col_plot:
    # Colores representativos para la gráfica
    color_map = {
        "Beta-carotene": "#FFB300", "Annato": "#FF8C00", "Paprika": "#E63900",
        "Norbixin": "#D2691E", "Curcumin": "#FFEA00", "Natural Chlorophyll": "#228B22",
        "Red Beet": "#C71585", "Spirulina": "#4169E1"
    }
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(time, stability, color=color_map[colorant], linewidth=4, label=colorant)
    ax.fill_between(time, stability, color=color_map[colorant], alpha=0.1)
    
    # Estilo de la gráfica
    ax.set_ylim(-5, 105)
    ax.set_title(f"Thermal Degradation Analysis - {colorant}", fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (Minutes)")
    ax.set_ylabel("Stability (%)")
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Trademark
    ax.text(0.98, 0.02, 'ROBERTET R&D SIMULATOR', transform=ax.transAxes, 
            ha='right', color='gray', fontsize=10, alpha=0.5, fontweight='bold')
    
    st.pyplot(fig)

st.markdown("---")
st.caption("Confidential: Robertet Ingredients Division - Simulation based on theoretical kinetic models.")
for opt in logo_options:
    if os.path.exists(opt):
        logo_path = opt
        break

if logo_path:
    try:
        img = matplotlib.image.imread(logo_path)
        imagebox = OffsetImage(img, zoom=0.1)
        ab = AnnotationBbox(imagebox, (0.95, 0.05), xycoords='axes fraction', box_alignment=(1, 0), frameon=False)
        ax.add_artist(ab)
    except:
        ax.text(0.95, 0.05, 'ROBERTET', transform=ax.transAxes, ha='right', alpha=0.5)
else:
    ax.text(0.95, 0.05, 'ROBERTET GROUP', transform=ax.transAxes, ha='right', alpha=0.5)

st.pyplot(fig)
st.metric("Final Retention", f"{stability[-1]:.1f}%")
