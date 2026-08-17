"""
Robertet R&D — Color Intelligence Simulator
v3 — modelo de dos KPIs: retención química vs. color entregado.

Cambio conceptual respecto a v2:
    v2 respondía "¿el pigmento sobrevive el calor?"
    v3 responde "¿cuánto color queda EN EL PRODUCTO al final de la línea?"

Son preguntas distintas. Un pigmento puede tener 96% de retención química
y entregar 8% de color, porque el 92% se fue por el drenaje en el enfriado.
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import colorsys

st.set_page_config(page_title="Robertet R&D Color Intelligence", layout="wide")

LOGO = "https://www.robertet.com/wp-content/uploads/2021/03/Logo-Robertet-1.png"

# ==========================================================================
# ACCESO
# ==========================================================================
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.image(LOGO, width=300)
        st.markdown("### 🔒 R&D Portal — Latin America")
        clave = st.text_input("PIN de Acceso / Access PIN:", type="password")
        if st.button("Unlock Simulator"):
            if clave == "LatAm2026":
                st.session_state.acceso_concedido = True
                st.rerun()
            else:
                st.error("❌ Access Denied")
    st.stop()

# ==========================================================================
# TRADUCCIONES
# ==========================================================================
lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])
ES = lang == "Español"

T = {
    "title":      "🔬 Inteligencia de Color R&D — Robertet" if ES else "🔬 R&D Color Intelligence — Robertet",
    "t1":         "🔥 Proceso" if ES else "🔥 Process",
    "t2":         "📅 Vida de Anaquel" if ES else "📅 Shelf Life",
    "t3":         "🧪 Mezclas" if ES else "🧪 Blends",
    "t4":         "💡 Recomendador" if ES else "💡 Recommender",
    "sample":     "Muestra" if ES else "Sample",
    "pigment":    "Pigmento" if ES else "Pigment",
    "compare":    "Modo comparativo" if ES else "Comparison mode",
    "process":    "Proceso" if ES else "Process",
    "preset":     "Preset de proceso" if ES else "Process preset",
    "apppoint":   "Punto de aplicación" if ES else "Application point",
    "ca":         "Calcio en fijado (% CaCl₂)" if ES else "Calcium set bath (% CaCl₂)",
    "ph":         "pH del producto" if ES else "Product pH",
    "washratio":  "Enfriado: relación agua:producto" if ES else "Chilling: water:product ratio",
    "antiox":     "Sistema antioxidante (extracto de romero)" if ES else "Antioxidant system (rosemary extract)",
    "chem":       "Retención química" if ES else "Chemical retention",
    "phys":       "Retención física" if ES else "Physical retention",
    "deliv":      "COLOR ENTREGADO" if ES else "DELIVERED COLOUR",
    "chem_h":     "Sobrevive la molécula" if ES else "Molecule survives",
    "phys_h":     "Se queda en el producto" if ES else "Stays on the product",
    "deliv_h":    "Lo que ve el consumidor" if ES else "What the consumer sees",
    "storage":    "Temp. almacén (°C)" if ES else "Storage temp (°C)",
    "uv":         "Empaque (filtro UV)" if ES else "Packaging (UV filter)",
    "uv_opts":    (["Transparente (UV alto)", "Semi-opaco", "Opaco / sin UV"] if ES
                   else ["Clear (high UV)", "Semi-opaque", "Opaque / no UV"]),
    "months":     "Meses de anaquel" if ES else "Shelf life months",
    "stages":     "Etapas del proceso" if ES else "Process stages",
    "note":       "Análisis técnico" if ES else "Technical insight",
}

# ==========================================================================
# BASE DE DATOS DE PIGMENTOS
# --------------------------------------------------------------------------
# k85 ......... constante de degradación térmica (min⁻¹) a 85 °C, medio acuoso
# polarity .... "oil" | "water" | "both"  → gobierna la retención física
# o2 .......... sensibilidad a oxígeno (multiplicador sobre k)
# ca .......... retención tras el baño de calcio (1.00 = indiferente)
# light_k ..... constante de fotodegradación (mes⁻¹) sin filtro UV
# ph_opt ...... rango de pH donde el tono es estable
# ph_pen ...... penalización de k fuera del rango
# bind ........ retención en masa cárnica por fijación iónica a la proteína.
#               Solo aplica a pigmentos aniónicos (carmín, y los azoicos
#               sulfonados que se están reemplazando). Sobrescribe la
#               retención por polaridad, que subestima estos casos.
# ==========================================================================
PIGMENTS = {
    "Paprika (WD)":        dict(k85=0.0030, polarity="oil",   o2=1.20, ca=1.00, light_k=0.075, hue="#E63900", ph_opt=(2.0, 9.0), ph_pen=1.0),
    "Paprika (oil)":       dict(k85=0.0026, polarity="oil",   o2=1.10, ca=1.00, light_k=0.070, hue="#DA3A0E", ph_opt=(2.0, 9.0), ph_pen=1.0),
    "Lycopene":            dict(k85=0.0042, polarity="oil",   o2=1.85, ca=1.00, light_k=0.140, hue="#C6362B", ph_opt=(2.0, 9.0), ph_pen=1.0),
    "Bixin (annatto oil)": dict(k85=0.0022, polarity="oil",   o2=1.15, ca=1.00, light_k=0.090, hue="#E28313", ph_opt=(2.0, 9.0), ph_pen=1.0),
    "Norbixin (annatto)":  dict(k85=0.0050, polarity="water", o2=1.10, ca=0.15, light_k=0.095, hue="#D2691E", ph_opt=(4.5, 9.0), ph_pen=6.0),
    "Beta-carotene":       dict(k85=0.0010, polarity="oil",   o2=1.45, ca=1.00, light_k=0.110, hue="#FFB300", ph_opt=(2.0, 9.0), ph_pen=1.0),
    "β-apo-8'-carotenal":  dict(k85=0.0016, polarity="oil",   o2=1.40, ca=1.00, light_k=0.105, hue="#E8541F", ph_opt=(2.0, 9.0), ph_pen=1.0),
    "Caramel colour":      dict(k85=0.0002, polarity="water", o2=0.10, ca=1.00, light_k=0.010, hue="#7A4A21", ph_opt=(2.0, 9.0), ph_pen=1.0),
    "Carmine":             dict(k85=0.0008, polarity="water", o2=0.30, ca=0.75, light_k=0.030, hue="#8E1F2F", ph_opt=(3.5, 8.0), ph_pen=2.5, bind=0.92),
    "Red 40 + Yellow 6":   dict(k85=0.0003, polarity="water", o2=0.15, ca=1.00, light_k=0.020, hue="#D62828", ph_opt=(2.0, 9.0), ph_pen=1.0, bind=0.95),
    "Curcumin":            dict(k85=0.0100, polarity="both",  o2=1.00, ca=1.00, light_k=0.320, hue="#FFEA00", ph_opt=(2.0, 7.5), ph_pen=2.0),
    "Red Beet":            dict(k85=0.0400, polarity="water", o2=1.30, ca=1.00, light_k=0.180, hue="#C71585", ph_opt=(4.0, 6.0), ph_pen=2.0),
    "Natural Chlorophyll": dict(k85=0.0150, polarity="oil",   o2=1.20, ca=0.85, light_k=0.250, hue="#228B22", ph_opt=(6.0, 9.0), ph_pen=3.0),
    "Spirulina":           dict(k85=0.1500, polarity="water", o2=1.60, ca=1.00, light_k=0.400, hue="#4169E1", ph_opt=(5.5, 7.5), ph_pen=3.0),
}

# ==========================================================================
# PUNTOS DE APLICACIÓN — retención física (wash-out)
# --------------------------------------------------------------------------
# ADVERTENCIA: estos valores son ESTIMACIONES DE INGENIERÍA, no medidas.
# Cuantificarlos es exactamente el objetivo del Test B del protocolo Fase 0.
# ==========================================================================
APP_POINTS = {
    "bath": dict(
        es="Baño de agua (color en el agua)", en="Water bath (colour in the water)",
        retention={"oil": 0.08, "water": 0.35, "both": 0.22},
        note_es="El pigmento nunca se fija: se deposita y el enfriado lo devuelve al agua. "
                "Para un carotenoide (apolar) es prácticamente inviable — no hay afinidad con el agua ni con el alginato.",
        note_en="The pigment never fixes: it deposits and the chilling step returns it to the water. "
                "For an apolar carotenoid this is effectively unviable.",
    ),
    "gel": dict(
        es="Gel de alginato (color en la tripa)", en="Alginate gel (colour in the casing)",
        retention={"oil": 0.85, "water": 0.70, "both": 0.78},
        note_es="Atrapamiento físico en la red del gel. El color queda donde se ve. "
                "Depende de que el sistema de casing del proveedor permita dosificar.",
        note_en="Physical entrapment in the gel network. Colour sits where it is seen. "
                "Depends on the casing supplier allowing dosing.",
    ),
    "meat": dict(
        es="Masa cárnica (color en la emulsión)", en="Meat emulsion (colour in the mix)",
        retention={"oil": 0.95, "water": 0.60, "both": 0.78},
        note_es="Partición en la fase grasa de la emulsión. El pigmento queda protegido dentro "
                "del producto: ni el baño ácido ni el enfriado lo alcanzan.",
        note_en="Partition into the fat phase. The pigment is protected inside the product: "
                "neither the acid bath nor the chilling step reaches it.",
    ),
}

# ==========================================================================
# PRESETS DE PROCESO — (nombre, °C, minutos, exposición a O₂)
# ==========================================================================
PRESETS = {
    "Freddy Hirsch / Sigma — salchicha coextruida": [
        ("Fijado Ca²⁺",  20, 2,  0.8),
        ("Cocción agua", 82, 15, 1.0),
        ("Horno seco",   70, 20, 1.6),
        ("Enfriado",      7, 20, 0.9),
    ],
    "Pasteurización simple": [("Pasteurización", 72, 15, 1.0)],
    "Esterilización UHT":    [("UHT", 140, 1, 0.7)],
    "Horneado":              [("Horneado", 180, 25, 1.8)],
    "Personalizado":         [("Etapa 1", 82, 15, 1.0)],
}

UV_FACTOR = {0: 1.0, 1: 0.45, 2: 0.05}


# ==========================================================================
# MODELO
# ==========================================================================
def ph_multiplier(p, ph):
    """Penalización de velocidad de degradación fuera del rango de pH óptimo."""
    lo, hi = p["ph_opt"]
    if lo <= ph <= hi:
        return 1.0
    delta = (lo - ph) if ph < lo else (ph - hi)
    return 1.0 + (p["ph_pen"] - 1.0) * min(delta / 1.5, 1.0) * p["ph_pen"]


def stage_rate(p, temp_c, o2_exposure, ph, antiox):
    """Constante de degradación efectiva para una etapa."""
    if temp_c < 40:
        thermal = p["k85"] * 0.02 * (max(temp_c, 1) / 85.0) ** 2.5
    else:
        thermal = p["k85"] * (temp_c / 85.0) ** 2.5
    o2 = p["o2"] * o2_exposure
    if antiox:
        o2 = 1.0 + (o2 - 1.0) * 0.45 if o2 > 1.0 else o2
    return thermal * o2 * ph_multiplier(p, ph)


def thermal_curve(pigment_name, stages, ph, antiox, points_per_stage=40):
    """Curva de retención química a lo largo de todas las etapas del proceso."""
    p = PIGMENTS[pigment_name]
    t_axis, y_axis, boundaries = [0.0], [100.0], []
    clock, level = 0.0, 100.0
    for label, temp_c, minutes, o2 in stages:
        k = stage_rate(p, temp_c, o2, ph, antiox)
        local = np.linspace(0, minutes, points_per_stage)[1:]
        for dt in local:
            t_axis.append(clock + dt)
            y_axis.append(level * float(np.exp(-k * dt)))
        level = level * float(np.exp(-k * minutes))
        clock += minutes
        boundaries.append((clock, label))
    return np.array(t_axis), np.array(y_axis), boundaries


def calcium_retention(pigment_name, ca_pct):
    """Retención tras el baño de fijado. Los carotenoides son indiferentes al Ca²⁺."""
    p = PIGMENTS[pigment_name]
    if p["ca"] >= 0.999:
        return 1.0
    severity = min(ca_pct / 1.0, 1.5)
    return float(1.0 - (1.0 - p["ca"]) * severity)


def washout_retention(pigment_name, app_point, ratio=10.0):
    """Retención física en el enfriado, según dónde se aplicó el color."""
    p = PIGMENTS[pigment_name]
    base = APP_POINTS[app_point]["retention"][p["polarity"]]
    # Los pigmentos aniónicos se fijan iónicamente a la proteína cárnica cerca
    # de su punto isoeléctrico. La retención por polaridad los subestima.
    if app_point == "meat" and p.get("bind"):
        base = p["bind"]
    elif app_point == "bath" and p.get("bind"):
        base = min(p["bind"] * 0.55, 0.60)  # migra y se fija, pero solo en superficie
    # Más agua de enfriado por kg de producto = más pérdida, con rendimientos decrecientes
    adj = base * (10.0 / max(ratio, 1.0)) ** 0.12
    return float(min(max(adj, 0.01), 0.99))


def shelf_curve(pigment_name, months, uv_idx, storage_c, antiox):
    """Pérdida de color durante el anaquel: luz + temperatura de almacén."""
    p = PIGMENTS[pigment_name]
    k_light = p["light_k"] * UV_FACTOR[uv_idx]
    k_temp = p["k85"] * 60.0 * (max(storage_c, 0) / 85.0) ** 2.0
    k = k_light + k_temp
    if antiox:
        k *= 0.55
    m = np.linspace(0, months, 60)
    return m, 100.0 * np.exp(-k * m)


def full_result(pigment_name, stages, ph, antiox, ca_pct, app_point, ratio):
    """Devuelve los tres KPIs del proceso completo."""
    t, y, bounds = thermal_curve(pigment_name, stages, ph, antiox)
    chem = float(y[-1])
    ca = calcium_retention(pigment_name, ca_pct)
    wash = washout_retention(pigment_name, app_point, ratio)
    phys = ca * wash
    return dict(t=t, y=y, bounds=bounds, chem=chem, ca=ca,
                wash=wash, phys=phys * 100.0, delivered=chem * phys)


# ==========================================================================
# BARRA LATERAL
# ==========================================================================
st.sidebar.image(LOGO, width=180)

st.sidebar.markdown(f"### {T['sample']} A")
pig_list = list(PIGMENTS.keys())
p1 = st.sidebar.selectbox(f"{T['pigment']} (A)", pig_list, index=pig_list.index("Paprika (WD)"))

compare_on = st.sidebar.checkbox(T["compare"])
p2 = None
if compare_on:
    p2 = st.sidebar.selectbox(f"{T['pigment']} (B)", pig_list, index=pig_list.index("Lycopene"))

st.sidebar.markdown(f"--- \n### ⚙️ {T['process']}")
preset_name = st.sidebar.selectbox(T["preset"], list(PRESETS.keys()))
stages = [list(s) for s in PRESETS[preset_name]]

if preset_name == "Personalizado":
    n = st.sidebar.number_input("Etapas" if ES else "Stages", 1, 5, 2)
    stages = []
    for i in range(int(n)):
        st.sidebar.caption(f"— {'Etapa' if ES else 'Stage'} {i+1}")
        tc = st.sidebar.slider(f"°C #{i+1}", 2, 200, 82, key=f"t{i}")
        mn = st.sidebar.slider(f"min #{i+1}", 1, 120, 15, key=f"m{i}")
        o2 = st.sidebar.select_slider(
            f"O₂ #{i+1}", options=[0.7, 0.9, 1.0, 1.3, 1.6, 1.8], value=1.0, key=f"o{i}")
        stages.append([f"{'Etapa' if ES else 'Stage'} {i+1}", tc, mn, o2])
else:
    with st.sidebar.expander(T["stages"], expanded=False):
        for label, tc, mn, o2 in stages:
            st.caption(f"**{label}** · {tc} °C · {mn} min · O₂ ×{o2}")

app_labels = {k: (v["es"] if ES else v["en"]) for k, v in APP_POINTS.items()}
app_point = st.sidebar.radio(
    T["apppoint"], list(APP_POINTS.keys()),
    format_func=lambda k: app_labels[k], index=0)

ph_val = st.sidebar.slider(T["ph"], 2.0, 10.0, 5.8, 0.1)
ca_pct = st.sidebar.slider(T["ca"], 0.0, 3.0, 1.0, 0.1)
wash_ratio = st.sidebar.slider(T["washratio"], 1.0, 30.0, 10.0, 1.0)
antiox = st.sidebar.checkbox(T["antiox"], value=False)

st.sidebar.markdown(f"--- \n### 📦 {T['t2']}")
storage_c = st.sidebar.slider(T["storage"], 0, 25, 4)
uv_idx = T["uv_opts"].index(st.sidebar.selectbox(T["uv"], T["uv_opts"], index=1))
months = st.sidebar.slider(T["months"], 1, 24, 6)

R1 = full_result(p1, stages, ph_val, antiox, ca_pct, app_point, wash_ratio)
R2 = full_result(p2, stages, ph_val, antiox, ca_pct, app_point, wash_ratio) if compare_on else None

# ==========================================================================
# DASHBOARD
# ==========================================================================
st.title(T["title"])
tab_p, tab_s, tab_b, tab_r = st.tabs([T["t1"], T["t2"], T["t3"], T["t4"]])

# ---------------------------------------------------------------- PROCESO
with tab_p:
    def kpi_row(name, R, label):
        st.markdown(
            f'<div style="background:{PIGMENTS[name]["hue"]};opacity:{max(0.12, R["delivered"]/100)};'
            f'height:56px;border-radius:8px;display:flex;align-items:center;justify-content:center;'
            f'color:#fff;font-weight:700;border:1px solid #ddd;">{label}: {name}</div>',
            unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric(T["chem"], f"{R['chem']:.1f}%", help=T["chem_h"])
        k2.metric(T["phys"], f"{R['phys']:.1f}%", help=T["phys_h"])
        k3.metric(T["deliv"], f"{R['delivered']:.1f}%", help=T["deliv_h"])

    kpi_row(p1, R1, "A")
    if compare_on:
        st.markdown("")
        kpi_row(p2, R2, "B")

    st.markdown("---")
    c1, c2 = st.columns([2.4, 1])

    with c1:
        fig, ax = plt.subplots(figsize=(9, 4.2))
        ax.plot(R1["t"], R1["y"], color=PIGMENTS[p1]["hue"], lw=3.2, label=f"A: {p1}")
        ax.axhline(R1["delivered"], color=PIGMENTS[p1]["hue"], lw=2, ls=":",
                   label=f"A: {T['deliv'].lower()} {R1['delivered']:.0f}%")
        if compare_on:
            ax.plot(R2["t"], R2["y"], color=PIGMENTS[p2]["hue"], lw=2.6, ls="--", label=f"B: {p2}")
            ax.axhline(R2["delivered"], color=PIGMENTS[p2]["hue"], lw=1.6, ls=":")
        for x, label in R1["bounds"][:-1]:
            ax.axvline(x, color="#999", lw=0.8, alpha=0.5)
        for i, (x, label) in enumerate(R1["bounds"]):
            x0 = 0 if i == 0 else R1["bounds"][i - 1][0]
            ax.text((x0 + x) / 2, 3, label, ha="center", fontsize=7.5, color="#555")
        ax.set_ylim(-2, 105)
        ax.set_xlabel("min")
        ax.set_ylabel("%")
        ax.grid(alpha=0.18)
        ax.legend(fontsize=8, loc="lower left")
        st.pyplot(fig)

    with c2:
        st.markdown(f"**{T['note']}**")
        st.caption(APP_POINTS[app_point]["note_es" if ES else "note_en"])
        st.markdown(
            f"- {T['chem']}: **{R1['chem']:.1f}%**\n"
            f"- Calcio: **×{R1['ca']:.2f}**\n"
            f"- Wash-out: **×{R1['wash']:.2f}**\n"
            f"- **{T['deliv']}: {R1['delivered']:.1f}%**")
        gap = R1["chem"] - R1["delivered"]
        if gap > 40:
            st.error(
                f"⚠️ {gap:.0f} puntos de color se pierden **después** de sobrevivir el proceso. "
                "El problema no es estabilidad térmica: es el punto de aplicación."
                if ES else
                f"⚠️ {gap:.0f} points of colour are lost **after** surviving the process. "
                "The issue is not thermal stability: it is the application point.")
        elif R1["ca"] < 0.9:
            st.warning("⚠️ Pérdida por calcio significativa: riesgo de precipitación y moteado."
                       if ES else "⚠️ Significant calcium loss: precipitation and speckling risk.")
        else:
            st.success("✅ Sin cuello de botella evidente en este escenario."
                       if ES else "✅ No obvious bottleneck in this scenario.")

    st.caption(
        "Los factores de retención física son estimaciones de ingeniería, no medidas de laboratorio. "
        "Cuantificarlos es el objetivo del Test B del protocolo de Fase 0."
        if ES else
        "Physical retention factors are engineering estimates, not laboratory measurements. "
        "Quantifying them is the purpose of Test B in the Phase 0 protocol.")

# ---------------------------------------------------------------- ANAQUEL
with tab_s:
    st.subheader("📅 " + ("Estabilidad durante el anaquel" if ES else "Shelf life stability"))
    st.caption("Parte del color entregado al final del proceso, no del 100%."
               if ES else "Starts from the delivered colour, not from 100%.")

    m1, s1 = shelf_curve(p1, months, uv_idx, storage_c, antiox)
    s1 = s1 * R1["delivered"] / 100.0

    fig2, ax2 = plt.subplots(figsize=(9, 4))
    ax2.plot(m1, s1, color=PIGMENTS[p1]["hue"], lw=3.2, label=f"A: {p1}")
    if compare_on:
        m2, s2 = shelf_curve(p2, months, uv_idx, storage_c, antiox)
        s2 = s2 * R2["delivered"] / 100.0
        ax2.plot(m2, s2, color=PIGMENTS[p2]["hue"], lw=2.6, ls="--", label=f"B: {p2}")
    ax2.axhline(70, color="#666", ls=":", lw=1.2)
    ax2.text(months * 0.02, 71.5, "Umbral aceptable" if ES else "Acceptable threshold",
             fontsize=8, color="#666")
    ax2.set_xlabel("meses" if ES else "months")
    ax2.set_ylabel("%")
    ax2.set_ylim(-2, 105)
    ax2.grid(alpha=0.18)
    ax2.legend(fontsize=8)
    st.pyplot(fig2)

    e1, e2 = st.columns(2)
    e1.metric(f"A — {'Final anaquel' if ES else 'End of shelf life'}", f"{s1[-1]:.1f}%")
    if compare_on:
        e2.metric(f"B — {'Final anaquel' if ES else 'End of shelf life'}", f"{s2[-1]:.1f}%")

    if PIGMENTS[p1]["light_k"] > 0.12 and uv_idx == 0 and not antiox:
        st.warning(
            "⚠️ Pigmento fotosensible en empaque transparente y sin antioxidante. "
            "Activar el sistema de romero o cambiar a empaque semi-opaco."
            if ES else
            "⚠️ Light-sensitive pigment in clear packaging without antioxidant. "
            "Enable the rosemary system or move to semi-opaque packaging.")

# ---------------------------------------------------------------- MEZCLAS
with tab_b:
    st.subheader("🧪 " + ("Constructor de mezclas" if ES else "Blend builder"))
    st.caption("Tono indicativo por mezcla aditiva ponderada. No sustituye un matching espectrofotométrico."
               if ES else "Indicative hue by weighted additive mixing. Not a substitute for spectrophotometric matching.")

    chosen = st.multiselect(
        "Componentes" if ES else "Components", pig_list,
        default=["Paprika (WD)", "Lycopene", "Caramel colour"])

    if chosen:
        doses, cols = {}, st.columns(min(len(chosen), 4))
        for i, name in enumerate(chosen):
            with cols[i % len(cols)]:
                doses[name] = st.slider(name, 0, 100, 100 // max(len(chosen), 1), key=f"d_{name}")

        total = sum(doses.values()) or 1
        rgb_mix = np.zeros(3)
        deliv_w = 0.0
        rows = []
        for name, dose in doses.items():
            R = full_result(name, stages, ph_val, antiox, ca_pct, app_point, wash_ratio)
            w = dose / total
            eff = w * R["delivered"] / 100.0
            rgb_mix += np.array(mcolors.to_rgb(PIGMENTS[name]["hue"])) * eff
            deliv_w += eff
            rows.append((name, f"{dose}", f"{R['chem']:.0f}%", f"{R['delivered']:.0f}%"))

        if deliv_w > 0:
            rgb_norm = np.clip(rgb_mix / deliv_w, 0, 1)
            hex_mix = mcolors.to_hex(rgb_norm)
            b1, b2 = st.columns([1, 2])
            with b1:
                st.markdown(
                    f'<div style="background:{hex_mix};height:110px;border-radius:10px;'
                    f'border:1px solid #ccc;"></div>', unsafe_allow_html=True)
                st.caption(f"{hex_mix} · {'entrega' if ES else 'delivery'} {deliv_w*100:.0f}%")
            with b2:
                st.table({
                    T["pigment"]: [r[0] for r in rows],
                    "Dosis" if ES else "Dose": [r[1] for r in rows],
                    T["chem"]: [r[2] for r in rows],
                    T["deliv"]: [r[3] for r in rows],
                })
            weakest = min(rows, key=lambda r: float(r[3].rstrip("%")))
            st.info(f"{'Componente limitante' if ES else 'Limiting component'}: **{weakest[0]}** "
                    f"({weakest[3]} {'entregado' if ES else 'delivered'})")

# ---------------------------------------------------------------- RECOMENDADOR
with tab_r:
    st.subheader("🎯 " + ("Búsqueda por tono" if ES else "Target hue search"))
    rc1, rc2 = st.columns([1, 2])
    with rc1:
        target = st.color_picker("Color objetivo" if ES else "Target colour", "#C0392B")
        st.markdown(f'<div style="background:{target};height:100px;border-radius:10px;'
                    f'border:1px solid #ccc;"></div>', unsafe_allow_html=True)
    with rc2:
        hue = colorsys.rgb_to_hsv(*mcolors.to_rgb(target))[0] * 360
        ranked = []
        for name, p in PIGMENTS.items():
            h_p = colorsys.rgb_to_hsv(*mcolors.to_rgb(p["hue"]))[0] * 360
            d_hue = min(abs(hue - h_p), 360 - abs(hue - h_p))
            R = full_result(name, stages, ph_val, antiox, ca_pct, app_point, wash_ratio)
            score = R["delivered"] - d_hue * 1.4
            ranked.append((score, name, d_hue, R["delivered"]))
        ranked.sort(reverse=True)

        st.markdown("### 🏆 " + ("Ranking" if ES else "Ranking"))
        for score, name, d_hue, deliv in ranked[:4]:
            bar = "█" * max(1, int(deliv / 10))
            st.markdown(
                f"<span style='color:{PIGMENTS[name]['hue']};font-size:18px'>{bar}</span> "
                f"**{name}** — {'Δtono' if ES else 'Δhue'} {d_hue:.0f}° · "
                f"{T['deliv'].lower()} {deliv:.0f}%", unsafe_allow_html=True)

        best = ranked[0]
        if best[3] < 25:
            st.error("❌ " + ("Ningún pigmento entrega color suficiente en este punto de aplicación. "
                             "Mover la aplicación antes de cambiar de pigmento."
                             if ES else
                             "No pigment delivers enough colour at this application point. "
                             "Move the application point before changing pigment."))
        elif best[2] > 25:
            st.warning("⚠️ " + ("Ningún componente único cubre el tono. Usar mezcla."
                                if ES else "No single component covers the hue. Use a blend."))
        else:
            st.success(f"✅ **{best[1]}** — {'candidato principal' if ES else 'lead candidate'}.")

st.caption("Confidential Robertet R&D — Regional Division.")
