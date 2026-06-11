import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Value Selling Calculator", page_icon="🌿", layout="centered")

# 2. Diccionario de Idiomas (Localización)
textos = {
    "Español": {
        "titulo": "🌿 Reemplazo de Oleoresinas vs Especia Natural",
        "subtitulo": "Factor de reemplazo, costo en uso y ahorros reales para especias comerciales.",
        "paso1": "1. Selección de Producto",
        "buscar": "Busca y elige la especia:",
        "paso2": "2. Concentración del Marcador",
        "param_clave": "Parámetro clave",
        "en_nat": "En Especia Natural",
        "en_oleo": "En Oleoresina",
        "factor_exito": "### Factor de Reemplazo: 1 : {ratio:.1f}",
        "factor_cap": "1 kg de oleoresina reemplaza a {ratio:.2f} kg de {especia}",
        "alerta_cero": "Ingresa valores mayores a 0 para calcular el reemplazo.",
        "paso3": "3. Precios y Ahorro",
        "moneda": "Moneda:",
        "precio_oleo": "Precio Oleoresina ({sym}/kg)",
        "precio_nat": "Precio Especia Natural ({sym}/kg)",
        "ciu": "Costo en Uso Equivalente",
        "ahorro_kg": "Ahorro por kg (Vs Natural)",
        "costo_extra_kg": "Costo Extra por kg",
        "ahorro_pct": "{pct:.1f}% ahorro",
        "caro_pct": "-{pct:.1f}% más caro",
        "paso4": "Cálculo por Lote (Opcional)",
        "obj_nat": "Especia natural que deseas reemplazar (kg):",
        "oleo_nec": "Oleoresina Necesaria",
        "costo_con_oleo": "Costo con Oleoresina",
        "ahorro_tot": "Ahorro Total",
        "costo_adic": "Costo Adicional"
    },
    "English": {
        "titulo": "🌿 Oleoresin vs Natural Spice Replacement",
        "subtitulo": "Replacement factor, cost-in-use, and real savings for commercial spices.",
        "paso1": "1. Product Selection",
        "buscar": "Search and choose the spice:",
        "paso2": "2. Marker Concentration",
        "param_clave": "Key Parameter",
        "en_nat": "In Natural Spice",
        "en_oleo": "In Oleoresin",
        "factor_exito": "### Replacement Factor: 1 : {ratio:.1f}",
        "factor_cap": "1 kg of oleoresin replaces {ratio:.2f} kg of {especia}",
        "alerta_cero": "Enter values greater than 0 to calculate replacement.",
        "paso3": "3. Prices and Savings",
        "moneda": "Currency:",
        "precio_oleo": "Oleoresin Price ({sym}/kg)",
        "precio_nat": "Natural Spice Price ({sym}/kg)",
        "ciu": "Equivalent Cost in Use",
        "ahorro_kg": "Savings per kg (Vs Natural)",
        "costo_extra_kg": "Extra Cost per kg",
        "ahorro_pct": "{pct:.1f}% savings",
        "caro_pct": "-{pct:.1f}% more expensive",
        "paso4": "Batch Calculation (Optional)",
        "obj_nat": "Natural spice to replace (kg):",
        "oleo_nec": "Oleoresin Needed",
        "costo_con_oleo": "Cost with Oleoresin",
        "ahorro_tot": "Total Savings",
        "costo_adic": "Additional Cost"
    }
}

# Selector de Idioma (En la parte superior)
idioma = st.radio("🌍 Language / Idioma:", ["English", "Español"], horizontal=True)
t = textos[idioma] # 't' ahora contiene todos los textos en el idioma elegido

st.title(t["titulo"])
st.markdown(t["subtitulo"])
st.markdown("---")

