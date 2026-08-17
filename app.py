"""
Robertet R&D — Color Intelligence Simulator
v4

Cambios respecto a v3:
  1. Gráfica interactiva (Plotly): hover con valores, zoom, etapas sombreadas.
  2. Dosificación MULTIPUNTO: baño, gel y masa pueden usarse a la vez, o ninguno.
  3. Mezclas de hasta 5 componentes con interruptor individual.
  4. Selector de sistema antioxidante.
  5. El wash-out YA NO SE ELIGE: se calcula desde las etapas húmedas del proceso.

Modelo de pérdida física — dos fenómenos separados, antes confundidos en uno:
    CAPTACIÓN  ¿el pigmento llegó al producto?      (falla en el baño de agua)
    RETENCIÓN  ¿se quedó ahí?                       (falla en el enfriado)
Un carotenoide en el baño no pierde color por lavado: nunca se depositó.
"""

import streamlit as st
import numpy as np
import pandas as pd
import colorsys
import plotly.graph_objects as go
import matplotlib.colors as mcolors

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

lang = st.sidebar.selectbox("🌐 Language / Idioma", ["Español", "English"])
ES = lang == "Español"


def t(es, en):
    return es if ES else en


# ==========================================================================
# PIGMENTOS
# --------------------------------------------------------------------------
# k85 ..... degradación térmica (min⁻¹) a 85 °C
# pol ..... "oil" | "water" | "both" — gobierna captación y retención
# o2 ...... sensibilidad a oxígeno
# ca ...... retención tras el baño de calcio (1.00 = indiferente)
# light ... fotodegradación (mes⁻¹) sin filtro UV
# bind .... fijación iónica a proteína cárnica (aniónicos). None = no aplica
# ==========================================================================
PIGMENTS = {
    "Paprika (WD)":        dict(k85=.0030, pol="oil",   o2=1.20, ca=1.00, light=.075, bind=None, hue="#E63900", ph=(2, 9), pen=1.0),
    "Paprika (oil)":       dict(k85=.0026, pol="oil",   o2=1.10, ca=1.00, light=.070, bind=None, hue="#DA3A0E", ph=(2, 9), pen=1.0),
    "Lycopene":            dict(k85=.0042, pol="oil",   o2=1.85, ca=1.00, light=.140, bind=None, hue="#C6362B", ph=(2, 9), pen=1.0),
    "Bixin (annatto oil)": dict(k85=.0022, pol="oil",   o2=1.15, ca=1.00, light=.090, bind=None, hue="#E28313", ph=(2, 9), pen=1.0),
    "Norbixin (annatto)":  dict(k85=.0050, pol="water", o2=1.10, ca=0.15, light=.095, bind=None, hue="#D2691E", ph=(4.5, 9), pen=6.0),
    "Beta-carotene":       dict(k85=.0010, pol="oil",   o2=1.45, ca=1.00, light=.110, bind=None, hue="#FFB300", ph=(2, 9), pen=1.0),
    "β-apo-8'-carotenal":  dict(k85=.0016, pol="oil",   o2=1.40, ca=1.00, light=.105, bind=None, hue="#E8541F", ph=(2, 9), pen=1.0),
    "Caramel colour":      dict(k85=.0002, pol="water", o2=0.10, ca=1.00, light=.010, bind=None, hue="#7A4A21", ph=(2, 9), pen=1.0),
    "Carmine":             dict(k85=.0008, pol="water", o2=0.30, ca=0.75, light=.030, bind=0.93, hue="#8E1F2F", ph=(3.5, 8), pen=2.5),
    "Red 40 + Yellow 6":   dict(k85=.0003, pol="water", o2=0.15, ca=1.00, light=.020, bind=0.95, hue="#D62828", ph=(2, 9), pen=1.0),
    "Curcumin":            dict(k85=.0100, pol="both",  o2=1.00, ca=1.00, light=.320, bind=None, hue="#FFEA00", ph=(2, 7.5), pen=2.0),
    "Red Beet":            dict(k85=.0400, pol="water", o2=1.30, ca=1.00, light=.180, bind=None, hue="#C71585", ph=(4, 6), pen=2.0),
    "Natural Chlorophyll": dict(k85=.0150, pol="oil",   o2=1.20, ca=0.85, light=.250, bind=None, hue="#228B22", ph=(6, 9), pen=3.0),
    "Spirulina":           dict(k85=.1500, pol="water", o2=1.60, ca=1.00, light=.400, bind=None, hue="#4169E1", ph=(5.5, 7.5), pen=3.0),
}

