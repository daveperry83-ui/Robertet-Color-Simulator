import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# Renderizado web estable
matplotlib.use('Agg') 

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Robertet R&D Dashboard", layout="wide")

# ==========================================
# 🔒 SEGURIDAD (PIN: LatAm2026)
# ==========================================
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
# ==========================================

# 2. DICCIONARIOS MULTILINGÜES (Formateados para evitar errores de GitHub)
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])

if lang == "Español":
    T = {
        "title": "🔬 Dashboard de Inteligencia de Color R&D",
        "t1": "🔥 Proceso Térmico", "t2": "📅 Vida de Anaquel",
        "p1": "Muestra A (Principal)", "p2": "Muestra B (Comparativa)",
        "pigment": "Pigmento", "matrix": "Matriz Base", "app": "Aplicación Final",
        "temp": "Temp. Proceso (°C)", "ph": "Nivel de pH", "alc": "Alcohol (%)",
        "storage": "Temp. Almacén (°C)", "pkg": "Empaque (Filtro UV)", "months": "Objetivo (Meses)",
        "compare": "Activar Comparación", "ret": "Retención",
        "uv_opts": ["Transparente (UV Alto)", "Semi-Opaco", "Opaco/Lata (Sin UV)"],
        "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "Nota Técnica R&D:"
    }
else:
    T = {
        "title": "🔬 R&D Color Intelligence Dashboard",
        "t1": "🔥 Thermal Processing", "t2": "📅 Shelf Life",
        "p1": "Sample A (Primary)", "p2": "Sample B (Comparative)",
        "pigment": "Pigment", "matrix": "Base Matrix", "app": "Target Application",
        "temp": "Process Temp (°C)", "ph": "pH Level", "alc": "Alcohol (%)",
        "storage": "Storage Temp (°C)", "pkg": "Packaging (UV Filter)", "months": "Target (Months)",
        "compare": "Enable Comparison", "ret": "Retention",
        "uv_opts": ["Clear (High UV)", "Semi-Opaque", "Opaque/Can (No UV)"],
        "apps": ["Beverages", "Dairy", "Bakery", "Meat", "Sauces", "Confectionery"],
        "note": "R&D Technical Note:"
    }

pigments_list = [
    "Beta-carotene", "Annato", "Paprika", "Norbixin", 
    "Curcumin", "Natural Chlorophyll", "Red Beet", "Spirulina"
]

# 3. BARRA LATERAL (CONTROLES)
st.sidebar.image("https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png", width=180)
st.sidebar.markdown(f"### 1. {T['p1']}")
p1_name = st.sidebar.selectbox(f"{T['pigment']} (A)", pigments_list, key="p1")
p1_matrix = st.sidebar.radio(f"{T['matrix']} (A)", ["Water", "Milk", "Oil"], horizontal=True, key="m1")

compare_mode = st.sidebar.checkbox(T["compare"])
p2_name = None
p2_matrix = None

if compare_mode:
    st.sidebar.markdown(f"--- \n### 2. {T['p2']}")
    p2_name = st.sidebar.selectbox(f"{T['pigment']} (B)", pigments_list, key="p2")
    p2_matrix = st.sidebar.radio(f"{T['matrix']} (B)", ["Water", "Milk", "Oil"], horizontal=True, key="m2")

st.sidebar.markdown("--- \n### ⚙️ Settings")
app_target = st.sidebar.selectbox(T["app"], T["apps"])
temp = st.sidebar.slider(T["temp"], 20, 130, 90)
ph_val = st.sidebar.slider(T["ph"], 2.0, 10.0, 7.0)
st_temp = st.sidebar.slider(T["storage"], 4, 40, 25)
pkg = st.sidebar.selectbox(T["pkg"], T["uv_opts"])
months = st.sidebar.slider(T["months"], 1, 24, 6)

# 4. LÓGICA MATEMÁTICA Y COLORES
def get_color(name, ph):
    colors = {
        "Beta-carotene": "#FFB300", 
        "Annato": "#FF8C00", 
        "Paprika": "#E63900", 
        "Norbixin": "#D2691E", 
        "Curcumin": "#FFEA00", 
        "Natural Chlorophyll": "#228B22", 
        "Red Beet": "#C71585", 
        "Spirulina": "#4169E1"
    }
    c = colors.get(name, "#000000")
    if name == "Red Beet" and ph > 7: 
        c = "#8B008B"
    elif name == "Curcumin" and ph > 8: 
        c = "#FF4500"
    return c

