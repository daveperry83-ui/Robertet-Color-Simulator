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

import os
import base64
import streamlit as st
import numpy as np
import pandas as pd
import colorsys
import plotly.graph_objects as go
import matplotlib.colors as mcolors

st.set_page_config(page_title="Robertet R&D Color Intelligence", layout="wide",
                   page_icon="🔬", initial_sidebar_state="expanded")

# ==========================================================================
# IDENTIDAD VISUAL
# ==========================================================================
THEME = dict(
    navy="#0E2439", navy2="#16324B", navy3="#22415E",
    gold="#C1974A", gold_soft="#E4D3AE",
    paper="#FAFAF8", card="#FFFFFF", ink="#161A1F",
    muted="#6B7480", rule="#E3E1DC",
    ok="#2E7D52", warn="#B67514", bad="#A32B2B",
)

# Wordmark de respaldo. Se usa solo si no hay archivo de logo en el repo:
# coloca assets/robertet-logo.png (o .svg) y se toma ese automaticamente.
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 74">
<text x="160" y="34" text-anchor="middle" font-family="Georgia,'Times New Roman',serif"
      font-size="28" letter-spacing="7" fill="{fg}">ROBERTET</text>
<line x1="52" y1="46" x2="268" y2="46" stroke="{accent}" stroke-width="1"/>
<text x="160" y="63" text-anchor="middle" font-family="Helvetica,Arial,sans-serif"
      font-size="9.5" letter-spacing="3.4" fill="{sub}">R&amp;D COLOUR INTELLIGENCE</text>
</svg>"""


def logo_html(width=210, fg="#FFFFFF", accent=None, sub=None):
    """Logo del repo si existe; si no, wordmark vectorial embebido."""
    accent = accent or THEME["gold"]
    sub = sub or THEME["gold_soft"]
    for path in ("assets/robertet-logo.png", "assets/robertet-logo.svg",
                 "assets/logo.png", "robertet-logo.png"):
        if os.path.exists(path):
            mime = "image/svg+xml" if path.endswith(".svg") else "image/png"
            with open(path, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode()
            return f'<img src="data:{mime};base64,{b64}" style="width:{width}px">'
    svg = LOGO_SVG.format(fg=fg, accent=accent, sub=sub)
    b64 = base64.b64encode(svg.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{b64}" style="width:{width}px">'


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

.stApp { background: %(paper)s; }
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: %(navy)s; border-right: 1px solid %(navy3)s; }
[data-testid="stSidebar"] * { color: #E8EDF2; }
[data-testid="stSidebar"] h3 {
  font-size: 12px !important; font-weight: 700; letter-spacing: .13em;
  text-transform: uppercase; color: %(gold)s !important;
  margin: 4px 0 6px; padding-bottom: 5px; border-bottom: 1px solid %(navy3)s;
}
[data-testid="stSidebar"] hr { border-color: %(navy3)s; margin: 14px 0 6px; }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small { font-size: 12px !important; color: #AFC0D0 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] input {
  background: %(navy2)s !important; border-color: %(navy3)s !important;
  color: #F2F5F8 !important; font-size: 13px !important;
}

/* ---------- cabecera ---------- */
.rb-head {
  background: linear-gradient(100deg, %(navy)s 0%%, %(navy2)s 62%%, %(navy3)s 100%%);
  border-radius: 12px; padding: 20px 26px; margin-bottom: 18px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 20px; flex-wrap: wrap;
}
.rb-head h1 {
  color: #fff; font-size: 21px; font-weight: 600; margin: 0; letter-spacing: -.01em;
}
.rb-head .sub {
  color: %(gold_soft)s; font-size: 12px; letter-spacing: .09em;
  text-transform: uppercase; margin-top: 4px;
}
.rb-chip {
  font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: %(gold)s;
  border: 1px solid rgba(193,151,74,.45); border-radius: 30px; padding: 5px 13px;
  white-space: nowrap;
}

/* ---------- tarjetas KPI ---------- */
.rb-kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
@media (max-width: 760px) { .rb-kpis { grid-template-columns: 1fr; } }
.rb-kpi {
  background: %(card)s; border: 1px solid %(rule)s; border-top: 3px solid %(rule)s;
  border-radius: 10px; padding: 14px 16px;
}
.rb-kpi.hero { border-top-color: %(gold)s; }
.rb-kpi .lab {
  font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase;
  color: %(muted)s; font-weight: 600;
}
.rb-kpi .val {
  font-size: 31px; font-weight: 700; color: %(ink)s; line-height: 1.15; margin-top: 3px;
  font-variant-numeric: tabular-nums;
}
.rb-kpi .hint { font-size: 11.5px; color: %(muted)s; margin-top: 2px; }

/* ---------- barra de formulacion ---------- */
.rb-band {
  height: 46px; border-radius: 9px; display: flex; align-items: center;
  justify-content: center; color: #fff; font-weight: 600; letter-spacing: .04em;
  text-shadow: 0 1px 3px rgba(0,0,0,.35); margin-bottom: 12px;
  border: 1px solid rgba(0,0,0,.08);
}

/* ---------- muestras de color ---------- */
.rb-sw { text-align: center; }
.rb-sw .chip {
  height: 84px; border-radius: 9px; border: 1px solid %(rule)s;
  box-shadow: inset 0 1px 4px rgba(0,0,0,.10);
}
.rb-sw .name { font-size: 12px; font-weight: 600; margin-top: 7px; color: %(ink)s; }
.rb-sw .meta {
  font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; color: %(muted)s;
}

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid %(rule)s; }
.stTabs [data-baseweb="tab"] {
  font-size: 13.5px; font-weight: 600; color: %(muted)s;
  padding: 9px 16px; border-radius: 8px 8px 0 0;
}
.stTabs [aria-selected="true"] { color: %(navy)s !important; background: %(card)s; }
.stTabs [data-baseweb="tab-highlight"] { background: %(gold)s; }

/* ---------- tablas y varios ---------- */
[data-testid="stDataFrame"] { border: 1px solid %(rule)s; border-radius: 9px; }
h2, h3 { color: %(navy)s; font-weight: 600; letter-spacing: -.01em; }
.block-container { padding-top: 2.2rem; max-width: 1350px; }
#MainMenu, footer { visibility: hidden; }
</style>
""" % THEME


def kpi(label, value, hint="", hero=False):
    return (f'<div class="rb-kpi{" hero" if hero else ""}">'
            f'<div class="lab">{label}</div><div class="val">{value}</div>'
            f'<div class="hint">{hint}</div></div>')


def plot_layout(fig, height=430, xtitle="", ytitle="%"):
    fig.update_layout(
        height=height, margin=dict(l=8, r=80, t=26, b=8),
        hovermode="x unified", plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color=THEME["ink"]),
        hoverlabel=dict(bgcolor="white", bordercolor=THEME["rule"],
                        font=dict(family="Inter, sans-serif", size=12)),
        xaxis=dict(title=xtitle, showspikes=True, spikemode="across", spikethickness=1,
                   spikecolor=THEME["muted"], gridcolor="#F0EFEC",
                   linecolor=THEME["rule"], zeroline=False),
        yaxis=dict(title=ytitle, range=[-2, 105], gridcolor="#F0EFEC",
                   linecolor=THEME["rule"], zeroline=False),
        legend=dict(orientation="h", y=1.14, x=0, bgcolor="rgba(0,0,0,0)",
                    font=dict(size=11.5)))
    return fig


