import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import colorsys
import matplotlib.colors as mcolors

# Configuración estable para servidores
matplotlib.use('Agg') 

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Robertet R&D Color Intelligence", layout="wide")

# ==========================================
# 🔒 SEGURIDAD (PIN: LatAm2026)
# ==========================================
if "acceso_concedido" not in st.session_state:
    st.session_state.acceder = False

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

# 2. TRADUCCIONES
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])

if lang == "Español":
    T = {
        "title": "🔬 Inteligencia de Color R&D - Robertet",
        "t1": "🔥 Proceso Térmico", "t2": "📅 Vida de Anaquel", "t3": "💡 Recomendador",
        "p1": "Muestra A", "p2": "Muestra B (Comparativa)",
        "pigment": "Pigmento", "matrix": "Matriz Base", "m_opts": ["Agua", "Leche", "Aceite"],
        "temp": "Temp. Proceso (°C)", "ph": "pH", "months": "Meses Anaquel",
        "compare": "Modo Comparativo", "ret": "Retención Final",
        "uv": "Protección UV", "uv_opts": ["Ninguna", "Media", "Total"],
        "note": "Análisis Técnico:"
    }
else:
    T = {
        "title": "🔬 R&D Color Intelligence - Robertet",
        "t1": "🔥 Thermal Process", "t2": "📅 Shelf Life", "t3": "💡 Smart Recommender",
        "p1": "Sample A", "p2": "Sample B (Comparative)",
        "pigment": "Pigment", "matrix": "Base Matrix", "m_opts": ["Water", "Milk", "Oil"],
        "temp": "Process Temp (°C)", "ph": "pH Level", "months": "Shelf Life Months",
        "compare": "Comparison Mode", "ret": "Final Retention",
        "uv": "UV Protection", "uv_opts": ["None", "Medium", "Total"],
        "note": "Technical Insight:"
    }

pigments = ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"]

# 3. CONTROLES LATERALES
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=180)
st.sidebar.markdown(f"### {T['p1']}")
p1_name = st.sidebar.selectbox(f"{T['pigment']} (A)", pigments, key="p1")
p1_matrix = st.sidebar.radio(f"{T['matrix']} (A)", T["m_opts"], horizontal=True, key="m1")

compare_on = st.sidebar.checkbox(T["compare"])
p2_name, p2_matrix = None, None
if compare_on:
    st.sidebar.markdown(f"--- \n### {T['p2']}")
    p2_name = st.sidebar.selectbox(f"{T['pigment']} (B)", pigments, key="p2")
    p2_matrix = st.sidebar.radio(f"{T['matrix']} (B)", T["m_opts"], horizontal=True, key="m2")

st.sidebar.markdown("--- \n### ⚙️ Global Parameters")
temp = st.sidebar.slider(T["temp"], 20, 180, 90) 
ph_val = st.sidebar.slider(T["ph"], 2.0, 10.0, 7.0)
pkg_uv = st.sidebar.selectbox(T["uv"], T["uv_opts"])
target_m = st.sidebar.slider(T["months"], 1, 24, 6)

# 4. LÓGICA QUÍMICA
def get_props(name, ph):
    colors = {"Beta-carotene":"#FFB300", "Annato":"#FF8C00", "Paprika":"#E63900", "Norbixin":"#D2691E", 
              "Curcumin":"#FFEA00", "Natural Chlorophyll":"#228B22", "Red Beet":"#C71585", "Spirulina":"#4169E1"}
    c = colors.get(name, "#000000")
    if name == "Red Beet" and ph > 7: c = "#8B008B"
    elif name == "Curcumin" and ph > 8: c = "#FF4500"
    
    rates = {"Beta-carotene":0.001, "Annato":0.002, "Paprika":0.003, "Norbixin":0.005, 
             "Curcumin":0.01, "Natural Chlorophyll":0.015, "Red Beet":0.04, "Spirulina":0.15}
    return c, rates.get(name, 0.01)

