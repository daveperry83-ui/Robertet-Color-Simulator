import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.colors as mcolors

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Robertet R&D Color Intelligence", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .color-card { height: 90px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); margin-bottom: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
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

# 3. CONSTANTES QUÍMICAS
pigments = ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"]
water_soluble = ["Red Beet", "Spirulina", "Norbixin"]
oil_soluble = ["Beta-carotene", "Paprika", "Annato"]

try: st.sidebar.image("logo.png", width=180)
except: pass

# 4. CONTROLES: MEZCLAS MÚLTIPLES
st.sidebar.markdown("### 🎨 Formulación (Multimezcla)")
selected_pigments = st.sidebar.multiselect("Selecciona Pigmentos (Máx 5 recomendados)", pigments, default=["Beta-carotene"])

if not selected_pigments:
    st.error("Debes seleccionar al menos un pigmento.")
    st.stop()

raw_ratios = []
if len(selected_pigments) > 1:
    st.sidebar.markdown("**Ajuste de Proporciones:**")
    for p in selected_pigments:
        raw_ratios.append(st.sidebar.slider(f"{p}", 1, 100, 100//len(selected_pigments)))
else:
    raw_ratios = [100]

# Normalización a 100%
total_ratio = sum(raw_ratios)
ratios = [r / total_ratio for r in raw_ratios]

# 5. CONTROLES: MATRIZ Y PROCESO
st.sidebar.markdown("--- \n### ⚙️ Parámetros Físico-Químicos")
matrix = st.sidebar.radio("Matriz Base", ["Agua", "Leche", "Aceite", "Carne"], horizontal=True)
app_target = st.sidebar.selectbox("Aplicación", ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"])

temp = st.sidebar.slider("Temp. Proceso (°C)", 20, 180, 90) 
proc_time = st.sidebar.slider("Tiempo Proceso (min)", 1, 180, 60)
ph_val = st.sidebar.slider("pH", 2.0, 10.0, 6.0)

# 6. CONTROLES: ESTRÉS Y PROTECCIÓN
st.sidebar.markdown("--- \n### 🛡️ Factores de Estrés y Protección")
auto_stress = st.sidebar.checkbox("🤖 Autodetectar Estrés según Aplicación", value=True)

if auto_stress:
    # Lógica de autocalculado R&D
    wash_on = True if app_target in ["Meat", "Vegetables"] else False
    ca_on = True if app_target in ["Dairy", "Meat"] else False
    st.sidebar.info(f"Auto-aplicando: Lavado={wash_on} | Calcio={ca_on}")
else:
    wash_on = st.sidebar.checkbox("Lavado Intensivo (Lixiviación)", value=False)
    ca_on = st.sidebar.checkbox("Coextrusión con Calcio", value=False)

romero_on = st.sidebar.checkbox("🌿 Añadir Extracto de Romero (Antioxidante)")

st.sidebar.markdown("--- \n### 📦 Anaquel")
st_temp = st.sidebar.slider("Temp. Almacén (°C)", 4, 40, 25)
pkg_uv = st.sidebar.selectbox("Empaque", ["Transparente (UV Alto)", "Semi-Opaco", "Opaco/Lata (Sin UV)"])
target_m = st.sidebar.slider("Meses Anaquel", 1, 24, 6)

# 7. MOTORES DE CÁLCULO FÍSICO-QUÍMICO
def get_props(name, ph):
    colors = {"Beta-carotene":"#FFB300", "Annato":"#FF8C00", "Paprika":"#E63900", "Norbixin":"#D2691E", 
              "Curcumin":"#FFEA00", "Natural Chlorophyll":"#228B22", "Red Beet":"#C71585", "Spirulina":"#4169E1"}
    c = colors.get(name, "#000000")
    if name == "Red Beet" and ph > 7.5: c = "#8B008B"
    elif name == "Curcumin" and ph > 8: c = "#FF4500"
    rates = {"Beta-carotene":0.001, "Annato":0.002, "Paprika":0.003, "Norbixin":0.005, 
             "Curcumin":0.01, "Natural Chlorophyll":0.015, "Red Beet":0.04, "Spirulina":0.15}
    return c, rates.get(name, 0.01)

def blend_hex_multi(color_list, ratio_list):
    base = np.array([0.0, 0.0, 0.0])
    for c, r in zip(color_list, ratio_list):
        base += np.array(mcolors.to_rgb(c)) * r
    return mcolors.to_hex(base)

def calc_kinetics(name, mat, t_c, time_m, ph, wash_active, ca_active, romero_active, s_temp, pkg, months):
    base_color, base_k = get_props(name, ph)
    
    # Efecto Romero: Protege dobles enlaces en carotenoides y curcumina
    if romero_active and name in ["Beta-carotene", "Annato", "Paprika", "Curcumin", "Norbixin"]:
        base_k *= 0.5 
        
    k_p = base_k * (t_c / 85.0)**2.5 
    
    is_oil = (mat in ["Oil", "Aceite"])
    if is_oil and name in water_soluble: k_p = 999
    if name == "Norbixin" and ph < 4: k_p = 999
    
    # Penalizaciones Acumulativas
    penalty = 0
    if wash_active:
        if name in water_soluble: penalty += 40
        elif name in oil_soluble: penalty += 5
    if ca_active:
        if name == "Norbixin": penalty += 80
        elif name == "Red Beet": penalty += 25
        elif name == "Natural Chlorophyll": penalty += 15
        else: penalty += 5
        
    penalty = min(penalty, 99)
    init_retention = (100 - penalty) / 100
    
    t_min = np.linspace(0, time_m, 100)
    stab_proc = (100 * init_retention) * np.exp(-k_p * t_min)
    
    t_days = np.linspace(0, months * 30, 100)
    uv_factor = 4.0 if "Transparente" in pkg and name in ["Curcumin", "Natural Chlorophyll", "Spirulina"] else 1.2
    k_s = (base_k * 0.015) * (s_temp / 20.0) * uv_factor
    stab_shelf = stab_proc[-1] * np.exp(-k_s * t_days)
    
    return t_min, stab_proc, t_days, stab_shelf, base_color

# Calcular mezcla
t_proc_master = np.linspace(0, proc_time, 100)
t_shelf_master = np.linspace(0, target_m * 30, 100)
sp_mix = np.zeros(100)
ss_mix = np.zeros(100)
colors_to_blend = []

for p_name, p_ratio in zip(selected_pigments, ratios):
    tp, sp, ts, ss, p_color = calc_kinetics(p_name, matrix, temp, proc_time, ph_val, wash_on, ca_on, romero_on, st_temp, pkg_uv, target_m)
    sp_mix += sp * p_ratio
    ss_mix += ss * p_ratio
    colors_to_blend.append(p_color)

final_color = blend_hex_multi(colors_to_blend, ratios)

# 8. GRÁFICOS PLOTLY PREMIUM (Restaurados)
def make_plot(x, y, color, title, x_lbl):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='lines', 
        line=dict(color=color, width=4), 
        fill='tozeroy', 
        fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.2)",
        hovertemplate=f"{x_lbl}: %{{x:.1f}}<br>Retención: %{{y:.1f}}%<extra></extra>"
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title=x_lbl, yaxis_title="Retención %",
        yaxis=dict(range=[0, 105]), template="plotly_white",
        hovermode="x unified"
    )
    return fig

# 9. DASHBOARD VISUAL
st.title(T["title"])
tab_p, tab_s = st.tabs(["🔥 Dinámica de Proceso", "📅 Proyección de Anaquel"])

with tab_p:
    col_info, col_graph = st.columns([1, 2.5])
    with col_info:
        label = "Mezcla" if len(selected_pigments) > 1 else selected_pigments[0]
        st.markdown(f'<div class="color-card" style="background-color:{final_color};">{label}</div>', unsafe_allow_html=True)
        st.metric("Retención de Formulación", f"{sp_mix[-1]:.1f}%")
        
        info_str = f"**Matriz:** {matrix}<br>**Temp:** {temp}°C | **pH:** {ph_val}"
        st.info(info_str, icon="🧪")
        if wash_on or ca_on: 
            st.warning(f"⚠️ Estrés Físico activo. Penalización de lixiviación/iónica calculada.")
        if romero_on:
            st.success("🌿 Protección Antioxidante (Romero) activada en la cinética térmica.")
            
    with col_graph:
        st.plotly_chart(make_plot(t_proc_master, sp_mix, final_color, "Proceso", "Minutos"), use_container_width=True)

with tab_s:
    col_info_s, col_graph_s = st.columns([1, 2.5])
    with col_info_s:
        st.markdown(f'<div class="color-card" style="background-color:{final_color}; opacity:{max(0.2, ss_mix[-1]/100)};">Mes {target_m}</div>', unsafe_allow_html=True)
        st.metric(f"Retención en Anaquel", f"{ss_mix[-1]:.1f}%")
        st.info(f"**Empaque:** {pkg_uv}")
    with col_graph_s:
        st.plotly_chart(make_plot(t_shelf_master, ss_mix, final_color, "Anaquel", "Días"), use_container_width=True)

st.caption("Confidential Robertet R&D - Advanced Kinetics & Blending.")