st.markdown(CSS, unsafe_allow_html=True)


# ==========================================================================
# ACCESO
# ==========================================================================
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False

if not st.session_state.acceso_concedido:
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        st.markdown(
            f'<div style="background:{THEME["navy"]};border-radius:14px;'
            f'padding:36px 30px 30px;text-align:center;margin-top:44px">'
            f'{logo_html(240)}'
            f'<div style="color:{THEME["gold_soft"]};font-size:11px;letter-spacing:.16em;'
            f'margin-top:20px">R&D PORTAL &middot; LATIN AMERICA</div></div>',
            unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
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
# ts ...... fuerza colorante relativa del PREPARADO COMERCIAL, índice con el
#           blend Red 40 + Yellow 6 = 100. Refleja color por gramo de producto
#           tal como se compra, no por gramo de pigmento puro: por eso una
#           oleorresina de páprika al 40.000 CU vale ~12 y el carmín al 50% de
#           ácido carmínico vale ~35. Son ordenes de magnitud, no valores
#           certificados — sustituir por la ficha técnica real de cada SKU.
# ==========================================================================
PIGMENTS = {
    "Paprika (WD)":        dict(k85=.0030, pol="oil",   o2=1.20, ca=1.00, light=.075, bind=None, ts=12, hue="#E63900", ph=(2, 9), pen=1.0),
    "Paprika (oil)":       dict(k85=.0026, pol="oil",   o2=1.10, ca=1.00, light=.070, bind=None, ts=28, hue="#DA3A0E", ph=(2, 9), pen=1.0),
    "Lycopene":            dict(k85=.0042, pol="oil",   o2=1.85, ca=1.00, light=.140, bind=None, ts=8, hue="#C6362B", ph=(2, 9), pen=1.0),
    "Bixin (annatto oil)": dict(k85=.0022, pol="oil",   o2=1.15, ca=1.00, light=.090, bind=None, ts=10, hue="#E28313", ph=(2, 9), pen=1.0),
    "Norbixin (annatto)":  dict(k85=.0050, pol="water", o2=1.10, ca=0.15, light=.095, bind=None, ts=9, hue="#D2691E", ph=(4.5, 9), pen=6.0),
    "Beta-carotene":       dict(k85=.0010, pol="oil",   o2=1.45, ca=1.00, light=.110, bind=None, ts=20, hue="#FFB300", ph=(2, 9), pen=1.0),
    "β-apo-8'-carotenal":  dict(k85=.0016, pol="oil",   o2=1.40, ca=1.00, light=.105, bind=None, ts=22, hue="#E8541F", ph=(2, 9), pen=1.0),
    "Caramel colour":      dict(k85=.0002, pol="water", o2=0.10, ca=1.00, light=.010, bind=None, ts=3, hue="#7A4A21", ph=(2, 9), pen=1.0),
    "Carmine":             dict(k85=.0008, pol="water", o2=0.30, ca=0.75, light=.030, bind=0.93, ts=35, hue="#8E1F2F", ph=(3.5, 8), pen=2.5),
    "Red 40 + Yellow 6":   dict(k85=.0003, pol="water", o2=0.15, ca=1.00, light=.020, bind=0.95, ts=100, hue="#D62828", ph=(2, 9), pen=1.0),
    "Curcumin":            dict(k85=.0100, pol="both",  o2=1.00, ca=1.00, light=.320, bind=None, ts=40, hue="#FFEA00", ph=(2, 7.5), pen=2.0),
    "Red Beet":            dict(k85=.0400, pol="water", o2=1.30, ca=1.00, light=.180, bind=None, ts=4, hue="#C71585", ph=(4, 6), pen=2.0),
    "Natural Chlorophyll": dict(k85=.0150, pol="oil",   o2=1.20, ca=0.85, light=.250, bind=None, ts=6, hue="#228B22", ph=(6, 9), pen=3.0),
    "Spirulina":           dict(k85=.1500, pol="water", o2=1.60, ca=1.00, light=.400, bind=None, ts=5, hue="#4169E1", ph=(5.5, 7.5), pen=3.0),
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
    t("Cárnico coextruido en alginato", "Alginate co-extruded meat"): [
        (t("Fijado Ca²⁺", "Ca²⁺ setting"),   20, 2,  0.8, True,  0.3),
        (t("Cocción en agua", "Water cook"), 82, 15, 1.0, True,  0.5),
        (t("Horno seco", "Dry oven"),        70, 20, 1.6, False, 0.0),
        (t("Enfriado en agua", "Water chill"), 7, 20, 0.9, True,  0.6),
    ],
    t("Cárnico en tripa natural", "Natural casing meat"): [
        (t("Cocción en agua", "Water cook"), 78, 25, 1.0, True,  0.4),
        (t("Enfriado en agua", "Water chill"), 5, 15, 0.9, True,  0.5),
    ],
    t("Pasteurización simple", "Simple pasteurisation"): [
        (t("Pasteurización", "Pasteurisation"), 72, 15, 1.0, True, 0.4)],
    t("Esterilización UHT", "UHT sterilisation"): [
        ("UHT", 140, 1, 0.7, True, 0.5)],
    t("Horneado", "Baking"): [
        (t("Horneado", "Baking"), 180, 25, 1.8, False, 0.0)],
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
# COLORIMETRÍA — sRGB → CIELAB y CIEDE2000
# ==========================================================================
SUBSTRATE = "#8C6A5D"   # carne emulsionada cocida: fondo gris-pardo, no blanco


def srgb_to_lab(hex_color):
    r, g, b = mcolors.to_rgb(hex_color)

    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    x = r * .4124564 + g * .3575761 + b * .1804375
    y = r * .2126729 + g * .7151522 + b * .0721750
    z = r * .0193339 + g * .1191920 + b * .9503041
    xn, yn, zn = .95047, 1.0, 1.08883

    def f(u):
        return u ** (1 / 3) if u > .008856 else (7.787 * u + 16 / 116)

    fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def ciede2000(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    kL = kC = kH = 1.0
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7))) if Cb > 0 else 0.5
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360 if (a2p or b2) else 0.0

    dLp = L2 - L1
    dCp = C2p - C1p
    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dhp) / 2)

    Lbp = (L1 + L2) / 2
    Cbp = (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbp = (h1p + h2p + 360) / 2
    else:
        hbp = (h1p + h2p - 360) / 2

    T = (1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp))
         + 0.32 * np.cos(np.radians(3 * hbp + 6)) - 0.20 * np.cos(np.radians(4 * hbp - 63)))
    dTheta = 30 * np.exp(-(((hbp - 275) / 25) ** 2))
    Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) if Cbp > 0 else 0.0
    Sl = 1 + (0.015 * (Lbp - 50) ** 2) / np.sqrt(20 + (Lbp - 50) ** 2)
    Sc = 1 + 0.045 * Cbp
    Sh = 1 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dTheta)) * Rc

    return float(np.sqrt((dLp / (kL * Sl)) ** 2 + (dCp / (kC * Sc)) ** 2 +
                         (dHp / (kH * Sh)) ** 2 +
                         Rt * (dCp / (kC * Sc)) * (dHp / (kH * Sh))))


