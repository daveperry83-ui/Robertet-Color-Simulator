import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Configuración técnica para evitar conflictos en servidores web
matplotlib.use('Agg') 

# 1. ESTILO Y CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Robertet Color Stability Lab", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #d1d8e0; padding: 15px; border-radius: 10px; background-color: white; }
    .color-box {
        height: 150px;
        width: 100%;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        text-shadow: 1px 1px 2px black;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. PANEL LATERAL (CONTROLES)
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=200)
st.sidebar.header("Formulation Controls")

colorant = st.sidebar.selectbox("Select Pigment", 
    ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"])

matrix = st.sidebar.radio("Base Matrix", ["Water", "Milk", "Oil"], horizontal=True)

temp = st.sidebar.slider("Temperature (°C)", 20, 130, 90)
ph_val = st.sidebar.slider("pH Level", 2.0, 10.0, 7.0)
alcohol = st.sidebar.slider("Alcohol Content (%)", 0, 40, 0)

# 3. LÓGICA DE COLOR DINÁMICO (QUÍMICA VISUAL)
def get_dynamic_color(name, stability_pct, ph):
    # Colores base en Hex
    base_colors = {
        "Beta-carotene": "#FFB300", "Annato": "#FF8C00", "Paprika": "#E63900",
        "Norbixin": "#D2691E", "Curcumin": "#FFEA00", "Natural Chlorophyll": "#228B22",
        "Red Beet": "#C71585", "Spirulina": "#4169E1"
    }
    
    color = base_colors[name]
    
    # Lógica de cambio de color por pH (Indicadores Naturales)
    if name == "Red Beet":
        if ph > 7.0: color = "#8B008B" # Vira a púrpura/oscuro
        if ph > 8.5: color = "#5D4037" # Vira a marrón (degradación)
    elif name == "Curcumin":
        if ph > 8.0: color = "#FF4500" # Vira a naranja rojizo
    elif name == "Natural Chlorophyll":
        if ph < 5.0: color = "#6B8E23" # Feofitinización (verde oliva)

    return color

# 4. CÁLCULO CINÉTICO
time = np.linspace(0, 60, 100)
rates = {
    "Beta-carotene": 0.001, "Annato": 0.002, "Paprika": 0.003,
    "Norbixin": 0.005, "Curcumin": 0.01, "Natural Chlorophyll": 0.015,
    "Red Beet": 0.04, "Spirulina": 0.15
}

k = rates[colorant] * (temp / 85.0)**2
if alcohol > 15: k *= 1.4
stability = 100 * np.exp(-k * time)

# Reglas de incompatibilidad
error_msg = None
if matrix == "Oil" and colorant in ["Norbixin", "Red Beet", "Spirulina"]:
    stability = np.zeros_like(time)
    error_msg = f"{colorant} is insoluble in Oil."
elif ph_val < 4.0 and colorant == "Norbixin":
    stability = np.zeros_like(time)
    error_msg = "Norbixin precipitates at pH < 4.0."

# 5. RENDERIZADO DEL DASHBOARD
st.title("🔬 Color Stability Intelligence Dashboard")
st.markdown("---")

col_info, col_chart = st.columns([1, 2.5])

with col_info:
    st.subheader("Visual Analysis")
    
    # EL VISUALIZADOR DE COLOR
    current_color = get_dynamic_color(colorant, stability[-1], ph_val)
    opacity = max(0.1, stability[-1] / 100) # El color se desvanece con la degradación
    
    st.markdown(f"""
        <div class="color-box" style="background-color: {current_color}; opacity: {opacity};">
            SIMULATED APPEARANCE
        </div>
        """, unsafe_allow_html=True)
    
    final_stab = stability[-1]
    st.metric("Final Retention", f"{final_stab:.1f}%")
    
    if error_msg:
        st.error(f"⚠️ {error_msg}")
    elif final_stab > 80:
        st.success("STATUS: RECOMMENDED")
    else:
        st.error("STATUS: HIGH RISK")

with col_chart:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(time, stability, color=current_color, linewidth=4)
    ax.fill_between(time, stability, color=current_color, alpha=0.1)
    ax.set_ylim(-5, 105)
    ax.set_title(f"Degradación Térmica: {colorant}", fontsize=12, fontweight='bold')
    ax.set_ylabel("% Stability")
    ax.set_xlabel("Time (Minutes)")
    ax.grid(True, alpha=0.2)
    
    # Marca de agua
    ax.text(0.98, 0.02, 'ROBERTET R&D SIMULATOR', transform=ax.transAxes, 
            ha='right', color='gray', fontsize=8, alpha=0.5)
    
    st.pyplot(fig)

st.caption("Confidential: Robertet Ingredients Division - Predictive kinetic model for regional technical support.")
