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
    return (f'<div style="text-align:center">'
            f'<div style="background:{hex_color};height:86px;border-radius:10px;'
            f'border:1px solid #ccc"></div>'
            f'<div style="font-size:12px;margin-top:6px"><b>{label}</b></div>'
            f'<div style="font-size:11px;color:#777">{sub}</div></div>')



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


# ==========================================================================
# BARRA LATERAL
# ==========================================================================
st.sidebar.image(LOGO, width=180)
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
st.sidebar.markdown("--- \n### 🎯 " + t("Dosificación", "Dosing"))
st.sidebar.caption(t("Varios puntos a la vez, o ninguno.", "Several points at once, or none."))
dosing_raw = {}
for key, ap in APP_POINTS.items():
    on = st.sidebar.checkbox(ap["es"] if ES else ap["en"], value=(key == "meat"), key=f"ap_{key}")
    if on:
        dosing_raw[key] = st.sidebar.slider("→ % " + t("de la dosis", "of dose"),
                                            0, 100, 100, 5, key=f"sh_{key}")
tot = sum(dosing_raw.values())
dosing = {k: v / tot for k, v in dosing_raw.items()} if tot > 0 else {}

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
st.title("🔬 " + t("Inteligencia de Color R&D — Robertet", "R&D Colour Intelligence — Robertet"))

if B is None:
    st.warning(t("No hay componentes activos. Enciende al menos uno en la barra lateral.",
                 "No active components. Switch on at least one in the sidebar."))
    st.stop()

tab_p, tab_s, tab_b, tab_r = st.tabs([
    t("🔥 Proceso", "🔥 Process"), t("📅 Anaquel", "📅 Shelf life"),
    t("🧪 Formulación", "🧪 Formulation"), t("💡 Recomendador", "💡 Recommender")])