# 3. Base de Datos Completa (Nombres Bilingües)
datos = [
    {"Producto": "Black pepper / Pimienta Negra", "Parametro": "Piperine", "Unidad": "%", "Nat": 5.0, "Oleo": 40.0},
    {"Producto": "White pepper / Pimienta Blanca", "Parametro": "Piperine", "Unidad": "%", "Nat": 6.0, "Oleo": 38.0},
    {"Producto": "Capsicum / Chile", "Parametro": "Capsaicin (pungency)", "Unidad": "SHU", "Nat": 40000.0, "Oleo": 1000000.0},
    {"Producto": "Paprika / Pimentón", "Parametro": "Color value", "Unidad": "CU", "Nat": 120.0, "Oleo": 40000.0},
    {"Producto": "Turmeric / Cúrcuma", "Parametro": "Curcumin", "Unidad": "%", "Nat": 3.5, "Oleo": 35.0},
    {"Producto": "Rosemary (antioxidant) / Romero", "Parametro": "Carnosic acid", "Unidad": "%", "Nat": 2.0, "Oleo": 18.0},
    {"Producto": "Ginger / Jengibre", "Parametro": "Volatile oil (gingerols)", "Unidad": "%", "Nat": 2.0, "Oleo": 26.0},
    {"Producto": "Cardamom / Cardamomo", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 6.5, "Oleo": 60.0},
    {"Producto": "Clove / Clavo", "Parametro": "Volatile oil (eugenol)", "Unidad": "%", "Nat": 16.0, "Oleo": 80.0},
    {"Producto": "Nutmeg / Nuez Moscada", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 8.0, "Oleo": 30.0},
    {"Producto": "Mace / Macis", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 10.0, "Oleo": 30.0},
    {"Producto": "Cinnamon / Canela", "Parametro": "Volatile oil (cinnamaldehyde)", "Unidad": "%", "Nat": 1.5, "Oleo": 25.0},
    {"Producto": "Allspice / Pimienta Gorda", "Parametro": "Volatile oil (eugenol)", "Unidad": "%", "Nat": 4.0, "Oleo": 35.0},
    {"Producto": "Bay leaf / Laurel", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 2.0, "Oleo": 15.0},
    {"Producto": "Cumin / Comino", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 3.0, "Oleo": 20.0},
    {"Producto": "Coriander / Cilantro semilla", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 0.8, "Oleo": 6.0},
    {"Producto": "Caraway / Alcaravea", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 4.0, "Oleo": 15.0},
    {"Producto": "Fennel / Hinojo", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 4.0, "Oleo": 12.0},
    {"Producto": "Anise / Anís", "Parametro": "Volatile oil (anethole)", "Unidad": "%", "Nat": 2.5, "Oleo": 15.0},
    {"Producto": "Star anise / Anís Estrella", "Parametro": "Volatile oil (anethole)", "Unidad": "%", "Nat": 8.0, "Oleo": 18.0},
    {"Producto": "Dill seed / Eneldo", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 3.0, "Oleo": 15.0},
    {"Producto": "Celery seed / Semilla de Apio", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 2.5, "Oleo": 13.0},
    {"Producto": "Garlic / Ajo", "Parametro": "Volatile oil (sulfur cpds)", "Unidad": "%", "Nat": 0.3, "Oleo": 5.0},
    {"Producto": "Onion / Cebolla", "Parametro": "Volatile oil (sulfur cpds)", "Unidad": "%", "Nat": 0.1, "Oleo": 3.0},
    {"Producto": "Vanilla / Vainilla", "Parametro": "Vanillin", "Unidad": "%", "Nat": 2.0, "Oleo": 25.0},
    {"Producto": "Custom / Personalizado", "Parametro": "Marker / Marcador", "Unidad": "%", "Nat": 1.0, "Oleo": 1.0}
]
df = pd.DataFrame(datos)

# 4. Paso 1: Selección
st.subheader(t["paso1"])
nombres_productos = df["Producto"].tolist()
seleccion = st.selectbox(t["buscar"], nombres_productos)

datos_prod = df[df["Producto"] == seleccion].iloc[0]
unidad = datos_prod["Unidad"]

# 5. Paso 2: Concentración
st.subheader(t["paso2"])
st.info(f"**{t['param_clave']}:** {datos_prod['Parametro']}")

col1, col2 = st.columns(2)
with col1:
    c_nat = st.number_input(f"{t['en_nat']} ({unidad})", value=float(datos_prod["Nat"]), step=0.1, format="%.2f")
with col2:
    c_oleo = st.number_input(f"{t['en_oleo']} ({unidad})", value=float(datos_prod["Oleo"]), step=0.1, format="%.2f")

if c_nat > 0 and c_oleo > 0:
    ratio = c_oleo / c_nat
    st.success(t["factor_exito"].format(ratio=ratio))
    st.caption(t["factor_cap"].format(ratio=ratio, especia=seleccion.split(" / ")[0]))
else:
    ratio = 0
    st.warning(t["alerta_cero"])

# 6. Paso 3: Precios y Moneda
st.markdown("---")
st.subheader(t["paso3"])

moneda = st.radio(t["moneda"], ["USD ($)", "EUR (€)", "MXN ($)"], horizontal=True)
simbolo = moneda.split(" ")[1]

col_p1, col_p2 = st.columns(2)
with col_p1:
    p_oleo = st.number_input(t["precio_oleo"].format(sym=simbolo), value=80.0, step=1.0)
with col_p2:
    p_nat = st.number_input(t["precio_nat"].format(sym=simbolo), value=15.0, step=1.0)

# Matemáticas de Ahorro
if ratio > 0 and p_oleo > 0:
    costo_en_uso = p_oleo / ratio
    ahorro_kg = p_nat - costo_en_uso
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric(label=t["ciu"], value=f"{simbolo} {costo_en_uso:.2f}")
    
    if ahorro_kg > 0:
        porcentaje = (ahorro_kg / p_nat) * 100
        c2.metric(label=t["ahorro_kg"], value=f"{simbolo} {ahorro_kg:.2f}", delta=t["ahorro_pct"].format(pct=porcentaje))
    else:
        porcentaje = (abs(ahorro_kg) / p_nat) * 100
        c2.metric(label=t["costo_extra_kg"], value=f"{simbolo} {abs(ahorro_kg):.2f}", delta=t["caro_pct"].format(pct=porcentaje), delta_color="inverse")

# 7. Cálculo por Lote (Batch Calculation)
st.markdown("---")
st.subheader(t["paso4"])
target = st.number_input(t["obj_nat"], value=0.0, step=10.0)

if target > 0 and ratio > 0:
    oleo_necesaria = target / ratio
    costo_total_oleo = oleo_necesaria * p_oleo
    costo_total_nat = target * p_nat
    ahorro_lote = costo_total_nat - costo_total_oleo
    
    c_b1, c_b2, c_b3 = st.columns(3)
    c_b1.metric(t["oleo_nec"], f"{oleo_necesaria:.2f} kg")
    c_b2.metric(t["costo_con_oleo"], f"{simbolo} {costo_total_oleo:,.2f}")
    
    if ahorro_lote > 0:
        c_b3.metric(t["ahorro_tot"], f"{simbolo} {ahorro_lote:,.2f}")
    else:
        c_b3.metric(t["costo_adic"], f"{simbolo} {abs(ahorro_lote):,.2f}")
