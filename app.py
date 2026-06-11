import streamlit as st
import numpy as np
import plotly.graph_objects as go
import colorsys
import matplotlib.colors as mcolors

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(page_title="Robertet R&D Dashboard", page_icon="🌿",
                   layout="wide", initial_sidebar_state="expanded")

ROBERTET_GREEN = "#1B5E3A"
ROBERTET_DARK = "#0E3B25"
THRESHOLD = 70  # Umbral aceptable de retención (%)

# --- Helper: hex -> rgba ---
def hex_to_rgba(hex_color, alpha=0.15):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ==========================================
# 2. DISEÑO CSS GLOBAL
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {ROBERTET_DARK} 0%, {ROBERTET_GREEN} 100%);
}}

/* Solo etiquetas y textos sueltos en blanco (no los widgets) */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] .stMarkdown {{
    color: #F0F4F1 !important;
}}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.25); }}

/* Cajas de selectbox: fondo oscuro translúcido + texto blanco */
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background-color: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.35) !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] * {{
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    fill: #FFFFFF !important;
}}

/* Radio buttons y checkbox: texto blanco */
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stCheckbox label {{
    color: #F0F4F1 !important;
}}

/* Sliders: valores y barra legibles */
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {{
    color: #FFFFFF !important;
}}

/* MENUS DESPLEGABLES ABIERTOS (se dibujan fuera del sidebar, fondo blanco):
   forzar texto oscuro para que sean legibles */
[data-baseweb="popover"] [role="listbox"] li,
[data-baseweb="popover"] [role="option"] {{
    color: #1A1A1A !important;
    background-color: #FFFFFF !important;
}}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"] {{
    background-color: #EEF2EF !important;
    color: #0E3B25 !important;
}}

/* ---------- Tabs tipo pill ---------- */
.stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
.stTabs [data-baseweb="tab"] {{
    background: #EEF2EF; border-radius: 50px; padding: 8px 22px;
    font-weight: 600; border: none;
}}
.stTabs [aria-selected="true"] {{
    background: {ROBERTET_GREEN} !important; color: white !important;
}}

/* ---------- Métricas como tarjetas ---------- */
[data-testid="stMetric"] {{
    background: white; border-radius: 12px; padding: 16px 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border-left: 4px solid {ROBERTET_GREEN};
}}

/* ---------- Color cards ---------- */
.color-card {{
    height: 100px; border-radius: 14px; display: flex; align-items: center;
    justify-content: center; color: white; font-weight: 700; font-size: 1.15rem;
    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    border: 1px solid rgba(0,0,0,0.05);
    margin-bottom: 16px; text-shadow: 1px 1px 3px rgba(0,0,0,0.55);
    transition: transform .2s ease, box-shadow .2s ease;
}}
.color-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 22px rgba(0,0,0,0.20);
}}

/* ---------- Chips de candidatos descartados ---------- */
.chip {{
    display: inline-block; background: #F1F1EE; color: #777;
    border-radius: 50px; padding: 5px 14px; margin: 4px 6px 4px 0;
    font-size: 0.85rem; border: 1px solid #E2E2DD;
}}
.chip-ok {{
    background: {ROBERTET_GREEN}; color: white; border: none; font-weight: 600;
}}

/* ---------- Tarjeta de login ---------- */
.login-card {{
    background: white; border-radius: 18px; padding: 40px 36px 28px 36px;
    box-shadow: 0 16px 48px rgba(14,59,37,0.18);
    text-align: center; margin-top: 8vh;
}}

/* ---------- Títulos ---------- */
h1 {{ font-weight: 800 !important; letter-spacing: -0.5px; }}
h3 {{ font-weight: 700 !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 🔒 SEGURIDAD (PIN: LatAm2026)
# ==========================================
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    # Fondo degradado solo para la pantalla de login
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, {ROBERTET_DARK} 0%, {ROBERTET_GREEN} 60%, #2E7D50 100%);
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=260)
        st.markdown("### 🔒 R&D Portal — Latin America")
        st.caption("Acceso restringido / Restricted access")
        clave = st.text_input("PIN de Acceso / Access PIN:", type="password")
        if st.button("Unlock Simulator", use_container_width=True, type="primary"):
            if clave == "LatAm2026":
                st.session_state.acceso_concedido = True
                st.rerun()
            else:
                st.error("❌ Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 4. DICCIONARIOS MULTILINGÜES
# ==========================================
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])