def on_substrate(hex_color, delivered_pct, substrate=SUBSTRATE):
    """Cómo se ve ese tono realmente sobre carne cocida, a la intensidad entregada."""
    alpha = min(max(delivered_pct / 100.0, 0.0), 1.0)
    fg = np.array(mcolors.to_rgb(hex_color))
    bg = np.array(mcolors.to_rgb(substrate))
    return mcolors.to_hex(np.clip(bg * (1 - alpha) + fg * alpha, 0, 1))


def swatch(hex_color, label, sub=""):
    return (f'<div class="rb-sw"><div class="chip" style="background:{hex_color}"></div>'
            f'<div class="name">{label}</div><div class="meta">{sub}</div></div>')



# ==========================================================================
# MEZCLA — la formulación es el objeto principal, no un pigmento suelto
# ==========================================================================
def blend_result(components, stages, ph, ax, ca_pct, ca_on, dosing, cook_loss):
    """
    components: lista de (nombre, participación 0-1) ya normalizada.
    Una sola componente al 100% es un 'single'; la matemática es la misma.
    """
    if not components:
        return None
    parts, ys, chem, delivered = [], None, 0.0, 0.0
    rgb, weight = np.zeros(3), 0.0
    for name, share in components:
        R = full_result(name, stages, ph, ax, ca_pct, ca_on, dosing, cook_loss)
        parts.append((name, share, R))
        ys = share * R["ys"] if ys is None else ys + share * R["ys"]
        chem += share * R["chem"]
        delivered += share * R["delivered"]
        eff = share * R["delivered"] / 100.0
        rgb += np.array(mcolors.to_rgb(PIGMENTS[name]["hue"])) * eff
        weight += eff
    hexm = mcolors.to_hex(np.clip(rgb / weight, 0, 1)) if weight > 0 else "#999999"
    phys = (delivered / chem * 100.0) if chem > 0 else 0.0
    return dict(parts=parts, ts=parts[0][2]["ts"], ys=ys, bounds=parts[0][2]["bounds"],
                chem=chem, phys=phys, delivered=delivered, hex=hexm,
                ca=parts[0][2]["ca"], single=(len(parts) == 1))



def combo_metrics(components, cache, ref_sub):
    """Tono, entrega y ΔE₀₀ de una combinación, a partir de resultados ya calculados."""
    delivered, rgb, weight = 0.0, np.zeros(3), 0.0
    for name, share in components:
        d = cache[name]["delivered"]
        delivered += share * d
        eff = share * d / 100.0
        rgb += np.array(mcolors.to_rgb(PIGMENTS[name]["hue"])) * eff
        weight += eff
    if weight <= 0:
        return None
    hexm = mcolors.to_hex(np.clip(rgb / weight, 0, 1))
    sub = on_substrate(hexm, delivered)
    return dict(components=components, delivered=delivered, hex=hexm, sub=sub,
                dE=ciede2000(srgb_to_lab(ref_sub), srgb_to_lab(sub)))


def suggest_alternative(ref_sub, cache, exclude_ref, min_delivered=25.0, min_chem=60.0):
    """
    Busca la formulación que más se acerca al color de referencia.
    Explora componentes sueltos, pares y tríos sobre el catálogo disponible.

    Filtro de viabilidad (min_chem): se excluyen pigmentos cuya retención química
    cae por debajo del umbral en este proceso. El modelo trata la degradación como
    pérdida de intensidad a tono constante, y eso deja de ser cierto cuando el
    pigmento se destruye: las betalaínas viran a pardo y las antocianinas a
    azul-violeta. Sin este filtro el optimizador recomienda pigmentos muertos
    porque su tono nominal mejora la mezcla en el papel.
    """
    pool = [n for n in cache
            if n != exclude_ref and cache[n]["chem"] >= min_chem]
    best = []

    for n in pool:                                          # sueltos
        r = combo_metrics([(n, 1.0)], cache, ref_sub)
        if r and r["delivered"] >= min_delivered:
            best.append(r)

    for i, a in enumerate(pool):                            # pares
        for b in pool[i + 1:]:
            for w in range(10, 100, 10):
                r = combo_metrics([(a, w / 100), (b, 1 - w / 100)], cache, ref_sub)
                if r and r["delivered"] >= min_delivered:
                    best.append(r)

    top = sorted(pool, key=lambda n: -cache[n]["delivered"])[:6]
    for i, a in enumerate(top):                             # tríos
        for j, b in enumerate(top[i + 1:], i + 1):
            for c in top[j + 1:]:
                for wa in (20, 40, 60):
                    for wb in (20, 40, 60):
                        if wa + wb >= 100:
                            continue
                        r = combo_metrics(
                            [(a, wa / 100), (b, wb / 100), (c, (100 - wa - wb) / 100)],
                            cache, ref_sub)
                        if r and r["delivered"] >= min_delivered:
                            best.append(r)

    if not best:
        return None
    best.sort(key=lambda r: (round(r["dE"], 2), -r["delivered"]))
    return best[0]



def dose_estimate(components, cache, ref_name, ref_dose_ppm, ref_dosing_result):
    """
    Dosis requerida para igualar el color que entrega el sistema de referencia.

    Se ancla al incumbente en vez de calcular en absoluto, porque la fuerza
    colorante absoluta depende del SKU y del método de medición. Igualando
    color entregado:

        D_total · Σ(share_i · TS_i · entrega_i) = dosis_ref · TS_ref · entrega_ref

    Devuelve None si la formulación no entrega color (denominador nulo).
    """
    denom = sum(s * PIGMENTS[n]["ts"] * cache[n]["delivered"] for n, s in components)
    if denom <= 0:
        return None
    numer = ref_dose_ppm * PIGMENTS[ref_name]["ts"] * ref_dosing_result["delivered"]
    total = numer / denom
    return dict(total_ppm=total,
                rows=[(n, s, total * s) for n, s in components])