# ==========================================================================
# PUNTOS DE APLICACIÓN
# --------------------------------------------------------------------------
# uptake ......... fracción del pigmento dosificado que llega al producto
# bound .......... fracción inmovilizada que NUNCA se va, por más agua que pase
# leach_k ........ velocidad de salida de la fracción no fijada (min⁻¹ de contacto acuoso)
#
# Los valores son estimaciones de ingeniería. Medirlos es el objeto del
# Test B del protocolo de Fase 0.
# ==========================================================================
APP_POINTS = {
    "bath": dict(
        es="Baño de agua", en="Water bath",
        desc_es="Color disuelto en el agua de cocción; migra al producto.",
        desc_en="Colour dissolved in the cooking water; migrates to the product.",
        uptake={"oil": 0.10, "water": 0.55, "both": 0.30, "bind": 0.72},
        bound={"oil": 0.12, "water": 0.28, "both": 0.18, "bind": 0.76},
        leach={"oil": 0.045, "water": 0.040, "both": 0.042, "bind": 0.018},
    ),
    "gel": dict(
        es="Gel de alginato", en="Alginate gel",
        desc_es="Color dosificado en el gel antes de la coextrusión.",
        desc_en="Colour dosed into the gel before co-extrusion.",
        uptake={"oil": 1.00, "water": 1.00, "both": 1.00, "bind": 1.00},
        bound={"oil": 0.80, "water": 0.38, "both": 0.60, "bind": 0.55},
        leach={"oil": 0.015, "water": 0.035, "both": 0.025, "bind": 0.020},
    ),
    "meat": dict(
        es="Masa cárnica", en="Meat emulsion",
        desc_es="Color dosificado en la emulsión antes de formar.",
        desc_en="Colour dosed into the emulsion before forming.",
        uptake={"oil": 1.00, "water": 1.00, "both": 1.00, "bind": 1.00},
        bound={"oil": 0.96, "water": 0.45, "both": 0.72, "bind": 0.93},
        leach={"oil": 0.008, "water": 0.030, "both": 0.018, "bind": 0.006},
    ),
}

# etapa: (nombre, °C, min, O₂, húmeda?, agitación 0-1)
PRESETS = {
    "Freddy Hirsch / Sigma — coextruida": [
        ("Fijado Ca²⁺",  20, 2,  0.8, True,  0.3),
        ("Cocción agua", 82, 15, 1.0, True,  0.5),
        ("Horno seco",   70, 20, 1.6, False, 0.0),
        ("Enfriado agua", 7, 20, 0.9, True,  0.6),
    ],
    "Pasteurización simple": [("Pasteurización", 72, 15, 1.0, True, 0.4)],
    "Esterilización UHT":    [("UHT", 140, 1, 0.7, True, 0.5)],
    "Horneado":              [("Horneado", 180, 25, 1.8, False, 0.0)],
}

ANTIOX = {
    t("Ninguno", "None"):                       dict(o2=1.00, light=1.00),
    t("Extracto de romero", "Rosemary extract"): dict(o2=0.45, light=0.60),
    t("Tocoferoles", "Tocopherols"):             dict(o2=0.65, light=0.80),
    t("Romero + tocoferoles", "Rosemary + tocopherols"): dict(o2=0.35, light=0.55),
    t("Ascorbato / eritorbato", "Ascorbate / erythorbate"): dict(o2=0.75, light=0.95),
}

UV_FACTOR = {0: 1.0, 1: 0.45, 2: 0.05}


# ==========================================================================
# MODELO
# ==========================================================================
def pol_key(p):
    """Clave de comportamiento físico: los aniónicos que se fijan van aparte."""
    return "bind" if p["bind"] else p["pol"]


def ph_mult(p, ph):
    lo, hi = p["ph"]
    if lo <= ph <= hi:
        return 1.0
    d = (lo - ph) if ph < lo else (ph - hi)
    return 1.0 + (p["pen"] - 1.0) * min(d / 1.5, 1.0) * p["pen"]