if lang == "Español":
    T = {
        "title": "🔬 Inteligencia de Color R&D — Robertet",
        "t1": "🔥 Proceso Térmico", "t2": "📅 Vida de Anaquel", "t3": "💡 Recomendador (BETA)",
        "p1": "Muestra A", "p2": "Muestra B (Comparativa)",
        "pigment": "Pigmento", "matrix": "Matriz Base", "m_opts": ["Agua", "Leche", "Aceite"],
        "temp": "Temp. Proceso (°C)", "ph": "pH", "months": "Meses Anaquel",
        "storage": "Temp. Almacén (°C)",
        "compare": "Modo Comparativo", "ret": "Retención Final",
        "uv": "Empaque (Filtro UV)", "uv_opts": ["Transparente (UV Alto)", "Semi-Opaco", "Opaco/Lata (Sin UV)"],
        "app": "Aplicación Final", "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "Nota Técnica R&D:", "beta_msg": "🧪 VERSIÓN BETA: Algoritmo predictivo en fase de calibración.",
        "time_m": "Tiempo (Minutos)", "time_d": "Tiempo (Días)", "stab_pct": "Estabilidad (%)",
        "threshold": "Umbral aceptable", "vs_thr": "vs umbral",
        "discarded": "Candidatos evaluados:", "no_match": "❌ No hay pigmento natural viable para estas condiciones.",
        "r_oil": "inestable en aceite", "r_ph": "requiere pH ≥ 4", "r_temp": "no resiste >130°C",
    }
else:
    T = {
        "title": "🔬 R&D Color Intelligence — Robertet",
        "t1": "🔥 Thermal Process", "t2": "📅 Shelf Life", "t3": "💡 Smart Recommender (BETA)",
        "p1": "Sample A", "p2": "Sample B (Comparative)",
        "pigment": "Pigment", "matrix": "Base Matrix", "m_opts": ["Water", "Milk", "Oil"],
        "temp": "Process Temp (°C)", "ph": "pH Level", "months": "Shelf Life Months",
        "storage": "Storage Temp (°C)",
        "compare": "Comparison Mode", "ret": "Final Retention",
        "uv": "Packaging (UV Filter)", "uv_opts": ["Clear (High UV)", "Semi-Opaque", "Opaque/Can (No UV)"],
        "app": "Target Application", "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "R&D Technical Insight:", "beta_msg": "🧪 BETA VERSION: Predictive algorithm under lab calibration.",
        "time_m": "Time (Minutes)", "time_d": "Time (Days)", "stab_pct": "Stability (%)",
        "threshold": "Acceptable threshold", "vs_thr": "vs threshold",
        "discarded": "Evaluated candidates:", "no_match": "❌ No viable natural pigment for these conditions.",
        "r_oil": "unstable in oil", "r_ph": "requires pH ≥ 4", "r_temp": "won't survive >130°C",
    }

pigments = ["Beta-carotene", "Annato", "Paprika", "Norbixin", "Curcumin",
            "Natural Chlorophyll", "Red Beet", "Spirulina"]

# ==========================================
# 5. CONTROLES LATERALES
# ==========================================
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=170)
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
app_target = st.sidebar.selectbox(T["app"], T["apps"])
temp = st.sidebar.slider(T["temp"], 20, 180, 90)
ph_val = st.sidebar.slider(T["ph"], 2.0, 10.0, 7.0)

st.sidebar.markdown("--- \n### 📦 Shelf Life Parameters")
st_temp = st.sidebar.slider(T["storage"], 4, 40, 25)
pkg_uv = st.sidebar.selectbox(T["uv"], T["uv_opts"])
target_m = st.sidebar.slider(T["months"], 1, 24, 6)

