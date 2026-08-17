import streamlit as st
import numpy as np
import plotly.graph_objects as go
import colorsys
import matplotlib.colors as mcolors

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Robertet R&D Color Intelligence", layout="wide", initial_sidebar_state="expanded")

# --- DISEÑO CSS PREMIUM ---
st.markdown("""
    <style>
    .color-card {
        height: 90px; border-radius: 12px; display: flex; align-items: center; 
        justify-content: center; color: white; font-weight: 600; font-size: 1.2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SEGURIDAD
if "acceso_concedido" not in st.session_state: st.session_state.acceso_concedido = False
if not st.session_state.acceso_concedido:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try: st.image("logo.png", width=300)
        except: st.warning("⚠️ Sube el archivo 'logo.png' a GitHub.")
        st.markdown("### 🔒 R&D Portal - Latin America")
        clave = st.text_input("PIN de Acceso:", type="password")
        if st.button("Unlock Simulator", use_container_width=True):
            if clave == "LatAm2026":
                st.session_state.acceso_concedido = True
                st.rerun()
            else: st.error("❌ Access Denied")
    st.stop()

# 3. DICCIONARIOS MULTILINGÜES
lang = st.sidebar.selectbox("🌐 Language", ["Español", "English"])
T = {
    "title": "🔬 Inteligencia de Color R&D - Robertet",
    "m_opts": ["Agua", "Leche", "Aceite", "Carne"],
    "uv_opts": ["Transparente (UV Alto)", "Semi-Opaco", "Opaco/Lata (Sin UV)"],
    "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
    "stress_opts": ["Estándar", "Lavado (Lixiviación)", "Coextrusión (Calcio)"]
} if lang == "Español" else {
    "title": "🔬 R&D Color Intelligence - Robertet",
    "m_opts": ["Water", "Milk", "Oil", "Meat"],
    "uv_opts": ["Clear (High UV)", "Semi-Opaque", "Opaque/Can (No UV)"],
    "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
    "stress_opts": ["Standard", "Washing (Leaching)", "Coextrusion (Calcium)"]
}

pigments = ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"]
water_soluble = ["Red Beet", "Spirulina", "Norbixin"]
oil_soluble = ["Beta-carotene", "Paprika", "Annato"]

# 4. CONTROLES LATERALES
try: st.sidebar.image("logo.png", width=180)
except: pass

st.sidebar.markdown("### 🎨 Formulación (Pigmentos)")
blend_mode = st.sidebar.checkbox("Activar Mezcla (Blend Mode)")
p1_name = st.sidebar.selectbox("Pigmento Principal", pigments)
p1_ratio = st.sidebar.slider("Ratio Principal (%)", 10, 100, 70) if blend_mode else 100
p2_name = st.sidebar.selectbox("Pigmento Secundario", [p for p in pigments if p != p1_name]) if blend_mode else None

st.sidebar.markdown("--- \n### ⚙️ Parámetros Físico-Químicos")
matrix = st.sidebar.radio("Matriz Base", T["m_opts"], horizontal=True)
app_target = st.sidebar.selectbox("Aplicación", T["apps"])
stress_type = st.sidebar.selectbox("Estrés Específico", T["stress_opts"])
temp = st.sidebar.slider("Temp. Proceso (°C)", 20, 180, 90) 
proc_time = st.sidebar.slider("Tiempo Proceso (min)", 1, 180, 60)
ph_val = st.sidebar.slider("pH", 2.0, 10.0, 6.0)

st.sidebar.markdown("--- \n### 📦 Parámetros de Anaquel")
st_temp = st.sidebar.slider("Temp. Almacén (°C)", 4, 40, 25)
pkg_uv = st.sidebar.selectbox("Empaque", T["uv_opts"])
target_m = st.sidebar.slider("Meses Anaquel", 1, 24, 6)

# 5. MOTORES DE CÁLCULO
def get_props(name, ph):
    colors = {"Beta-carotene":"#FFB300", "Annato":"#FF8C00", "Paprika":"#E63900", "Norbixin":"#D2691E", 
              "Curcumin":"#FFEA00", "Natural Chlorophyll":"#228B22", "Red Beet":"#C71585", "Spirulina":"#4169E1"}
    c = colors.get(name, "#000000")
    if name == "Red Beet" and ph > 7.5: c = "#8B008B"
    elif name == "Curcumin" and ph > 8: c = "#FF4500"
    
    rates = {"Beta-carotene":0.001, "Annato":0.002, "Paprika":0.003, "Norbixin":0.005, 
             "Curcumin":0.01, "Natural Chlorophyll":0.015, "Red Beet":0.04, "Spirulina":0.15}
    return c, rates.get(name, 0.01)

def blend_hex(c1, c2, r1):
    c1_rgb, c2_rgb = np.array(mcolors.to_rgb(c1)), np.array(mcolors.to_rgb(c2))
    blended = (c1_rgb * (r1/100)) + (c2_rgb * (1 - r1/100))
    return mcolors.to_hex(blended)

def calc_kinetics(name, mat, t_c, time_m, ph, stress, s_temp, pkg, months):
    base_color, base_k = get_props(name, ph)
    k_p = base_k * (t_c / 85.0)**2.5 
    
    # Incompatibilidad Absoluta
    is_oil = (mat in ["Oil", "Aceite"])
    if is_oil and name in water_soluble: k_p = 999
    if name == "Norbixin" and ph < 4: k_p = 999
    
    # Castigos por Estrés (Lixiviación / Calcio)
    penalty = 0
    if "Lavado" in stress or "Washing" in stress:
        if name in water_soluble: penalty = 40
        elif name in oil_soluble: penalty = 5
    elif "Calcio" in stress or "Calcium" in stress:
        if name == "Norbixin": penalty = 80
        elif name == "Red Beet": penalty = 25
        elif name == "Natural Chlorophyll": penalty = 15
        else: penalty = 5
        
    init_retention = (100 - penalty) / 100
    
    # Proceso
    t_min = np.linspace(0, time_m, 100)
    stab_proc = (100 * init_retention) * np.exp(-k_p * t_min)
    
    # Anaquel
    t_days = np.linspace(0, months * 30, 100)
    uv_factor = 4.0 if ("Clear" in pkg or "Transparente" in pkg) and name in ["Curcumin", "Natural Chlorophyll", "Spirulina"] else 1.2
    k_s = (base_k * 0.015) * (s_temp / 20.0) * uv_factor
    stab_shelf = stab_proc[-1] * np.exp(-k_s * t_days)
    
    return t_min, stab_proc, t_days, stab_shelf, base_color, penalty

# Variables de Plot
tp_1, sp_1, ts_1, ss_1, col_1, pen_1 = calc_kinetics(p1_name, matrix, temp, proc_time, ph_val, stress_type, st_temp, pkg_uv, target_m)
if blend_mode:
    tp_2, sp_2, ts_2, ss_2, col_2, pen_2 = calc_kinetics(p2_name, matrix, temp, proc_time, ph_val, stress_type, st_temp, pkg_uv, target_m)
    # Mezcla matemática
    sp_mix = (sp_1 * (p1_ratio/100)) + (sp_2 * (1 - p1_ratio/100))
    ss_mix = (ss_1 * (p1_ratio/100)) + (ss_2 * (1 - p1_ratio/100))
    col_mix = blend_hex(col_1, col_2, p1_ratio)

# 6. GRÁFICOS PLOTLY
def make_plot(x, y, color, title, x_lbl):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=color, width=4), fill='tozeroy', 
                             fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.2)"))
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), xaxis_title=x_lbl, yaxis_title="Retención %",
                      yaxis=dict(range=[0, 105]), template="plotly_white")
    return fig

# 7. DASHBOARD VISUAL
st.title(T["title"])
tab_p, tab_s, tab_r = st.tabs(["🔥 Proceso Térmico", "📅 Vida de Anaquel", "💡 Recomendador (BETA)"])

with tab_p:
    c1, c2 = st.columns([1, 2.5])
    with c1:
        if blend_mode:
            st.markdown(f'<div class="color-card" style="background-color:{col_mix};">Mezcla: {p1_name} + {p2_name}</div>', unsafe_allow_html=True)
            st.metric("Retención de la Mezcla", f"{sp_mix[-1]:.1f}%")
        else:
            st.markdown(f'<div class="color-card" style="background-color:{col_1};">{p1_name}</div>', unsafe_allow_html=True)
            st.metric("Retención Final", f"{sp_1[-1]:.1f}%")
        
        st.info(f"**Matriz:** {matrix} | **Estrés:** {stress_type}")
        if pen_1 > 0: st.warning(f"⚠️ Caída inicial por estrés químico/físico detectada.")
    with c2:
        y_data = sp_mix if blend_mode else sp_1
        c_data = col_mix if blend_mode else col_1
        st.plotly_chart(make_plot(tp_1, y_data, c_data, "Proceso", "Minutos"), use_container_width=True)

with tab_s:
    c1, c2 = st.columns([1, 2.5])
    with c1:
        y_shelf = ss_mix if blend_mode else ss_1
        c_data = col_mix if blend_mode else col_1
        st.markdown(f'<div class="color-card" style="background-color:{c_data}; opacity:{max(0.2, y_shelf[-1]/100)};">Anaquel (Mes {target_m})</div>', unsafe_allow_html=True)
        st.metric(f"Retención en Anaquel", f"{y_shelf[-1]:.1f}%")
        st.info(f"**Empaque:** {pkg_uv}")
    with c2:
        st.plotly_chart(make_plot(ts_1, y_shelf, c_data, "Anaquel", "Días"), use_container_width=True)

with tab_r:
    st.subheader("🎯 Recomendador Inteligente (Incluye Cárnicos)")
    st.write("Calculando pigmentos compatibles según pH, Matriz y Estrés seleccionados.")
    
    validos = []
    is_oil = (matrix in ["Oil", "Aceite"])
    
    for cand in pigments:
        ok = True
        if is_oil and cand in water_soluble: ok = False
        if cand == "Norbixin" and ph_val < 4: ok = False
        if temp > 120 and cand in ["Spirulina", "Red Beet"]: ok = False
        if "Calcio" in stress_type and cand == "Norbixin": ok = False
        if ok: validos.append(cand)
        
    if validos:
        st.success(f"**Pigmentos viables para tu proceso:** {', '.join(validos)}")
    else:
        st.error("❌ Ningún pigmento natural sobrevive estas condiciones extremas simultáneas.")

st.caption("Confidential Robertet R&D - Advanced Kinetics & Blending.")