def stage_k(p, temp_c, o2_exp, ph, ax):
    if temp_c < 40:
        therm = p["k85"] * 0.02 * (max(temp_c, 1) / 85.0) ** 2.5
    else:
        therm = p["k85"] * (temp_c / 85.0) ** 2.5
    o2 = p["o2"] * o2_exp
    if o2 > 1.0:
        o2 = 1.0 + (o2 - 1.0) * ANTIOX[ax]["o2"]
    return therm * o2 * ph_mult(p, ph)


def thermal_curve(name, stages, ph, ax, n=40):
    p = PIGMENTS[name]
    ts, ys, bounds = [0.0], [100.0], []
    clock, level = 0.0, 100.0
    for label, tc, mn, o2, wet, agit in stages:
        k = stage_k(p, tc, o2, ph, ax)
        for dt in np.linspace(0, mn, n)[1:]:
            ts.append(clock + dt)
            ys.append(level * float(np.exp(-k * dt)))
        level *= float(np.exp(-k * mn))
        bounds.append((clock, clock + mn, label, tc, wet))
        clock += mn
    return np.array(ts), np.array(ys), bounds


def aqueous_contact(stages, app_point):
    """
    Minutos efectivos de contacto acuoso DESPUÉS de que el color está en su sitio.
    Se calcula solo — el usuario ya no elige un factor de lavado.
    La agitación y la temperatura aceleran la extracción.
    """
    total = 0.0
    for label, tc, mn, o2, wet, agit in stages:
        if not wet:
            continue
        # El color dosificado en el gel o la masa ya está presente desde el inicio.
        # El del baño solo empieza a poder salir después de haber entrado.
        temp_f = 1.0 + max(tc - 20, 0) / 100.0     # más caliente = más extracción
        agit_f = 1.0 + agit * 0.8                  # agitación mecánica
        total += mn * temp_f * agit_f
    return total


def physical_retention(name, app_point, stages, cook_loss_pct):
    """Captación × retención, ambas derivadas del proceso. Sin sliders."""
    p = PIGMENTS[name]
    k = pol_key(p)
    ap = APP_POINTS[app_point]
    contact = aqueous_contact(stages, app_point)

    uptake = ap["uptake"][k]
    bound = ap["bound"][k]
    leach = ap["leach"][k]

    retention = bound + (1.0 - bound) * float(np.exp(-leach * contact))

    # Arrastre por merma: la grasa y el agua que salen se llevan pigmento.
    # Solo golpea al color que está dentro de la emulsión.
    if app_point == "meat":
        retention *= (1.0 - (cook_loss_pct / 100.0) * (0.9 if k == "oil" else 0.5))

    return dict(uptake=uptake, retention=max(retention, 0.0),
                phys=uptake * max(retention, 0.0), contact=contact)


def calcium_retention(name, ca_pct, ca_step_on):
    if not ca_step_on:
        return 1.0
    p = PIGMENTS[name]
    if p["ca"] >= 0.999:
        return 1.0
    return float(1.0 - (1.0 - p["ca"]) * min(ca_pct / 1.0, 1.5))


def full_result(name, stages, ph, ax, ca_pct, ca_on, dosing, cook_loss):
    """
    dosing: dict {punto: fracción de dosis}. Puede tener 1, 2 o 3 puntos activos,
    o estar vacío.
    """
    ts, ys, bounds = thermal_curve(name, stages, ph, ax)
    chem = float(ys[-1])
    ca = calcium_retention(name, ca_pct, ca_on)

    delivered, breakdown = 0.0, {}
    for pt, share in dosing.items():
        if share <= 0:
            continue
        ph_r = physical_retention(name, pt, stages, cook_loss)
        d = chem * ca * ph_r["phys"] * share
        delivered += d
        breakdown[pt] = dict(share=share, **ph_r, delivered=d)

    total_share = sum(dosing.values()) or 1.0
    phys_eff = (delivered / (chem * ca)) / total_share * 100.0 if chem * ca > 0 else 0.0

    return dict(ts=ts, ys=ys, bounds=bounds, chem=chem, ca=ca,
                phys=phys_eff, delivered=delivered, breakdown=breakdown)


def shelf_curve(name, months, uv_idx, storage_c, ax):
    p = PIGMENTS[name]
    k = p["light"] * UV_FACTOR[uv_idx] * ANTIOX[ax]["light"]
    k += p["k85"] * 60.0 * (max(storage_c, 0) / 85.0) ** 2.0 * ANTIOX[ax]["o2"]
    m = np.linspace(0, months, 60)
    return m, 100.0 * np.exp(-k * m)