# ==========================================
# 6. LÓGICA QUÍMICA (sin cambios funcionales)
# ==========================================
def get_props(name, ph):
    colors = {"Beta-carotene": "#FFB300", "Annato": "#FF8C00", "Paprika": "#E63900",
              "Norbixin": "#D2691E", "Curcumin": "#FFEA00", "Natural Chlorophyll": "#228B22",
              "Red Beet": "#C71585", "Spirulina": "#4169E1"}
    c = colors.get(name, "#000000")
    if name == "Red Beet" and ph > 7: c = "#8B008B"
    elif name == "Curcumin" and ph > 8: c = "#FF4500"

    rates = {"Beta-carotene": 0.001, "Annato": 0.002, "Paprika": 0.003, "Norbixin": 0.005,
             "Curcumin": 0.01, "Natural Chlorophyll": 0.015, "Red Beet": 0.04, "Spirulina": 0.15}
    return c, rates.get(name, 0.01)

def run_sim(name, matrix, t_c, ph, storage_t, pkg, months):
    color, base_k = get_props(name, ph)
    t_min = np.linspace(0, 60, 100)
    k_p = base_k * (t_c / 85.0) ** 2.5

    is_oil = (matrix in ["Oil", "Aceite"])
    if is_oil and name in ["Norbixin", "Red Beet", "Spirulina"]: k_p = 999
    elif ph < 4 and name == "Norbixin": k_p = 999

    stab_proc = 100 * np.exp(-k_p * t_min)

    t_days = np.linspace(0, months * 30, 100)
    uv_factor = 1.2
    if pkg == T["uv_opts"][0] and name in ["Curcumin", "Natural Chlorophyll", "Spirulina"]:
        uv_factor = 4.0

    k_s = (base_k * 0.015) * (storage_t / 20.0) * uv_factor
    stab_shelf = stab_proc[-1] * np.exp(-k_s * t_days)

    return t_min, stab_proc, t_days, stab_shelf, color

tp1, sp1, ts1, ss1, col1 = run_sim(p1_name, p1_matrix, temp, ph_val, st_temp, pkg_uv, target_m)
if compare_on:
    tp2, sp2, ts2, ss2, col2 = run_sim(p2_name, p2_matrix, temp, ph_val, st_temp, pkg_uv, target_m)

# ==========================================
# 7. GRÁFICAS PLOTLY MEJORADAS
# ==========================================
def create_plotly_chart(x1, y1, c1, n1, x_title, y_title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x1, y=y1, mode="lines",
        line=dict(color=c1, width=4),
        name=f"A: {n1}",
        fill="tozeroy", fillcolor=hex_to_rgba(c1, 0.15),
    ))
    # Traza B agregada de forma limpia desde fuera con fig.add_trace si aplica

    # Umbral de referencia
    fig.add_hline(y=THRESHOLD, line_dash="dot", line_color="gray",
                  annotation_text=T["threshold"], annotation_position="top right",
                  annotation_font_color="gray")

    # Anotación del punto final (lectura inmediata)
    fig.add_annotation(x=x1[-1], y=y1[-1], text=f"<b>{y1[-1]:.1f}%</b>",
                       showarrow=True, arrowhead=2, arrowcolor=c1,
                       font=dict(color=c1, size=13), ax=-40, ay=-25)

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(title=x_title, showgrid=True, gridcolor="rgba(0,0,0,0.06)", zeroline=False),
        yaxis=dict(title=y_title, showgrid=True, gridcolor="rgba(0,0,0,0.06)", zeroline=False, range=[-5, 105]),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig

def add_trace_b(fig, x2, y2, c2, n2):
    fig.add_trace(go.Scatter(
        x=x2, y=y2, mode="lines",
        line=dict(color=c2, width=3, dash="dash"),
        name=f"B: {n2}",
    ))
    fig.add_annotation(x=x2[-1], y=y2[-1], text=f"<b>{y2[-1]:.1f}%</b>",
                       showarrow=True, arrowhead=2, arrowcolor=c2,
                       font=dict(color=c2, size=13), ax=40, ay=-25)
    return fig

# ==========================================
# 8. DASHBOARD VISUAL
# ==========================================
st.title(T["title"])
tab_p, tab_s, tab_r = st.tabs([T["t1"], T["t2"], T["t3"]])