def calculate_kinetics(name, matrix, temp, ph, storage, pkg_type, months_target):
    rates = {
        "Beta-carotene": 0.001, "Annato": 0.002, "Paprika": 0.003,
        "Norbixin": 0.005, "Curcumin": 0.01, "Natural Chlorophyll": 0.015,
        "Red Beet": 0.04, "Spirulina": 0.15
    }
    base_rate = rates.get(name, 0.01)
    
    # Proceso
    t_proc = np.linspace(0, 60, 100)
    k_p = base_rate * (temp / 85.0)**2
    s_proc = 100 * np.exp(-k_p * t_proc)
    
    # Incompatibilidades (Reglas Estrictas)
    if matrix == "Oil" and name in ["Norbixin", "Red Beet", "Spirulina"]:
        s_proc = np.zeros_like(t_proc)
    elif ph < 4 and name == "Norbixin":
        s_proc = np.zeros_like(t_proc)
    
    # Anaquel
    t_shelf = np.linspace(0, months_target * 30, 100)
    uv_factor = 1.2
    if pkg_type == T["uv_opts"][0] and name in ["Curcumin", "Natural Chlorophyll", "Spirulina"]:
        uv_factor = 4.0
    
    k_s = (base_rate * 0.015) * (storage / 20.0) * uv_factor
    s_shelf = s_proc[-1] * np.exp(-k_s * t_shelf)
    
    return t_proc, s_proc, t_shelf, s_shelf

# Ejecutar Cálculos
tp1, sp1, ts1, ss1 = calculate_kinetics(p1_name, p1_matrix, temp, ph_val, st_temp, pkg, months)
col1 = get_color(p1_name, ph_val)

if compare_mode:
    tp2, sp2, ts2, ss2 = calculate_kinetics(p2_name, p2_matrix, temp, ph_val, st_temp, pkg, months)
    col2 = get_color(p2_name, ph_val)

# 5. RENDERIZADO VISUAL
st.title(T["title"])
tab1, tab2 = st.tabs([T["t1"], T["t2"]])

def draw_visual_box(name, stab, color, label):
    opacity = max(0.1, stab / 100.0)
    st.markdown(f"""
        <div style="background-color:{color}; opacity:{opacity}; height:80px; 
        border-radius:10px; display:flex; align-items:center; justify-content:center; 
        color:white; font-weight:bold; border:1px solid #ddd; margin-bottom:10px;">
        {label}: {name}
        </div>
    """, unsafe_allow_html=True)
    st.metric(f"{T['ret']} ({label})", f"{stab:.1f}%")

with tab1:
    c_info, c_plot = st.columns([1, 2.5])
    with c_info:
        draw_visual_box(p1_name, sp1[-1], col1, "A")
        if compare_mode: 
            draw_visual_box(p2_name, sp2[-1], col2, "B")
        
        st.info(f"**{T['note']}** Para {app_target}, asegurar que {p1_name} tenga la emulsión o dispersión correcta según la matriz ({p1_matrix}).")
        
    with c_plot:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(tp1, sp1, color=col1, linewidth=4, label=f"A: {p1_name}")
        if compare_mode: 
            ax.plot(tp2, sp2, color=col2, linewidth=3, linestyle="--", label=f"B: {p2_name}")
        
        ax.set_ylim(-5, 105)
        ax.set_ylabel("%")
        ax.set_xlabel("Min.")
        ax.legend()
        ax.grid(alpha=0.2)
        st.pyplot(fig)

with tab2:
    c_info2, c_plot2 = st.columns([1, 2.5])
    with c_info2:
        draw_visual_box(p1_name, ss1[-1], col1, "A")
        if compare_mode: 
            draw_visual_box(p2_name, ss2[-1], col2, "B")
            
    with c_plot2:
        fig2, ax2 = plt.subplots(figsize=(10, 4.5))
        ax2.plot(ts1, ss1, color=col1, linewidth=4, label=f"A: {p1_name}")
        if compare_mode: 
            ax2.plot(ts2, ss2, color=col2, linewidth=3, linestyle="--", label=f"B: {p2_name}")
        
        ax2.set_ylim(-5, 105)
        ax2.set_ylabel("%")
        ax2.set_xlabel("Dias / Days")
        ax2.legend()
        ax2.grid(alpha=0.2)
        st.pyplot(fig2)

st.markdown("---")
st.caption("Confidential Robertet R&D - Regional Division. Multi-language Support Enabled.")