# ==========================================================================
# BARRA LATERAL
# ==========================================================================
st.sidebar.image(LOGO, width=180)
pig_list = list(PIGMENTS.keys())

st.sidebar.markdown("### " + t("Muestra", "Sample"))
p1 = st.sidebar.selectbox(t("Pigmento", "Pigment") + " (A)", pig_list,
                          index=pig_list.index("Paprika (WD)"))
compare_on = st.sidebar.checkbox(t("Modo comparativo", "Comparison mode"))
p2 = st.sidebar.selectbox(t("Pigmento", "Pigment") + " (B)", pig_list,
                          index=pig_list.index("Lycopene")) if compare_on else None

# ---------------------------------------------------------------- proceso
st.sidebar.markdown("--- \n### ⚙️ " + t("Proceso", "Process"))
preset = st.sidebar.selectbox(t("Preset", "Preset"), list(PRESETS.keys()))

st.sidebar.caption(t("Etapas activables. Editable abajo.", "Toggleable stages. Editable below."))
raw_stages = PRESETS[preset]
active_flags = []
for i, (label, tc, mn, o2, wet, agit) in enumerate(raw_stages):
    active_flags.append(st.sidebar.checkbox(f"{label} · {tc}°C · {mn}min",
                                            value=True, key=f"stg_{preset}_{i}"))

with st.sidebar.expander(t("Editar etapas", "Edit stages")):
    df = pd.DataFrame(
        [dict(Etapa=s[0], C=s[1], min=s[2], O2=s[3], Húmeda=s[4], Agit=s[5])
         for s, a in zip(raw_stages, active_flags) if a])
    if not df.empty:
        df = st.data_editor(df, hide_index=True, num_rows="fixed",
                            key=f"ed_{preset}", width="stretch")

stages = [(r.Etapa, float(r.C), float(r["min"]), float(r.O2), bool(r.Húmeda), float(r.Agit))
          for r in df.itertuples()] if not df.empty else []

if not stages:
    st.sidebar.error(t("Sin etapas activas.", "No active stages."))
    st.stop()

# ---------------------------------------------------------------- dosificación
st.sidebar.markdown("--- \n### 🎯 " + t("Dosificación", "Dosing"))
st.sidebar.caption(t("Se pueden activar varios puntos a la vez, o ninguno.",
                     "Several points can be active at once, or none."))
dosing_raw = {}
for key, ap in APP_POINTS.items():
    on = st.sidebar.checkbox(ap["es"] if ES else ap["en"],
                             value=(key == "meat"), key=f"ap_{key}")
    if on:
        dosing_raw[key] = st.sidebar.slider(
            "→ % " + t("de la dosis", "of dose"), 0, 100, 100, 5, key=f"sh_{key}")

tot = sum(dosing_raw.values())
dosing = {k: v / tot for k, v in dosing_raw.items()} if tot > 0 else {}
if tot > 0 and len(dosing_raw) > 1:
    st.sidebar.caption(t(f"Normalizado sobre {tot}%.", f"Normalised over {tot}%."))

# ---------------------------------------------------------------- condiciones
st.sidebar.markdown("--- \n### 🧪 " + t("Condiciones", "Conditions"))
ca_on = st.sidebar.checkbox(t("Baño de fijado con calcio", "Calcium setting bath"), value=True)
ca_pct = st.sidebar.slider("CaCl₂ %", 0.0, 3.0, 1.0, 0.1, disabled=not ca_on)
ph_val = st.sidebar.slider("pH", 2.0, 10.0, 5.8, 0.1)
cook_loss = st.sidebar.slider(t("Merma de cocción (%)", "Cook loss (%)"), 0, 25, 6)
antiox = st.sidebar.selectbox(t("Sistema antioxidante", "Antioxidant system"), list(ANTIOX.keys()))

st.sidebar.markdown("--- \n### 📦 " + t("Anaquel", "Shelf life"))
storage_c = st.sidebar.slider(t("Temp. almacén (°C)", "Storage temp (°C)"), 0, 25, 4)
uv_opts = t(["Transparente", "Semi-opaco", "Opaco / sin UV"], ["Clear", "Semi-opaque", "Opaque / no UV"])
uv_idx = uv_opts.index(st.sidebar.selectbox(t("Empaque", "Packaging"), uv_opts, index=1))
months = st.sidebar.slider(t("Meses", "Months"), 1, 24, 6)