def result_card(title, subtitle, sub_hex, pure_hex, composition,
                dE, delivered, perf, accent, tag=""):
    """Tarjeta comparativa: muestra sobre producto + tono puro + métricas."""
    dE_txt = "—" if dE is None else f"{dE:.1f}"
    perf_txt = "—" if perf is None else f"{perf:.0f}%"
    chip = (f'<span style="font-size:9.5px;letter-spacing:.1em;padding:2px 8px;'
            f'border-radius:20px;background:{accent};color:#fff">{tag}</span>'
            if tag else "")
    return f'''
<div style="border:1px solid {THEME["rule"]};border-top:3px solid {accent};
            border-radius:10px;padding:14px 15px;background:#fff;height:100%">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:8px">
    <div style="font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
                color:{THEME["muted"]};font-weight:600">{title}</div>{chip}
  </div>
  <div style="font-size:13.5px;font-weight:600;color:{THEME["ink"]};margin:3px 0 9px">
    {subtitle}</div>
  <div style="height:72px;border-radius:8px;background:{sub_hex};
              border:1px solid {THEME["rule"]};box-shadow:inset 0 1px 4px rgba(0,0,0,.10)"></div>
  <div style="display:flex;gap:6px;align-items:center;margin-top:6px">
    <div style="width:20px;height:14px;border-radius:3px;background:{pure_hex};
                border:1px solid {THEME["rule"]}"></div>
    <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                 color:{THEME["muted"]}">{pure_hex}</span>
  </div>
  <div style="font-size:11.5px;color:{THEME["muted"]};margin:9px 0 11px;
              line-height:1.45;min-height:32px">{composition}</div>
  <div style="display:flex;gap:14px;border-top:1px solid {THEME["rule"]};padding-top:9px">
    <div><div style="font-size:9.5px;letter-spacing:.08em;color:{THEME["muted"]}">ΔE₀₀</div>
      <div style="font-size:19px;font-weight:700;color:{THEME["ink"]}">{dE_txt}</div></div>
    <div><div style="font-size:9.5px;letter-spacing:.08em;color:{THEME["muted"]}">
      {t("ENTREGA", "DELIVERY")}</div>
      <div style="font-size:19px;font-weight:700;color:{THEME["ink"]}">{delivered:.0f}%</div></div>
    <div><div style="font-size:9.5px;letter-spacing:.08em;color:{THEME["muted"]}">
      {t("VS REF", "VS REF")}</div>
      <div style="font-size:19px;font-weight:700;color:{accent}">{perf_txt}</div></div>
  </div>
</div>'''


# ==========================================================================
# BARRA LATERAL
# ==========================================================================
st.sidebar.markdown(f'<div style="padding:2px 0 14px">{logo_html(190)}</div>',
                    unsafe_allow_html=True)
pig_list = list(PIGMENTS.keys())

# ---------------------------------------------------------------- formulación
st.sidebar.markdown("### 🧪 " + t("Formulación", "Formulation"))
st.sidebar.caption(t("Hasta 5 componentes. Apaga los que no uses — con uno solo activo "
                     "es un pigmento único.",
                     "Up to 5 components. Switch off what you don't use — with a single "
                     "one active it is a straight pigment."))

DEFAULTS = ["Lycopene", "Paprika (WD)", "Caramel colour",
            "Bixin (annatto oil)", "β-apo-8'-carotenal"]
DEF_ON = [True, True, True, False, False]
DEF_DOSE = [60, 20, 15, 5, 10]

raw_components = []
for i in range(5):
    with st.sidebar.container():
        c_tg, c_ds = st.sidebar.columns([1, 1])
        on = c_tg.toggle(f"#{i+1}", value=DEF_ON[i], key=f"tg_{i}")
        dose = c_ds.number_input("%", 0, 100, DEF_DOSE[i], 5,
                                 key=f"bd_{i}", disabled=not on,
                                 label_visibility="collapsed")
        pig = st.sidebar.selectbox(f"{t('Componente','Component')} {i+1}", pig_list,
                                   index=pig_list.index(DEFAULTS[i]),
                                   key=f"bp_{i}", label_visibility="collapsed",
                                   disabled=not on)
    if on and dose > 0:
        raw_components.append((pig, dose))

tot_dose = sum(d for _, d in raw_components)
components = [(n, d / tot_dose) for n, d in raw_components] if tot_dose else []
if len(components) > 1:
    st.sidebar.caption(t(f"Normalizado sobre {tot_dose}%.", f"Normalised over {tot_dose}%."))

# ---------------------------------------------------------------- proceso
st.sidebar.markdown("--- \n### ⚙️ " + t("Proceso", "Process"))
preset = st.sidebar.selectbox(t("Preset", "Preset"), list(PRESETS.keys()))
st.sidebar.caption(t("Etapas activables.", "Toggleable stages."))
raw_stages = PRESETS[preset]
active_flags = [st.sidebar.checkbox(f"{s[0]} · {s[1]}°C · {s[2]}min", value=True,
                                    key=f"stg_{preset}_{i}")
                for i, s in enumerate(raw_stages)]

COLS = ["Etapa", "TempC", "Minutos", "O2", "Humeda", "Agitacion"]
df = pd.DataFrame([dict(zip(COLS, s)) for s, a in zip(raw_stages, active_flags) if a],
                  columns=COLS)

with st.sidebar.expander(t("Editar etapas", "Edit stages")):
    if df.empty:
        st.caption(t("Ninguna etapa activa.", "No active stage."))
    else:
        df = st.data_editor(df, hide_index=True, num_rows="fixed",
                            key=f"ed_{preset}", use_container_width=True)

stages = []
for row in df.to_dict("records"):
    try:
        vals = [float(row[c]) for c in ["TempC", "Minutos", "O2", "Agitacion"]]
        if any(np.isnan(v) for v in vals):
            raise ValueError("NaN")
        tc, mn, o2, agit = vals
        stages.append((str(row["Etapa"]), tc, max(mn, 0.0), max(o2, 0.0),
                       bool(row["Humeda"]), min(max(agit, 0.0), 1.0)))
    except (TypeError, ValueError):
        st.sidebar.warning(t(f"Etapa '{row.get('Etapa','?')}' invalida, omitida.",
                             f"Stage '{row.get('Etapa','?')}' invalid, skipped."))

if not stages:
    st.sidebar.error(t("Sin etapas activas.", "No active stages."))
    st.stop()

# ---------------------------------------------------------------- dosificación
POINT_COLOR = {"bath": "#4A90D9", "gel": "#3E9E8F", "meat": "#C1974A"}

st.sidebar.markdown("--- \n### 🎯 " + t("Punto de aplicación", "Application point"))
st.sidebar.caption(t("**Dónde** se agrega el color en el proceso. No es la receta: "
                     "eso se define arriba, en Formulación.",
                     "**Where** the colour is added in the process. Not the recipe: "
                     "that is set above, in Formulation."))

dosing_raw = {}
for key, ap in APP_POINTS.items():
    name = ap["es"] if ES else ap["en"]
    on = st.sidebar.checkbox(name, value=(key == "meat"), key=f"ap_{key}")
    if on:
        dosing_raw[key] = st.sidebar.slider(
            t(f"Reparto — {name}", f"Split — {name}"), 0, 100, 100, 5, key=f"sh_{key}")

tot = sum(dosing_raw.values())
dosing = {k: v / tot for k, v in dosing_raw.items()} if tot > 0 else {}