def display_res(name, stab, color, label):
    # Mezcla hacia blanco según pérdida de color (texto siempre legible)
    fade = max(0.25, stab / 100)
    faded = hex_to_rgba(color, fade)
    st.markdown(
        f'<div class="color-card" style="background: linear-gradient(135deg, {color} 0%, {faded} 100%);">'
        f'{label}: {name}</div>',
        unsafe_allow_html=True,
    )
    delta = stab - THRESHOLD
    st.metric(f"{T['ret']} ({label})", f"{stab:.1f}%", delta=f"{delta:+.1f}% {T['vs_thr']}")

with tab_p:
    c1, c2 = st.columns([1, 2.5])
    with c1:
        display_res(p1_name, sp1[-1], col1, "A")
        if compare_on:
            display_res(p2_name, sp2[-1], col2, "B")
        st.info(f"**{T['note']}** @{temp}°C / App: {app_target}")
    with c2:
        fig_p = create_plotly_chart(tp1, sp1, col1, p1_name, T["time_m"], T["stab_pct"])
        if compare_on:
            fig_p = add_trace_b(fig_p, tp2, sp2, col2, p2_name)
        st.plotly_chart(fig_p, use_container_width=True)

with tab_s:
    c1_s, c2_s = st.columns([1, 2.5])
    with c1_s:
        display_res(p1_name, ss1[-1], col1, "A")
        if compare_on:
            display_res(p2_name, ss2[-1], col2, "B")
        st.info(f"**Storage:** {pkg_uv} @{st_temp}°C")
    with c2_s:
        fig_s = create_plotly_chart(ts1, ss1, col1, p1_name, T["time_d"], T["stab_pct"])
        if compare_on:
            fig_s = add_trace_b(fig_s, ts2, ss2, col2, p2_name)
        st.plotly_chart(fig_s, use_container_width=True)

with tab_r:
    st.warning(T["beta_msg"])
    st.subheader("🎯 Tono Objetivo / Target Hue")

    col_p, col_r = st.columns([1, 2])
    with col_p:
        target_color = st.color_picker("Color Picker", "#FF8C00")
        st.markdown(
            f'<div style="background:{target_color}; height:110px; border-radius:14px; '
            f'border:1px solid #ddd; box-shadow:0 6px 16px rgba(0,0,0,0.12);"></div>',
            unsafe_allow_html=True,
        )

    with col_r:
        rgb = mcolors.to_rgb(target_color)
        hsv = colorsys.rgb_to_hsv(*rgb)
        hue = hsv[0] * 360

        if hue >= 330 or hue <= 20: cands = ["Red Beet", "Paprika"]
        elif 20 < hue <= 45: cands = ["Paprika", "Annato", "Beta-carotene"]
        elif 45 < hue <= 75: cands = ["Curcumin", "Beta-carotene"]
        elif 75 < hue <= 160: cands = ["Natural Chlorophyll"]
        elif 160 < hue <= 260: cands = ["Spirulina"]
        else: cands = ["Red Beet"]

        rec = None
        evaluated = []  # (nombre, ok, razón)
        is_oil = (p1_matrix in ["Oil", "Aceite"])
        for cand in cands:
            ok, reason = True, ""
            if is_oil and cand in ["Norbixin", "Red Beet", "Spirulina"]:
                ok, reason = False, T["r_oil"]
            elif cand == "Norbixin" and ph_val < 4:
                ok, reason = False, T["r_ph"]
            elif temp > 130 and cand in ["Spirulina", "Red Beet"]:
                ok, reason = False, T["r_temp"]
            evaluated.append((cand, ok, reason))
            if ok and rec is None:
                rec = cand

        st.markdown("<br>", unsafe_allow_html=True)
        if rec:
            st.success(f"### 🏆 MATCH: {rec}")
            st.write(f"Sugerido para **{app_target}** en matriz de **{p1_matrix}**.")
        else:
            st.error(T["no_match"])

        # Chips: transparencia del algoritmo
        chips = f"**{T['discarded']}**<br>"
        for cand, ok, reason in evaluated:
            if ok and cand == rec:
                chips += f'<span class="chip chip-ok">✅ {cand}</span>'
            elif ok:
                chips += f'<span class="chip">{cand}</span>'
            else:
                chips += f'<span class="chip">❌ {cand} — {reason}</span>'
        st.markdown(chips, unsafe_allow_html=True)

st.caption("Confidential Robertet R&D — Regional Division.")