# ---------------------------------------------------------------- proceso
with tab_p:
    if not dosing:
        st.warning(t("Ningún punto de dosificación activo — no hay color en el producto.",
                     "No dosing point active — there is no colour on the product."))

    title = (B["parts"][0][0] if B["single"]
             else t("Mezcla de ", "Blend of ") + f"{len(B['parts'])}")
    st.markdown(
        f'<div style="background:{B["hex"]};opacity:{max(.12, B["delivered"]/100)};'
        f'height:52px;border-radius:8px;display:flex;align-items:center;'
        f'justify-content:center;color:#fff;font-weight:700;">{title}</div>',
        unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)
    k1.metric(t("Retención química", "Chemical retention"), f"{B['chem']:.1f}%",
              help=t("Sobrevive la molécula", "Molecule survives"))
    k2.metric(t("Retención física", "Physical retention"), f"{B['phys']:.1f}%",
              help=t("Se queda en el producto", "Stays on the product"))
    k3.metric(t("COLOR ENTREGADO", "DELIVERED COLOUR"), f"{B['delivered']:.1f}%",
              help=t("Lo que ve el consumidor", "What the consumer sees"))

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
    fig.update_layout(height=430, margin=dict(l=10, r=80, t=30, b=10),
                      hovermode="x unified", plot_bgcolor="white",
                      xaxis=dict(title=t("Tiempo (min)", "Time (min)"), showspikes=True,
                                 spikemode="across", spikethickness=1,
                                 spikecolor="#999", gridcolor="#EEE"),
                      yaxis=dict(title="%", range=[-2, 105], gridcolor="#EEE"),
                      legend=dict(orientation="h", y=1.14, x=0))
    st.plotly_chart(fig, use_container_width=True)

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
    fig2.update_layout(height=390, plot_bgcolor="white", hovermode="x unified",
                       margin=dict(l=10, r=40, t=30, b=10),
                       xaxis=dict(title=t("Meses", "Months"), gridcolor="#EEE"),
                       yaxis=dict(title="%", range=[-2, 105], gridcolor="#EEE"),
                       legend=dict(orientation="h", y=1.14, x=0))
    st.plotly_chart(fig2, use_container_width=True)
    st.metric(t("Al final del anaquel", "At end of shelf life"), f"{blend_shelf[-1]:.1f}%")

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
with tab_r:
    st.subheader("⚖️ " + t("Referencia artificial vs. propuesta natural",
                           "Artificial reference vs. natural proposal"))
    REF = "Red 40 + Yellow 6"
    Rref = full_result(REF, stages, ph_val, antiox, ca_pct, ca_on, {"bath": 1.0}, cook_loss)
    ref_hue = PIGMENTS[REF]["hue"]
    ref_sub = on_substrate(ref_hue, Rref["delivered"])
    blend_sub = on_substrate(B["hex"], B["delivered"])

    r1, r2, r3 = st.columns([1, 1, 1.3])
    with r1:
        st.markdown("**" + t("REFERENCIA", "REFERENCE") + "**")
        st.markdown(swatch(ref_hue, "Red 40 + Yellow 6", t("tono puro", "pure hue")),
                    unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(swatch(ref_sub, t("Sobre producto", "On product"),
                           t("entrega ", "delivery ") + f"{Rref['delivered']:.0f}%"),
                    unsafe_allow_html=True)
        st.caption(t("Dosificado en el baño, como el proceso actual.",
                     "Dosed in the bath, as in the current process."))
    with r2:
        st.markdown("**" + t("PROPUESTA", "PROPOSAL") + "**")
        st.markdown(swatch(B["hex"], t("Formulación", "Formulation"),
                           t("tono puro", "pure hue")), unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(swatch(blend_sub, t("Sobre producto", "On product"),
                           t("entrega ", "delivery ") + f"{B['delivered']:.0f}%"),
                    unsafe_allow_html=True)
        st.caption(" + ".join(f"{n.split(' (')[0]} {s*100:.0f}%" for n, s, _ in B["parts"]))
    with r3:
        st.markdown("**" + t("DESEMPEÑO", "PERFORMANCE") + "**")
        dE_pure = ciede2000(srgb_to_lab(ref_hue), srgb_to_lab(B["hex"]))
        dE_prod = ciede2000(srgb_to_lab(ref_sub), srgb_to_lab(blend_sub))
        perf = (B["delivered"] / Rref["delivered"] * 100.0) if Rref["delivered"] > 0 else 0.0
        m1, m2 = st.columns(2)
        m1.metric("ΔE₀₀ " + t("tono", "hue"), f"{dE_pure:.1f}")
        m2.metric("ΔE₀₀ " + t("producto", "product"), f"{dE_prod:.1f}")
        st.metric(t("Desempeño vs. referencia", "Performance vs. reference"), f"{perf:.0f}%",
                  delta=f"{B['delivered'] - Rref['delivered']:+.0f} pts")
        if dE_prod <= 2.0:
            st.success(t("✅ Diferencia imperceptible (ΔE₀₀ ≤ 2).",
                         "✅ Imperceptible difference (ΔE₀₀ ≤ 2)."))
        elif dE_prod <= 4.0:
            st.warning(t("⚠️ Perceptible lado a lado, aceptable aislado.",
                         "⚠️ Perceptible side by side, acceptable in isolation."))
        else:
            st.error(t("❌ Diferencia evidente. Ajustar proporciones.",
                       "❌ Obvious difference. Adjust ratios."))
        st.caption(t("Umbrales provisionales. Sustituir por la tolerancia real del cliente.",
                     "Provisional thresholds. Replace with the customer tolerance."))

    st.markdown("---")
    st.subheader("🎯 " + t("Búsqueda por tono", "Target hue search"))
    rc1, rc2 = st.columns([1, 2])
    with rc1:
        target = st.color_picker(t("Color objetivo", "Target colour"), ref_hue)
        st.markdown(f'<div style="background:{target};height:100px;border-radius:10px;'
                    f'border:1px solid #ccc;"></div>', unsafe_allow_html=True)
    with rc2:
        lab_t = srgb_to_lab(target)
        ranked = []
        for name, p in PIGMENTS.items():
            dE = ciede2000(lab_t, srgb_to_lab(p["hue"]))
            R = full_result(name, stages, ph_val, antiox, ca_pct, ca_on, dosing, cook_loss)
            ranked.append((R["delivered"] - dE * 1.6, name, dE, R["delivered"]))
        ranked.sort(reverse=True)
        st.markdown("### 🏆 Ranking")
        for _, name, dE, dv in ranked[:5]:
            st.markdown(f"<span style='color:{PIGMENTS[name]['hue']};font-size:18px'>"
                        f"{'█' * max(1, int(dv / 10))}</span> **{name}** — "
                        f"ΔE₀₀ {dE:.0f} · {t('entrega','delivery')} {dv:.0f}%",
                        unsafe_allow_html=True)
        if ranked[0][3] < 25:
            st.error(t("❌ Ningún pigmento entrega suficiente con esta dosificación.",
                       "❌ No pigment delivers enough with this dosing."))
        elif ranked[0][2] > 15:
            st.warning(t("⚠️ Ningún componente único cubre el tono. Usar mezcla.",
                         "⚠️ No single component covers the hue. Use a blend."))
        else:
            st.success(f"✅ **{ranked[0][1]}** — " + t("candidato principal", "lead candidate"))

st.caption("Confidential Robertet R&D — Regional Division.")