# Resumen visual: el slider es un peso relativo, no un porcentaje absoluto.
# Sin esto, dos sliders en 100 parecen 200% cuando en realidad son 50/50.
if dosing:
    if len(dosing) == 1:
        only = list(dosing)[0]
        st.sidebar.markdown(
            f'<div style="background:{POINT_COLOR[only]};height:9px;border-radius:5px;'
            f'margin:8px 0 6px"></div>'
            f'<div style="font-size:11.5px;color:#AFC0D0">'
            f'{t("Todo el color en", "All colour in")} '
            f'<b style="color:#F2F5F8">{APP_POINTS[only]["es"] if ES else APP_POINTS[only]["en"]}</b>'
            f'</div>', unsafe_allow_html=True)
    else:
        bar = "".join(
            f'<div style="width:{v*100:.1f}%;background:{POINT_COLOR[k]};height:100%"></div>'
            for k, v in dosing.items())
        rows = "".join(
            f'<div style="display:flex;align-items:center;gap:7px;margin-top:4px">'
            f'<span style="width:9px;height:9px;border-radius:2px;flex:0 0 auto;'
            f'background:{POINT_COLOR[k]}"></span>'
            f'<span style="flex:1;font-size:11.5px;color:#AFC0D0">'
            f'{APP_POINTS[k]["es"] if ES else APP_POINTS[k]["en"]}</span>'
            f'<b style="font-size:11.5px;color:#F2F5F8">{v*100:.0f}%</b></div>'
            for k, v in dosing.items())
        st.sidebar.markdown(
            f'<div style="display:flex;height:9px;border-radius:5px;overflow:hidden;'
            f'margin:8px 0 2px">{bar}</div>{rows}'
            f'<div style="font-size:10.5px;color:#8FA3B5;margin-top:7px;line-height:1.4">'
            f'{t("Los sliders son pesos relativos: se normalizan sobre su suma "
                 f"({tot}%). Estos son los valores efectivos.",
                 f"Sliders are relative weights, normalised over their sum ({tot}%). "
                 "These are the effective values.")}</div>',
            unsafe_allow_html=True)
else:
    st.sidebar.warning(t("Ningún punto activo: el producto no recibe color.",
                         "No active point: the product receives no colour."))

# ---------------------------------------------------------------- condiciones
st.sidebar.markdown("--- \n### 🔬 " + t("Condiciones", "Conditions"))
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

B = blend_result(components, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss)

# ==========================================================================
# DASHBOARD
# ==========================================================================
st.markdown(
    f'<div class="rb-head"><div style="display:flex;align-items:center;gap:22px">'
    f'{logo_html(170)}'
    f'<div><h1>{t("Inteligencia de Color", "Colour Intelligence")}</h1>'
    f'<div class="sub">{t("Simulador de proceso y anaquel", "Process &amp; shelf life simulator")}</div>'
    f'</div></div>'
    f'<div class="rb-chip">{preset} &middot; {sum(s[2] for s in stages):.0f} min</div>'
    f'</div>', unsafe_allow_html=True)

if B is None:
    st.warning(t("No hay componentes activos. Enciende al menos uno en la barra lateral.",
                 "No active components. Switch on at least one in the sidebar."))
    st.stop()

tab_p, tab_s, tab_b, tab_d, tab_r = st.tabs([
    t("🔥 Proceso", "🔥 Process"), t("📅 Anaquel", "📅 Shelf life"),
    t("🧪 Formulación", "🧪 Formulation"), t("⚖️ Dosis", "⚖️ Dosage"),
    t("💡 Recomendador", "💡 Recommender")])

# ---------------------------------------------------------------- proceso
with tab_p:
    if not dosing:
        st.warning(t("Ningún punto de dosificación activo — no hay color en el producto.",
                     "No dosing point active — there is no colour on the product."))

    title = (B["parts"][0][0] if B["single"]
             else t("Mezcla de ", "Blend of ") + f"{len(B['parts'])}")
    st.markdown(f'<div class="rb-band" style="background:{B["hex"]}">{title}</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="rb-kpis">'
        + kpi(t("Retención química", "Chemical retention"), f"{B['chem']:.1f}%",
              t("Sobrevive la molécula", "Molecule survives"))
        + kpi(t("Retención física", "Physical retention"), f"{B['phys']:.1f}%",
              t("Se queda en el producto", "Stays on the product"))
        + kpi(t("Color entregado", "Delivered colour"), f"{B['delivered']:.1f}%",
              t("Lo que ve el consumidor", "What the consumer sees"), hero=True)
        + '</div><div style="height:16px"></div>', unsafe_allow_html=True)

    fig = go.Figure()
    for start, end, label, tc, wet in B["bounds"]:
        fig.add_vrect(x0=start, x1=end,
                      fillcolor="#4A90D9" if wet else "#E8A33D",
                      opacity=0.09, layer="below", line_width=0,
                      annotation_text=f"{label}<br>{tc:.0f}°C",
                      annotation_position="top left",
                      annotation_font_size=9, annotation_font_color="#666")
    if not B["single"]:
        for name, share, R in B["parts"]:
            fig.add_trace(go.Scatter(
                x=R["ts"], y=R["ys"], mode="lines",
                name=f"{name} ({share*100:.0f}%)",
                line=dict(color=PIGMENTS[name]["hue"], width=1.8, dash="dot"),
                hovertemplate="<b>%{fullData.name}</b><br>%{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=B["ts"], y=B["ys"], mode="lines",
        name=t("Formulación", "Formulation") if not B["single"] else B["parts"][0][0],
        line=dict(color=B["hex"], width=4),
        hovertemplate="<b>%{fullData.name}</b><br>" + t("Minuto", "Minute") +
                      " %{x:.1f}<br>" + t("Retención química", "Chemical retention") +
                      " <b>%{y:.1f}%</b><extra></extra>"))
    fig.add_hline(y=B["delivered"], line=dict(color=B["hex"], width=1.8, dash="dot"),
                  annotation_text=t("entregado ", "delivered ") + f"{B['delivered']:.0f}%",
                  annotation_position="right", annotation_font_size=10)
    st.plotly_chart(plot_layout(fig, 430, t("Tiempo (min)", "Time (min)")),
                    use_container_width=True)

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("**" + t("Aporte por componente", "Contribution by component") + "**")
        st.dataframe(pd.DataFrame([
            {t("Componente", "Component"): n,
             t("Dosis", "Dose"): f"{s*100:.0f}%",
             t("Química", "Chemical"): f"{R['chem']:.0f}%",
             t("Entregado", "Delivered"): f"{R['delivered']:.0f}%",
             t("Aporta", "Contributes"): f"{s*R['delivered']:.1f}%"}
            for n, s, R in B["parts"]]), hide_index=True, use_container_width=True)

        first = B["parts"][0][2]
        if first["breakdown"]:
            st.markdown("**" + t("Por punto de dosificación", "By dosing point") + "**")
            st.dataframe(pd.DataFrame([
                {t("Punto", "Point"): APP_POINTS[k]["es"] if ES else APP_POINTS[k]["en"],
                 t("Dosis", "Dose"): f"{v['share']*100:.0f}%",
                 t("Captación", "Uptake"): f"{v['uptake']*100:.0f}%",
                 t("Retención", "Retention"): f"{v['retention']*100:.0f}%"}
                for k, v in first["breakdown"].items()]),
                hide_index=True, use_container_width=True)
        st.caption(t(f"Contacto acuoso calculado: {aqueous_contact(stages,'meat'):.0f} min-eq.",
                     f"Computed aqueous contact: {aqueous_contact(stages,'meat'):.0f} min-eq."))
    with c2:
        gap = B["chem"] - B["delivered"]
        worst = min(B["parts"], key=lambda x: x[2]["delivered"])
        if not dosing:
            st.info(t("Activa un punto de dosificación.", "Enable a dosing point."))
        elif gap > 40:
            st.error(t(f"⚠️ {gap:.0f} puntos se pierden **después** de sobrevivir el proceso. "
                       "El cuello de botella es el punto de aplicación.",
                       f"⚠️ {gap:.0f} points lost **after** surviving the process. "
                       "The bottleneck is the application point."))
        elif B["ca"] < 0.9:
            st.warning(t("⚠️ Pérdida por calcio: riesgo de precipitación.",
                         "⚠️ Calcium loss: precipitation risk."))
        else:
            st.success(t("✅ Sin cuello de botella evidente.", "✅ No obvious bottleneck."))
        if not B["single"]:
            st.info(t("Componente limitante: ", "Limiting component: ") +
                    f"**{worst[0]}** ({worst[2]['delivered']:.0f}%)")

    st.caption(t("Captación y retención son estimaciones de ingeniería, no medidas. "
                 "Cuantificarlas es el objeto del Test B del protocolo de Fase 0.",
                 "Uptake and retention are engineering estimates, not measurements."))