R1 = full_result(p1, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss)
R2 = full_result(p2, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss) if compare_on else None

# ==========================================================================
# GRÁFICA INTERACTIVA
# ==========================================================================
def process_figure(results):
    fig = go.Figure()
    for i, (start, end, label, tc, wet) in enumerate(results[0][1]["bounds"]):
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor="#4A90D9" if wet else "#E8A33D",
            opacity=0.09, layer="below", line_width=0,
            annotation_text=f"{label}<br>{tc:.0f}°C", annotation_position="top left",
            annotation_font_size=9, annotation_font_color="#666")
    for name, R, dash in results:
        p = PIGMENTS[name]
        fig.add_trace(go.Scatter(
            x=R["ts"], y=R["ys"], mode="lines", name=name,
            line=dict(color=p["hue"], width=3.4, dash=dash),
            hovertemplate="<b>%{fullData.name}</b><br>" +
                          t("Minuto", "Minute") + " %{x:.1f}<br>" +
                          t("Retención química", "Chemical retention") +
                          " <b>%{y:.1f}%</b><extra></extra>"))
        fig.add_hline(y=R["delivered"], line=dict(color=p["hue"], width=1.6, dash="dot"),
                      annotation_text=t("entregado ", "delivered ") + f"{R['delivered']:.0f}%",
                      annotation_position="right", annotation_font_size=10,
                      annotation_font_color=p["hue"])
    fig.update_layout(
        height=420, margin=dict(l=10, r=70, t=30, b=10),
        hovermode="x unified", plot_bgcolor="white",
        xaxis=dict(title=t("Tiempo (min)", "Time (min)"), showspikes=True,
                   spikemode="across", spikethickness=1, spikecolor="#999",
                   gridcolor="#EEE"),
        yaxis=dict(title="%", range=[-2, 105], gridcolor="#EEE"),
        legend=dict(orientation="h", y=1.12, x=0))
    return fig


# ==========================================================================
# DASHBOARD
# ==========================================================================
st.title("🔬 " + t("Inteligencia de Color R&D — Robertet", "R&D Colour Intelligence — Robertet"))
tab_p, tab_s, tab_b, tab_r = st.tabs([
    t("🔥 Proceso", "🔥 Process"), t("📅 Anaquel", "📅 Shelf life"),
    t("🧪 Mezclas", "🧪 Blends"), t("💡 Recomendador", "💡 Recommender")])

