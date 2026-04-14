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

# ¡AQUÍ REGRESA LA APLICACIÓN!
application = st.sidebar.selectbox("Target Application", 
    ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"])

matrix = st.sidebar.radio("Base Matrix", ["Water", "Milk", "Oil"], horizontal=True)

temp = st.sidebar.slider("Temperature (°C)", 20, 130, 90)
ph_val = st.sidebar.slider("pH Level", 2.0, 10.0, 7.0)
alcohol = st.sidebar.slider("Alcohol Content (%)", 0, 40, 0)

# 3. LÓGICA DE COLOR DINÁMICO (QUÍMICA VISUAL)
def get_dynamic_color(name, stability_pct, ph):
    base_colors = {
        "Beta-carotene": "#FFB300", "Annato": "#FF8C00", "Paprika": "#E63900",
        "Norbixin": "#D2691E", "Curcumin": "#FFEA00", "Natural Chlorophyll": "#228B22",
        "Red Beet": "#C71585", "Spirulina": "#4169E1"
    }
    color = base_colors[name]
    
    # Viraje por pH
    if name == "Red Beet":
        if ph > 7.0: color = "#8B008B"