# ---------------------------------------------------------------- anaquel
with tab_s:
    st.subheader("📅 " + t("Estabilidad en anaquel", "Shelf life stability"))
    st.caption(t("Arranca del color entregado, no del 100%.",
                 "Starts from delivered colour, not 100%."))
    fig2 = go.Figure()
    m_ref, blend_shelf = None, None
    for name, share, R in B["parts"]:
        m, s = shelf_curve(name, months, uv_idx, storage_c, antiox)
        s = s * R["delivered"] / 100.0
        m_ref = m
        blend_shelf = share * s if blend_shelf is None else blend_shelf + share * s
        if not B["single"]:
            fig2.add_trace(go.Scatter(
                x=m, y=s, mode="lines", name=f"{name} ({share*100:.0f}%)",
                line=dict(color=PIGMENTS[name]["hue"], width=1.8, dash="dot"),
                hovertemplate="<b>%{fullData.name}</b><br>%{y:.1f}%<extra></extra>"))
    fig2.add_trace(go.Scatter(
        x=m_ref, y=blend_shelf, mode="lines",
        name=t("Formulación", "Formulation") if not B["single"] else B["parts"][0][0],
        line=dict(color=B["hex"], width=4),
        hovertemplate="<b>%{fullData.name}</b><br>" + t("Mes", "Month") +
                      " %{x:.1f}<br><b>%{y:.1f}%</b><extra></extra>"))
    fig2.add_hline(y=70, line=dict(color="#888", dash="dot"),
                   annotation_text=t("Umbral aceptable", "Acceptable threshold"))
    st.plotly_chart(plot_layout(fig2, 390, t("Meses", "Months")), use_container_width=True)
    st.markdown('<div class="rb-kpis">'
                + kpi(t("Al final del anaquel", "At end of shelf life"),
                      f"{blend_shelf[-1]:.1f}%",
                      t(f"a {months} meses", f"at {months} months"), hero=True)
                + kpi(t("Al salir de proceso", "Leaving the process"),
                      f"{B['delivered']:.1f}%", t("punto de partida", "starting point"))
                + kpi(t("Pérdida en anaquel", "Shelf life loss"),
                      f"{B['delivered'] - blend_shelf[-1]:.1f} pts",
                      t("luz y temperatura", "light and temperature"))
                + '</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- formulación
with tab_b:
    st.subheader("🧪 " + t("Formulación", "Formulation"))
    st.caption(t("Los componentes se encienden y apagan en la barra lateral. "
                 "Tono indicativo por mezcla ponderada, no sustituye matching espectrofotométrico.",
                 "Components are toggled in the sidebar. Indicative hue by weighted mixing."))
    f1, f2 = st.columns([1, 2.2])
    with f1:
        st.markdown(swatch(B["hex"], t("Tono puro", "Pure hue"), B["hex"]),
                    unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown(swatch(on_substrate(B["hex"], B["delivered"]),
                           t("Sobre producto", "On product"),
                           t("entrega ", "delivery ") + f"{B['delivered']:.0f}%"),
                    unsafe_allow_html=True)
    with f2:
        st.dataframe(pd.DataFrame([
            {t("Componente", "Component"): n,
             t("Dosis", "Dose"): f"{s*100:.0f}%",
             t("Tono", "Hue"): PIGMENTS[n]["hue"],
             t("Química", "Chemical"): f"{R['chem']:.0f}%",
             t("Entregado", "Delivered"): f"{R['delivered']:.0f}%"}
            for n, s, R in B["parts"]]), hide_index=True, use_container_width=True)
        cols = st.columns(len(B["parts"]))
        for col, (n, s, R) in zip(cols, B["parts"]):
            col.markdown(swatch(PIGMENTS[n]["hue"], n.split(" (")[0], f"{s*100:.0f}%"),
                         unsafe_allow_html=True)

# ---------------------------------------------------------------- recomendador
# ---------------------------------------------------------------- dosis
with tab_d:
    st.subheader("⚖️ " + t("Dosis estimada y costo en uso", "Estimated dose and cost in use"))
    st.caption(t("La dosis se calcula por equivalencia con el sistema sintético: cuánto "
                 "colorante natural hace falta para entregar el mismo color que el "
                 "incumbente entrega en este proceso.",
                 "Dose is computed by equivalence with the synthetic system: how much natural "
                 "colour is needed to deliver the same colour the incumbent delivers in this "
                 "process."))

    REF_D = "Red 40 + Yellow 6"
    d1, d2, d3 = st.columns(3)
    ref_dose = d1.number_input(t("Dosis del sintético (ppm)", "Synthetic dose (ppm)"),
                               1, 2000, 60, 5,
                               help=t("Sobre producto terminado. Pídelo al cliente.",
                                      "On finished product. Ask the customer."))
    ref_point = d2.selectbox(t("Dosificado en", "Dosed in"), list(APP_POINTS.keys()),
                             format_func=lambda k: APP_POINTS[k]["es"] if ES else APP_POINTS[k]["en"],
                             index=0)
    batch = d3.number_input(t("Lote (kg)", "Batch (kg)"), 1, 100000, 1000, 100)

    Rref_d = full_result(REF_D, stages, ph_val, antiox, ca_pct, ca_on,
                         {ref_point: 1.0}, cook_loss)
    cache_d = {n: full_result(n, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss)
               for n in {c[0] for c in [(p[0], 0) for p in B["parts"]]}}
    est = dose_estimate([(n, s) for n, s, _ in B["parts"]], cache_d, REF_D, ref_dose, Rref_d)

    # Techo práctico: por encima de ~0.5% sobre producto no hay dosis que sea
    # formulable ni sensorialmente neutra. El cálculo sigue siendo aritméticamente
    # correcto, pero devolver "48 000 ppm" invita a leerlo como una dosis real.
    MAX_PPM = 5000.0

    if est is None:
        st.warning(t("La formulación no entrega color en esta configuración: no hay dosis "
                     "que iguale la referencia.",
                     "The formulation delivers no colour in this configuration: no dose can "
                     "match the reference."))
    elif est["total_ppm"] > MAX_PPM:
        st.error(t(f"❌ Igualar la referencia exigiría {est['total_ppm']:,.0f} ppm "
                   f"({est['total_ppm']/10000:.2f}% sobre producto). No es formulable: "
                   "por encima de ~0,5% el colorante deja de ser un aditivo y se vuelve un "
                   "ingrediente, con impacto en sabor, textura y costo. Esta configuración "
                   "no tiene solución por dosis — hay que cambiar el punto de aplicación.",
                   f"❌ Matching the reference would require {est['total_ppm']:,.0f} ppm "
                   f"({est['total_ppm']/10000:.2f}% on product). Not formulable: above ~0.5% "
                   "the colour stops being an additive and becomes an ingredient, with impact "
                   "on flavour, texture and cost. This configuration has no dose-based "
                   "solution — the application point must change.").replace(",", " "))
    else:
        ratio = est["total_ppm"] / ref_dose
        st.markdown('<div class="rb-kpis">'
                    + kpi(t("Dosis total", "Total dose"), f"{est['total_ppm']:.0f} ppm",
                          t("sobre producto terminado", "on finished product"), hero=True)
                    + kpi(t("Por lote", "Per batch"),
                          f"{est['total_ppm']*batch/1000:.0f} g",
                          f"{batch:,} kg".replace(",", " "))
                    + kpi(t("Factor vs. sintético", "Factor vs. synthetic"), f"{ratio:.1f}×",
                          t("gramos por gramo sustituido", "grams per gram replaced"))
                    + '</div><div style="height:16px"></div>', unsafe_allow_html=True)

        st.markdown("**" + t("Desglose por componente", "Breakdown by component") + "**")
        table = pd.DataFrame([
            {t("Componente", "Component"): n,
             t("Reparto", "Share"): f"{s*100:.0f}%",
             t("Fuerza", "Strength"): PIGMENTS[n]["ts"],
             t("Entrega", "Delivery"): f"{cache_d[n]['delivered']:.0f}%",
             t("Dosis (ppm)", "Dose (ppm)"): round(ppm, 1),
             t("Por lote (g)", "Per batch (g)"): round(ppm * batch / 1000, 1),
             t("Precio (USD/kg)", "Price (USD/kg)"): 0.0}
            for n, s, ppm in est["rows"]])

        edited = st.data_editor(
            table, hide_index=True, use_container_width=True, key="dose_tbl",
            disabled=[c for c in table.columns if c != t("Precio (USD/kg)", "Price (USD/kg)")])

        price_col = t("Precio (USD/kg)", "Price (USD/kg)")
        prices = [float(p or 0) for p in edited[price_col]]
        if any(p > 0 for p in prices):
            cost_t = sum(ppm * p / 1000.0 for (_, _, ppm), p in zip(est["rows"], prices))
            e1, e2 = st.columns(2)
            ref_price = e1.number_input(t("Precio del sintético (USD/kg)",
                                          "Synthetic price (USD/kg)"), 0.0, 500.0, 0.0, 1.0)
            ref_cost_t = ref_dose * ref_price / 1000.0
            with e2:
                st.markdown('<div class="rb-kpis" style="grid-template-columns:1fr 1fr">'
                            + kpi(t("Costo natural", "Natural cost"),
                                  f"${cost_t:,.2f}".replace(",", " "),
                                  t("por tonelada de producto", "per tonne of product"), hero=True)
                            + kpi(t("Costo sintético", "Synthetic cost"),
                                  f"${ref_cost_t:,.2f}".replace(",", " ") if ref_price else "—",
                                  t("por tonelada", "per tonne"))
                            + '</div>', unsafe_allow_html=True)
            if ref_price > 0 and ref_cost_t > 0:
                st.info(t(f"Sobrecosto de {cost_t/ref_cost_t:.1f}× frente al sintético, "
                          f"o {cost_t - ref_cost_t:+,.2f} USD por tonelada.",
                          f"Cost multiple of {cost_t/ref_cost_t:.1f}× versus synthetic, "
                          f"or {cost_t - ref_cost_t:+,.2f} USD per tonne.").replace(",", " "))
        else:
            st.caption(t("Escribe los precios en la última columna para calcular costo en uso.",
                         "Enter prices in the last column to compute cost in use."))

        # El punto de aplicación mueve la dosis tanto como el pigmento
        if dosing:
            alt_pts = {}
            for pt in APP_POINTS:
                c_alt = {n: full_result(n, stages, ph_val, antiox, ca_pct, ca_on,
                                        {pt: 1.0}, cook_loss) for n, _, _ in B["parts"]}
                e_alt = dose_estimate([(n, s) for n, s, _ in B["parts"]],
                                      c_alt, REF_D, ref_dose, Rref_d)
                alt_pts[pt] = e_alt["total_ppm"] if e_alt else None
            st.markdown("**" + t("Misma formulación, distinto punto de aplicación",
                                 "Same formulation, different application point") + "**")
            st.dataframe(pd.DataFrame([
                {t("Punto", "Point"): APP_POINTS[k]["es"] if ES else APP_POINTS[k]["en"],
                 t("Dosis requerida", "Required dose"):
                     (t("inviable", "unviable") if v and v > MAX_PPM
                      else f"{v:,.0f} ppm".replace(",", " ") if v else "—"),
                 t("Veces vs. masa", "Times vs. meat"):
                     f"{v/alt_pts['meat']:.1f}×" if v and alt_pts.get("meat") else "—"}
                for k, v in alt_pts.items()]), hide_index=True, use_container_width=True)

    st.caption(t("Los índices de fuerza colorante son órdenes de magnitud, no valores "
                 "certificados. Sustitúyelos por la ficha técnica del SKU real antes de "
                 "cotizar. Toda dosis debe confirmarse en banco.",
                 "Tinctorial strength indices are order-of-magnitude figures, not certified "
                 "values. Replace them with the real SKU datasheet before quoting. Any dose "
                 "must be confirmed at bench."))

with tab_r:
    REF = "Red 40 + Yellow 6"
    Rref = full_result(REF, stages, ph_val, antiox, ca_pct, ca_on, {"bath": 1.0}, cook_loss)
    ref_hue = PIGMENTS[REF]["hue"]
    ref_sub = on_substrate(ref_hue, Rref["delivered"])
    blend_sub = on_substrate(B["hex"], B["delivered"])

    st.subheader("⚖️ " + t("Comparación contra la referencia sintética",
                           "Benchmark against the synthetic reference"))
    st.caption(t("Las tres columnas se miden contra el mismo objetivo: el color que entrega "
                 "el sistema artificial en el proceso configurado. ΔE₀₀ es la diferencia de "
                 "color percibida sobre el producto — por debajo de 2 es imperceptible.",
                 "All three columns are measured against the same target: the colour the "
                 "artificial system delivers in the configured process. ΔE₀₀ is the perceived "
                 "colour difference on the product — below 2 is imperceptible."))

    # Resultados por pigmento, reutilizados por el optimizador
    cache = {n: full_result(n, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss)
             for n in PIGMENTS}
    alt = suggest_alternative(ref_sub, cache, REF) if dosing else None

    dE_blend = ciede2000(srgb_to_lab(ref_sub), srgb_to_lab(blend_sub))
    perf_blend = (B["delivered"] / Rref["delivered"] * 100.0) if Rref["delivered"] > 0 else None

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(result_card(
            t("REFERENCIA", "REFERENCE"), "Red 40 + Yellow 6", ref_sub, ref_hue,
            t("Colorantes sintéticos dosificados en el baño de agua. "
              "Es el objetivo a igualar, no un candidato.",
              "Synthetic dyes dosed in the water bath. This is the target to match, "
              "not a candidate."),
            None, Rref["delivered"], None, THEME["navy2"], t("OBJETIVO", "TARGET")),
            unsafe_allow_html=True)
    with c2:
        st.markdown(result_card(
            t("TU FORMULACIÓN", "YOUR FORMULATION"),
            B["parts"][0][0] if B["single"] else t("Mezcla de ", "Blend of ") + f"{len(B['parts'])}",
            blend_sub, B["hex"],
            " + ".join(f"{n.split(' (')[0]} {s*100:.0f}%" for n, s, _ in B["parts"]),
            dE_blend, B["delivered"], perf_blend, THEME["gold"], t("ACTUAL", "CURRENT")),
            unsafe_allow_html=True)
    with c3:
        if alt:
            same = ({n for n, _ in alt["components"]} ==
                    {n for n, _, _ in B["parts"]} and abs(alt["dE"] - dE_blend) < 0.15)
            perf_alt = (alt["delivered"] / Rref["delivered"] * 100.0) if Rref["delivered"] > 0 else None
            st.markdown(result_card(
                t("ALTERNATIVA DEL MODELO", "MODEL ALTERNATIVE"),
                t("Mejor match encontrado", "Best match found"),
                alt["sub"], alt["hex"],
                " + ".join(f"{n.split(' (')[0]} {s*100:.0f}%" for n, s in alt["components"]),
                alt["dE"], alt["delivered"], perf_alt,
                THEME["ok"] if not same else THEME["muted"],
                t("YA LA USAS", "ALREADY YOURS") if same else t("SUGERIDA", "SUGGESTED")),
                unsafe_allow_html=True)
        else:
            st.info(t("Activa un punto de aplicación para que el modelo busque alternativas.",
                      "Enable an application point so the model can search alternatives."))

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Lectura del resultado
    if dE_blend <= 2.0:
        st.success(t(f"✅ Tu formulación está en ΔE₀₀ {dE_blend:.1f}: diferencia imperceptible "
                     "para el consumidor.",
                     f"✅ Your formulation is at ΔE₀₀ {dE_blend:.1f}: imperceptible to the consumer."))
    elif dE_blend <= 4.0:
        st.warning(t(f"⚠️ ΔE₀₀ {dE_blend:.1f}: perceptible en comparación lado a lado, "
                     "aceptable viendo el producto aislado.",
                     f"⚠️ ΔE₀₀ {dE_blend:.1f}: perceptible side by side, acceptable in isolation."))
    else:
        msg = t(f"❌ ΔE₀₀ {dE_blend:.1f}: diferencia evidente.",
                f"❌ ΔE₀₀ {dE_blend:.1f}: obvious difference.")
        if alt and alt["dE"] < dE_blend - 0.5:
            msg += t(f" El modelo encuentra {alt['dE']:.1f} con "
                     + " + ".join(f"{n.split(' (')[0]} {s*100:.0f}%" for n, s in alt["components"]) + ".",
                     f" The model finds {alt['dE']:.1f} with "
                     + " + ".join(f"{n.split(' (')[0]} {s*100:.0f}%" for n, s in alt["components"]) + ".")
        st.error(msg)

    if alt:
        st.caption(t(f"La alternativa se busca entre componentes sueltos, pares y tríos del "
                     f"catálogo. Se excluyen los que retienen menos de 60% en este proceso: "
                     f"al destruirse cambian de tono, no solo de intensidad, y el modelo no "
                     f"simula ese viraje.",
                     "The alternative is searched across singles, pairs and triples in the "
                     "catalogue. Components retaining under 60% in this process are excluded: "
                     "when destroyed they shift hue, not just intensity, and the model does "
                     "not simulate that shift."))
    st.caption(t("Umbrales provisionales. El tono de referencia es una aproximación: "
                 "sustitúyelo por el L*a*b* medido del producto objetivo cuando lo tengas.",
                 "Provisional thresholds. The reference hue is an approximation: replace it "
                 "with the measured L*a*b* of the target product when available."))

    # ------------------------------------------------------------------
    # Exploración libre — replegada para no competir con la comparación
    # ------------------------------------------------------------------
    with st.expander(t("Exploración libre por tono", "Free hue exploration")):
        rc1, rc2 = st.columns([1, 2])
        with rc1:
            target = st.color_picker(t("Color objetivo", "Target colour"), ref_hue)
            st.markdown(f'<div style="background:{target};height:90px;border-radius:9px;'
                        f'border:1px solid {THEME["rule"]}"></div>', unsafe_allow_html=True)
            st.caption(t("Ranking de componentes sueltos contra este tono.",
                         "Ranking of single components against this hue."))
        with rc2:
            lab_t = srgb_to_lab(target)
            ranked = sorted(
                ((cache[n]["delivered"] - ciede2000(lab_t, srgb_to_lab(p["hue"])) * 1.6,
                  n, ciede2000(lab_t, srgb_to_lab(p["hue"])), cache[n]["delivered"])
                 for n, p in PIGMENTS.items()), reverse=True)
            for _, name, dE, dv in ranked[:6]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:12px;padding:6px 0;'
                    f'border-bottom:1px solid {THEME["rule"]}">'
                    f'<div style="width:15px;height:15px;border-radius:4px;flex:0 0 auto;'
                    f'background:{PIGMENTS[name]["hue"]};border:1px solid rgba(0,0,0,.12)"></div>'
                    f'<div style="flex:1;min-width:0"><div style="font-size:13px;'
                    f'font-weight:600;color:{THEME["ink"]}">{name}</div>'
                    f'<div style="height:5px;border-radius:3px;margin-top:4px;'
                    f'background:{THEME["rule"]}"><div style="height:5px;border-radius:3px;'
                    f'width:{min(dv,100):.0f}%;background:{PIGMENTS[name]["hue"]}"></div></div></div>'
                    f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;'
                    f'color:{THEME["muted"]};text-align:right;flex:0 0 auto">'
                    f'ΔE₀₀ {dE:.0f}<br>{dv:.0f}%</div></div>', unsafe_allow_html=True)

st.markdown(
    f'<div style="margin-top:26px;padding-top:14px;border-top:1px solid {THEME["rule"]};'
    f'display:flex;justify-content:space-between;font-size:11px;color:{THEME["muted"]};'
    f'letter-spacing:.06em;flex-wrap:wrap;gap:8px">'
    f'<span>CONFIDENTIAL &middot; ROBERTET R&amp;D &mdash; REGIONAL DIVISION</span>'
    f'<span>{t("Modelo de simulación — no sustituye validación de laboratorio",
               "Simulation model — does not replace laboratory validation")}</span></div>',
    unsafe_allow_html=True)
