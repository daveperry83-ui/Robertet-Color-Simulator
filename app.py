import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os

# Configuración técnica para evitar pantallas negras
matplotlib.use('Agg') 

# 1. CONFIGURACIÓN DE MARCA Y ESTILO
st.set_page_config(page_title="Robertet R&D Simulator", layout="wide")

# CSS para un look más corporativo
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border: 1px solid #d1d8e0; padding: 20px; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. PANEL LATERAL (INPUTS)
# Logo de Robertet directo desde su web para que nunca falle
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=200)
st.sidebar.header("Formulation Controls")

colorant = st.sidebar.selectbox("Pigment", 
    ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"])

matrix = st.sidebar.radio("Matrix Base", ["Water", "Milk", "Oil"], horizontal=True)

temp = st.sidebar.slider("Process Temperature (°C)", 20, 130, 90)
ph_val = st.sidebar.slider("pH Level", 2.0, 10.0, 7.0)
alcohol = st.sidebar.slider("Alcohol %", 0, 40, 0)

# 3. LÓGICA DE SIMULACIÓN (DATOS CIENTÍFICOS)
time = np.linspace(0, 60, 100)
rates = {
    "Beta-carotene": 0.001, "Annato": 0.002, "Paprika": 0.003,
    "Norbixin": 0.005, "Curcumin": 0.01, "Natural Chlorophyll": 0.015,
    "Red Beet": 0.04, "Spirulina": 0.15
}

# Cálculo de estrés cinético
k = rates[colorant] * (temp / 85.0)**2
if alcohol > 15: k *= 1.3
stability = 100 * np.exp(-k * time)

# Reglas de compatibilidad Robertet
error_msg = None
if matrix == "Oil" and colorant in ["Norbixin", "Red Beet", "Spirulina"]:
    stability = np.zeros_like(time)
    error_msg = f"Incompatibility Detected: {colorant} requires a water-soluble environment."
elif ph_val < 4.0 and colorant == "Norbixin":
    stability = np.zeros_like(time)
    error_msg = "pH Alert: Norbixin precipitates in acidic conditions (< 4.0)."

# 4. DISEÑO DEL DASHBOARD
st.title("🔬 Color Stability Intelligence Dashboard")
st.markdown("---")

col_info, col_chart = st.columns([1, 2.5])

with col_info:
    st.subheader("Analysis Results")
    final_res = stability[-1]
    st.metric("Final Retention (%)", f"{final_res:.1f}%")
    
    if error_msg:
        st.error(f"⚠️ {error_msg}")
    elif final_res > 85:
        st.success("✅ HIGHLY STABLE: Recommended for this process.")
    elif final_res > 60:
        st.warning("⚠️ MODERATE LOSS: Validation in final matrix suggested.")
    else:
        st.error("❌ NOT RECOMMENDED: High thermal degradation.")

    st.write(f"**Application Note:** Ensure proper emulsification if using {colorant} in {matrix}-based beverages.")

with col_chart:
    # Mapeo de colores visuales
    c_map = {"Beta-carotene":"orange", "Annato":"#FF8C00", "Paprika":"red", "Norbixin":"#D2691E", 
             "Curcumin":"yellow", "Natural Chlorophyll":"green", "Red Beet":"#C71585", "Spirulina":"blue"}
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(time, stability, color=c_map[colorant], linewidth=4)
    ax.fill_between(time, stability, color=c_map[colorant], alpha=0.1)
    ax.set_ylim(-5, 105)
    ax.set_title(f"Thermal Degradation Curve: {colorant}", fontsize=12, fontweight='bold')
    ax.set_ylabel("Stability %")
    ax.set_xlabel("Time (Minutes)")
    ax.grid(True, alpha=0.2)
    
    # Marca de agua profesional
    ax.text(0.98, 0.05, 'ROBERTET GROUP - CONFIDENTIAL', transform=ax.transAxes, 
            ha='right', color='gray', fontsize=9, alpha=0.4, fontweight='bold')
    
    st.pyplot(fig)

st.markdown("---")
st.caption("Theoretical simulation based on Robertet's internal kinetic benchmarks for the Latin American market.")
