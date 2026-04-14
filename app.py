import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg') 

# 1. ESTILO Y CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Robertet Color Stability Lab", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #d1d8e0; padding: 15px; border-radius: 10px; background-color: white; }
    .color-box {
        height: 120px; width: 100%; border-radius: 15px; border: 2px solid #e0e0e0;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: bold; text-shadow: 1px 1px 2px black; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. PANEL LATERAL (CONTROLES GLOBALES)
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=200)
st.sidebar.header("1. Application Matrix")

colorant = st.sidebar.selectbox("Select Pigment", 
    ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"])
application = st.sidebar.selectbox("Target Application", 
    ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"])
matrix = st.sidebar.radio("Base Matrix", ["Water", "Milk", "Oil"], horizontal=True)
ph_val = st.sidebar.slider("pH Level", 2.0, 10.0, 7.0)
alcohol = st.sidebar.slider("Alcohol Content (%)", 0, 40, 0)

# Controles de Proceso
st.sidebar.header("2. Processing Parameters")
temp = st.sidebar.slider("Pasteurization/Processing Temp (°C)", 20, 130, 90)

# Controles de Anaquel
st.sidebar.header("3. Storage & Packaging")
storage_temp = st.sidebar.slider("Storage Temp (°C)", 4, 40, 25)
packaging = st.sidebar.selectbox("Light Barrier (UV)", ["Clear (High UV)", "Semi-Opaque", "Opaque/Foil (No UV)"])
target_months = st.sidebar.slider("Target Shelf Life (Months)", 1, 24, 6)


# 3. LÓGICA DE COLOR DINÁMICO
def get_dynamic_color(name, stability_pct, ph):
    base_colors = {
        "Beta-carotene": "#FFB300", "Annato": "#FF8C00", "Paprika": "#E63900",
        "Norbixin": "#D2691E", "Curcumin": "#FFEA00", "Natural Chlorophyll": "#228B22",
        "Red Beet": "#C71585", "Spirulina": "#4169E1"
    }
    color = base_colors[name]
    if name == "Red Beet":
        if ph > 7.0: color = "#8B008B" 
        if ph > 8.5: color = "#5D4037" 
    elif name == "Curcumin":
        if ph > 8.0: color = "#FF4500" 
    elif name == "Natural Chlorophyll":
        if ph < 5.0: color = "#6B8E23" 
    return color

# 4. CINÉTICA: PROCESAMIENTO TÉRMICO (Minutos)
time_proc = np.linspace(0, 60, 100)
rates = {
    "Beta-carotene": 0.001, "Annato": 0.002, "Paprika": 0.003,
    "Norbixin": 0.005, "Curcumin": 0.01, "Natural Chlorophyll": 0.015,
    "Red Beet": 0.04, "Spirulina": 0.15
}

k_proc = rates[colorant] * (temp / 85.0)**2
if alcohol > 15: k_proc *= 1.4
stab_proc = 100 * np.exp(-k_proc * time_proc)

# Reglas de incompatibilidad
error_msg = None
if matrix == "Oil" and colorant in ["Norbixin", "Red Beet", "Spirulina"]:
    stab_proc = np.zeros_like(time_proc)
    error_msg = f"{colorant} is insoluble in Oil matrices."
elif ph_val < 4.0 and colorant == "Norbixin":
    stab_proc = np.zeros_like(time_proc)
    error_msg = "Norbixin precipitates at pH < 4.0."

final_proc_stab = stab_proc[-1]

# 5. CINÉTICA: VIDA DE ANAQUEL (Días)
days = np.linspace(0, target_months * 30, 100)

# Factor UV según empaque y colorante
uv_multiplier = 1.0
if packaging == "Clear (High UV)":
    # Curcumina, Clorofila y Espirulina son extremadamente sensibles a la luz
    if colorant in ["Curcumin", "Natural Chlorophyll", "Spirulina"]: uv_multiplier = 4.0
    else: uv_multiplier = 2.0
elif packaging == "Semi-Opaque":
    uv_multiplier = 1.5

# El deterioro en frío/ambiente es mucho más lento (aprox 1% de la tasa de calor extremo)
k_shelf = (rates[colorant] * 0.015) * (storage_temp / 20.0) * uv_multiplier
stab_shelf = final_proc_stab * np.exp(-k_shelf * days)
final_shelf_stab = stab_shelf[-1]


# 6. RENDERIZADO DEL DASHBOARD
st.title("🔬 R&D Intelligence Dashboard: Stability & Shelf Life")
st.markdown("---")

# PESTAÑAS (TABS) PARA ORGANIZAR LA INFO
tab1, tab2 = st.tabs(["🔥 Thermal Processing (Fábrica)", "📅 Shelf Life Projection (Supermercado)"])

with tab1:
    col_info, col_chart = st.columns([1, 2.5])
    with col_info:
        st.subheader("Processing Results")
        c_color = get_dynamic_color(colorant, final_proc_stab, ph_val)
        st.markdown(f'<div class="color-box" style="background-color: {c_color}; opacity: {max(0.1, final_proc_stab/100)};">POST-PROCESSING APPEARANCE</div>', unsafe_allow_html=True)
        st.metric("Survival after 60 mins", f"{final_proc_stab:.1f}%")
        
        if error_msg: st.error(f"⚠️ {error_msg}")
        elif final_proc_stab > 80: st.success("✅ RECOMMENDED for Process")
        else: st.warning("⚠️ HIGH LOSS during process")

    with col_chart:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(time_proc, stab_proc, color=c_color, linewidth=4)
        ax.fill_between(time_proc, stab_proc, color=c_color, alpha=0.1)
        ax.set_ylim(-5, 105); ax.set_ylabel("% Retention"); ax.set_xlabel("Processing Time (Minutes)")
        ax.set_title(f"Thermal Stress Curve: {colorant} at {temp}°C", fontweight='bold')
        ax.grid(True, alpha=0.2)
        st.pyplot(fig)

with tab2:
    col_info2, col_chart2 = st.columns([1, 2.5])
    with col_info2:
        st.subheader("Shelf Life Results")
        end_color = get_dynamic_color(colorant, final_shelf_stab, ph_val)
        st.markdown(f'<div class="color-box" style="background-color: {end_color}; opacity: {max(0.1, final_shelf_stab/100)};">END OF SHELF LIFE APPEARANCE</div>', unsafe_allow_html=True)
        
        st.metric(f"Retention at {target_months} Months", f"{final_shelf_stab:.1f}%", 
                  delta=f"-{(final_proc_stab - final_shelf_stab):.1f}% from factory", delta_color="inverse")
        
        if final_shelf_stab > 70: st.success("✅ OPTIMAL SHELF LIFE")
        elif final_shelf_stab > 50: st.warning("⚠️ NOTICEABLE FADING - Evaluate overdosing")
        else: st.error("❌ SEVERE COLOR LOSS")
        
        st.info(f"**Insight:** Packaging set to '{packaging}'. Storage at {storage_temp}°C.")

    with col_chart2:
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.plot(days, stab_shelf, color=end_color, linewidth=4, linestyle='--')
        ax2.fill_between(days, stab_shelf, color=end_color, alpha=0.1)
        ax2.set_ylim(-5, 105); ax2.set_ylabel("% Retention"); ax2.set_xlabel("Time in Market (Days)")
        ax2.set_title(f"Shelf Life Projection: {target_months} Months", fontweight='bold')
        ax2.grid(True, alpha=0.2)
        st.pyplot(fig2)

st.markdown("---")
st.caption("Confidential: Robertet Ingredients Division - Predictive kinetic models include temperature Arrhenius factors and UV exposure variables.")