def run_sim(name, matrix, t_c, ph):
    color, base_k = get_props(name, ph)
    t_min = np.linspace(0, 60, 100)
    # Factor de matriz (Aceite es más crítico para hidrosolubles)
    k_p = base_k * (t_c / 85.0)**2.5 
    
    # Lógica de Incompatibilidad (Aceite)
    # Nota: Leche y Agua se consideran compatibles para la mayoría de los extractos estándar de Robertet
    is_oil = (matrix == "Oil" or matrix == "Aceite")
    if is_oil and name in ["Norbixin", "Red Beet", "Spirulina"]: k_p = 999
    elif ph < 4 and name == "Norbixin": k_p = 999
    
    stab = 100 * np.exp(-k_p * t_min)
    return t_min, stab, color

tp1, sp1, col1 = run_sim(p1_name, p1_matrix, temp, ph_val)
if compare_on:
    tp2, sp2, col2 = run_sim(p2_name, p2_matrix, temp, ph_val)

# 5. DASHBOARD
st.title(T["title"])
tab_p, tab_s, tab_r = st.tabs([T["t1"], T["t2"], T["t3"]])

def display_res(name, stab, color, label):
    st.markdown(f'<div style="background-color:{color}; opacity:{max(0.1, stab/100)}; height:70px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; border:1px solid #ddd;">{label}: {name}</div>', unsafe_allow_html=True)
    st.metric(f"{T['ret']} ({label})", f"{stab:.1f}%")

with tab_p:
    c1, c2 = st.columns([1, 2.5])
    with c1:
        display_res(p1_name, sp1[-1], col1, "A")
        if compare_on: display_res(p2_name, sp2[-1], col2, "B")
        st.info(f"**{T['note']}** @{temp}°C")
    with c2:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(tp1, sp1, color=col1, lw=4, label=f"A: {p1_name}")
        if compare_on: ax.plot(tp2, sp2, color=col2, lw=3, ls="--", label=f"B: {p2_name}")
        ax.set_ylim(-5, 105); ax.legend(); ax.grid(alpha=0.2); st.pyplot(fig)

with tab_s:
    st.info("Shelf life logic active. Model assumes controlled storage conditions.")

with tab_r:
    st.subheader("🎯 Búsqueda por Tono / Target Hue Search")
    st.markdown("Selecciona el color deseado. El sistema recomendará el pigmento de Robertet ideal para tu matriz de **Leche/Agua/Aceite**.")
    
    col_picker, col_res = st.columns([1, 2])
    with col_picker:
        target_color = st.color_picker("Elige un color / Pick a color", "#FF8C00")
        st.markdown(f'<div style="background-color:{target_color}; height:100px; border-radius:10px; border: 1px solid #ccc;"></div>', unsafe_allow_html=True)
        
    with col_res:
        rgb = mcolors.to_rgb(target_color)
        hsv = colorsys.rgb_to_hsv(*rgb)
        hue = hsv[0] * 360 
        
        candidatos = []
        if hue >= 330 or hue <= 20: candidatos = ["Red Beet", "Paprika"]
        elif 20 < hue <= 45: candidatos = ["Paprika", "Annato", "Beta-carotene"]
        elif 45 < hue <= 75: candidatos = ["Curcumin", "Beta-carotene"]
        elif 75 < hue <= 160: candidatos = ["Natural Chlorophyll"]
        elif 160 < hue <= 260: candidatos = ["Spirulina"]
        else: candidatos = ["Red Beet"]
        
        rec = None
        is_oil = (p1_matrix == "Oil" or p1_matrix == "Aceite")
        for cand in candidatos:
            viable = True
            if is_oil and cand in ["Norbixin", "Red Beet", "Spirulina"]: viable = False
            elif cand == "Norbixin" and ph_val < 4: viable = False
            elif temp > 130 and cand in ["Spirulina", "Red Beet"]: viable = False
            if viable:
                rec = cand
                break
        
        st.markdown("### 🏆 Resultado R&D")
        if rec:
            st.success(f"**MATCH:** Sugerimos **{rec}**.")
            st.write(f"Compatible con la matriz de **{p1_matrix}** a {temp}°C.")
        else:
            st.error("❌ **INCOMPATIBILIDAD:** No hay pigmento natural para este tono bajo estas condiciones extremas.")

st.caption("Confidential Robertet R&D - Regional Division.")