with tab_p:
    if not dosing:
        st.warning(t("Ningún punto de dosificación activo — no hay color en el producto.",
                     "No dosing point active — there is no colour on the product."))

    def kpis(name, R, label):
        st.markdown(
            f'<div style="background:{PIGMENTS[name]["hue"]};opacity:{max(.12, R["delivered"]/100)};'
            f'height:52px;border-radius:8px;display:flex;align-items:center;justify-content:center;'
            f'color:#fff;font-weight:700;">{label}: {name}</div>', unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric(t("Retención química", "Chemical retention"), f"{R['chem']:.1f}%",
                  help=t("Sobrevive la molécula", "Molecule survives"))
        k2.metric(t("Retención física", "Physical retention"), f"{R['phys']:.1f}%",
                  help=t("Se queda en el producto", "Stays on the product"))
        k3.metric(t("COLOR ENTREGADO", "DELIVERED COLOUR"), f"{R['delivered']:.1f}%",
                  help=t("Lo que ve el consumidor", "What the consumer sees"))

    kpis(p1, R1, "A")
    if compare_on:
        st.markdown("")
        kpis(p2, R2, "B")

    results = [(p1, R1, "solid")] + ([(p2, R2, "dash")] if compare_on else [])
    st.plotly_chart(process_figure(results), width="stretch")

    c1, c2 = st.columns([1.4, 1])
    with c1:
        st.markdown("**" + t("Desglose por punto de dosificación", "Breakdown by dosing point") + "**")
        if R1["breakdown"]:
            st.dataframe(pd.DataFrame([
                {t("Punto", "Point"): APP_POINTS[k]["es"] if ES else APP_POINTS[k]["en"],
                 t("Dosis", "Dose"): f"{v['share']*100:.0f}%",
                 t("Captación", "Uptake"): f"{v['uptake']*100:.0f}%",
                 t("Retención", "Retention"): f"{v['retention']*100:.0f}%",
                 t("Aporta", "Contributes"): f"{v['delivered']:.1f}%"}
                for k, v in R1["breakdown"].items()]), hide_index=True, width="stretch")
        contact = aqueous_contact(stages, "meat")
        st.caption(t(f"Contacto acuoso efectivo calculado: {contact:.0f} min-equivalentes. "
                     "Se deriva de las etapas húmedas activas, su temperatura y agitación.",
                     f"Computed effective aqueous contact: {contact:.0f} min-equivalents. "
                     "Derived from the active wet stages, their temperature and agitation."))
    with c2:
        gap = R1["chem"] - R1["delivered"]
        if not dosing:
            st.info(t("Activa al menos un punto de dosificación.", "Enable at least one dosing point."))
        elif gap > 40:
            st.error(t(f"⚠️ {gap:.0f} puntos se pierden **después** de sobrevivir el proceso. "
                       "El cuello de botella es el punto de aplicación, no la estabilidad térmica.",
                       f"⚠️ {gap:.0f} points are lost **after** surviving the process. "
                       "The bottleneck is the application point, not thermal stability."))
        elif R1["ca"] < 0.9:
            st.warning(t("⚠️ Pérdida por calcio: riesgo de precipitación y moteado.",
                         "⚠️ Calcium loss: precipitation and speckling risk."))
        else:
            st.success(t("✅ Sin cuello de botella evidente.", "✅ No obvious bottleneck."))

    st.caption(t("Captación y retención son estimaciones de ingeniería, no medidas. "
                 "Cuantificarlas es el objeto del Test B del protocolo de Fase 0.",
                 "Uptake and retention are engineering estimates, not measurements. "
                 "Quantifying them is the purpose of Test B in the Phase 0 protocol."))

# ---------------------------------------------------------------- anaquel
with tab_s:
    st.subheader("📅 " + t("Estabilidad en anaquel", "Shelf life stability"))
    st.caption(t("Arranca del color entregado, no del 100%.", "Starts from delivered colour, not 100%."))
    fig2 = go.Figure()
    for name, R, dash in results:
        m, s = shelf_curve(name, months, uv_idx, storage_c, antiox)
        s = s * R["delivered"] / 100.0
        fig2.add_trace(go.Scatter(
            x=m, y=s, mode="lines", name=name,
            line=dict(color=PIGMENTS[name]["hue"], width=3.2, dash=dash),
            hovertemplate="<b>%{fullData.name}</b><br>" + t("Mes", "Month") +
                          " %{x:.1f}<br><b>%{y:.1f}%</b><extra></extra>"))
    fig2.add_hline(y=70, line=dict(color="#888", dash="dot"),
                   annotation_text=t("Umbral aceptable", "Acceptable threshold"))
    fig2.update_layout(height=380, plot_bgcolor="white", hovermode="x unified",
                       margin=dict(l=10, r=40, t=30, b=10),
                       xaxis=dict(title=t("Meses", "Months"), gridcolor="#EEE"),
                       yaxis=dict(title="%", range=[-2, 105], gridcolor="#EEE"),
                       legend=dict(orientation="h", y=1.12, x=0))
    st.plotly_chart(fig2, width="stretch")

    if PIGMENTS[p1]["light"] > 0.12 and uv_idx == 0 and ANTIOX[antiox]["light"] > 0.9:
        st.warning(t("⚠️ Pigmento fotosensible, empaque transparente y sin antioxidante efectivo.",
                     "⚠️ Light-sensitive pigment, clear packaging, no effective antioxidant."))

# ---------------------------------------------------------------- mezclas
with tab_b:
    st.subheader("🧪 " + t("Constructor de mezclas", "Blend builder"))
    st.caption(t("Hasta 5 componentes, cada uno activable. Tono indicativo por mezcla ponderada.",
                 "Up to 5 components, each toggleable. Indicative hue by weighted mixing."))

    defaults = ["Paprika (WD)", "Lycopene", "Caramel colour", "Bixin (annatto oil)", "β-apo-8'-carotenal"]
    slots, cols = [], st.columns(5)
    for i in range(5):
        with cols[i]:
            on = st.toggle(f"#{i+1}", value=(i < 3), key=f"tg_{i}")
            pig = st.selectbox("", pig_list, index=pig_list.index(defaults[i]),
                               key=f"bp_{i}", label_visibility="collapsed", disabled=not on)
            dose = st.slider("%", 0, 100, 40 if i < 3 else 20, 5,
                             key=f"bd_{i}", disabled=not on)
            if on and dose > 0:
                slots.append((pig, dose))

    if slots:
        total = sum(d for _, d in slots)
        rgb, weight, rows = np.zeros(3), 0.0, []
        for name, dose in slots:
            R = full_result(name, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss)
            w = dose / total
            eff = w * R["delivered"] / 100.0
            rgb += np.array(mcolors.to_rgb(PIGMENTS[name]["hue"])) * eff
            weight += eff
            rows.append({t("Pigmento", "Pigment"): name,
                         t("Dosis", "Dose"): f"{w*100:.0f}%",
                         t("Química", "Chemical"): f"{R['chem']:.0f}%",
                         t("Entregado", "Delivered"): f"{R['delivered']:.0f}%",
                         "_d": R["delivered"]})
        if weight > 0:
            hexm = mcolors.to_hex(np.clip(rgb / weight, 0, 1))
            b1, b2 = st.columns([1, 2.2])
            with b1:
                st.markdown(f'<div style="background:{hexm};height:120px;border-radius:10px;'
                            f'border:1px solid #ccc;"></div>', unsafe_allow_html=True)
                st.caption(f"{hexm} · {t('entrega', 'delivery')} {weight*100:.0f}%")
            with b2:
                st.dataframe(pd.DataFrame(rows).drop(columns=["_d"]),
                             hide_index=True, width="stretch")
            worst = min(rows, key=lambda r: r["_d"])
            st.info(t("Componente limitante: ", "Limiting component: ") +
                    f"**{worst[t('Pigmento','Pigment')]}** ({worst['_d']:.0f}%)")
    else:
        st.info(t("Activa al menos un componente.", "Enable at least one component."))

# ---------------------------------------------------------------- recomendador
with tab_r:
    st.subheader("🎯 " + t("Búsqueda por tono", "Target hue search"))
    rc1, rc2 = st.columns([1, 2])
    with rc1:
        target = st.color_picker(t("Color objetivo", "Target colour"), "#C0392B")
        st.markdown(f'<div style="background:{target};height:100px;border-radius:10px;'
                    f'border:1px solid #ccc;"></div>', unsafe_allow_html=True)
    with rc2:
        hue = colorsys.rgb_to_hsv(*mcolors.to_rgb(target))[0] * 360
        ranked = []
        for name, p in PIGMENTS.items():
            hp = colorsys.rgb_to_hsv(*mcolors.to_rgb(p["hue"]))[0] * 360
            dh = min(abs(hue - hp), 360 - abs(hue - hp))
            R = full_result(name, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss)
            ranked.append((R["delivered"] - dh * 1.4, name, dh, R["delivered"]))
        ranked.sort(reverse=True)
        st.markdown("### 🏆 Ranking")
        for _, name, dh, dv in ranked[:5]:
            st.markdown(
                f"<span style='color:{PIGMENTS[name]['hue']};font-size:18px'>"
                f"{'█' * max(1, int(dv / 10))}</span> **{name}** — "
                f"Δ{t('tono','hue')} {dh:.0f}° · {t('entrega','delivery')} {dv:.0f}%",
                unsafe_allow_html=True)
        best = ranked[0]
        if best[3] < 25:
            st.error(t("❌ Ningún pigmento entrega color suficiente con esta dosificación. "
                       "Mover el punto de aplicación antes de cambiar de pigmento.",
                       "❌ No pigment delivers enough colour with this dosing. "
                       "Move the application point before changing pigment."))
        elif best[2] > 25:
            st.warning(t("⚠️ Ningún componente único cubre el tono. Usar mezcla.",
                         "⚠️ No single component covers the hue. Use a blend."))
        else:
            st.success(f"✅ **{best[1]}** — " + t("candidato principal", "lead candidate"))

st.caption("Confidential Robertet R&D — Regional Division.")

