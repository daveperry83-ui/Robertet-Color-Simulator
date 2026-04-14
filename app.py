import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Forzar renderizado estable
matplotlib.use('Agg') 

st.set_page_config(page_title="Robertet Color Lab", layout="wide")

st.title("🔬 Natural Colorants Stability Simulator")
st.markdown("### Regional R&D Division")

# --- SIDEBAR ---
st.sidebar.header("Parameters")
colorant = st.sidebar.selectbox("Colorant", ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"])
matrix = st.sidebar.selectbox("Matrix", ["Water", "Milk", "Oil"])
temp = st.sidebar.slider("Temperature (°C)", 20, 130, 90)
ph_val = st.sidebar.slider("pH", 2.0, 10.0, 7.0)

# --- LOGIC ---
time = np.linspace(0, 60, 100)
rates = {"Beta-carotene": 0.001, "Annato": 0.002, "Paprika": 0.003, "Norbixin": 0.005, "Curcumin": 0.01, "Natural Chlorophyll": 0.015, "Red Beet": 0.04, "Spirulina": 0.15}
current_rate = rates[colorant] * (temp / 80.0)**2
stability = 100 * np.exp(-current_rate * time)

# --- PLOT ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(time, stability, color='#2c3e50', linewidth=3)
ax.fill_between(time, stability, color='#3498db', alpha=0.1)
ax.set_ylim(-5, 105)
ax.set_xlabel("Minutes")
ax.set_ylabel("Stability %")
ax.grid(True, alpha=0.3)

# Lógica robusta para el Logo
logo_options = ['robertet_logo.png', 'robertet_logo.png.png']
logo_path = None
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
