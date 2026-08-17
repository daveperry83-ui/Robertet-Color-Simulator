import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.colors as mcolors

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Robertet Advanced Blending", layout="wide")

st.markdown("""<style>.color-card { height: 70px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; margin-bottom: 10px; }</style>""", unsafe_allow_html=True)

# 2. SEGURIDAD
if "acceso_concedido" not in st.session_state: st.session_state.acceso_concedido = False
if not st.session_state.acceso_concedido:
    st.markdown("### 🔒 R&D Portal - Latin America")
    clave = st.text_input("PIN de Acceso:", type="password")
    if st.button("Unlock") and clave == "LatAm2026":
        st.session_state.acceso_concedido = True
        st.rerun()
    st.stop()

# 3. CONTROLES
pigments = ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"]
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=150)

# MODO MEZCLA
blend_mode = st.sidebar.checkbox("Activar Modo Mezcla (Blend Mode)")
p1_name = st.sidebar.selectbox("Pigmento Principal", pigments)
p1_ratio = st.sidebar.slider("Ratio Pigmento Principal (%)", 50, 100, 100) if blend_mode else 100

p2_name = None
if blend_mode:
    p2_name = st.sidebar.selectbox("Pigmento Secundario", [p for p in pigments if p != p1_name])

st.sidebar.markdown("---")
matrix = st.sidebar.radio("Matriz", ["Agua", "Leche", "Aceite"])
temp = st.sidebar.slider("Temp (°C)", 20, 180, 90)
proc_time = st.sidebar.slider("Tiempo Proceso (min)", 10, 180, 60)
baking_loss = st.sidebar.slider("Factor Pérdida Lavado/Cocción (%)", 0, 50, 0) # <--- NUEVO
ph = st.sidebar.slider("pH", 2.0, 10.0, 7.0)

# 4. LÓGICA DE CÁLCULO
def get_rate(name, ph):
    rates = {"Beta-carotene":0.001, "Annato":0.002, "Paprika":0.003, "Norbixin":0.005, 
             "Curcumin":0.01, "Natural Chlorophyll":0.015, "Red Beet":0.04, "Spirulina":0.15}
    return rates.get(name, 0.01)

def calc_stability(name, matrix, t_c, time, ph, loss):
    rate = get_rate(name, ph)
    # Cinética corregida por factor de lavado/cocción
    loss_factor = (100 - loss) / 100
    k = rate * (t_c / 85.0)**2.5
    
    # Incompatibilidades
    if (matrix == "Aceite" and name in ["Norbixin", "Red Beet", "Spirulina"]): k = 999
    
    t = np.linspace(0, time, 100)
    stab = 100 * np.exp(-k * (t/60)) * loss_factor
    return stab

# Ejecución
if not blend_mode:
    stab_curve = calc_stability(p1_name, matrix, temp, proc_time, ph, baking_loss)
    final_stab = stab_curve[-1]
else:
    s1 = calc_stability(p1_name, matrix, temp, proc_time, ph, baking_loss)
    s2 = calc_stability(p2_name, matrix, temp, proc_time, ph, baking_loss)
    stab_curve = (s1 * (p1_ratio/100)) + (s2 * (1 - p1_ratio/100))
    final_stab = stab_curve[-1]

# 5. VISUALIZACIÓN
col_info, col_graph = st.columns([1, 2])
with col_info:
    st.metric("Retención Final", f"{final_stab:.1f}%")
    st.info(f"Proceso: {temp}°C por {proc_time} min.")
    st.write(f"Factor de lavado aplicado: {baking_loss}%")

with col_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=stab_curve, mode='lines', line=dict(width=4), fill='tozeroy'))
    fig.update_layout(title="Curva de Retención de Color", yaxis=dict(range=[0, 105]), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.caption("Robertet R&D Engine - Blending Mode Active")
