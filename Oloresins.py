import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Calculadora de Oleoresinas", page_icon="🌿", layout="centered")

st.title("🌿 Reemplazo de Oleoresinas vs Especia Natural")
st.markdown("Factor de reemplazo, costo en uso y ahorros reales para especias comerciales.")
st.markdown("---")

# 2. Base de Datos Completa (Traducida del código React)
datos = [
    {"Producto": "Black pepper", "Parametro": "Piperine", "Unidad": "%", "Nat": 5.0, "Oleo": 40.0},
    {"Producto": "White pepper", "Parametro": "Piperine", "Unidad": "%", "Nat": 6.0, "Oleo": 38.0},
    {"Producto": "Capsicum / chili", "Parametro": "Capsaicin (pungency)", "Unidad": "SHU", "Nat": 40000.0, "Oleo": 1000000.0},
    {"Producto": "Paprika", "Parametro": "Color value", "Unidad": "CU", "Nat": 120.0, "Oleo": 40000.0},
    {"Producto": "Turmeric", "Parametro": "Curcumin", "Unidad": "%", "Nat": 3.5, "Oleo": 35.0},
    {"Producto": "Rosemary (antioxidant)", "Parametro": "Carnosic acid", "Unidad": "%", "Nat": 2.0, "Oleo": 18.0},
    {"Producto": "Ginger", "Parametro": "Volatile oil (gingerols)", "Unidad": "%", "Nat": 2.0, "Oleo": 26.0},
    {"Producto": "Cardamom", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 6.5, "Oleo": 60.0},
    {"Producto": "Clove", "Parametro": "Volatile oil (eugenol)", "Unidad": "%", "Nat": 16.0, "Oleo": 80.0},
    {"Producto": "Nutmeg", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 8.0, "Oleo": 30.0},
    {"Producto": "Mace", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 10.0, "Oleo": 30.0},
    {"Producto": "Cinnamon / cassia", "Parametro": "Volatile oil (cinnamaldehyde)", "Unidad": "%", "Nat": 1.5, "Oleo": 25.0},
    {"Producto": "Allspice / pimenta", "Parametro": "Volatile oil (eugenol)", "Unidad": "%", "Nat": 4.0, "Oleo": 35.0},
    {"Producto": "Bay / laurel leaf", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 2.0, "Oleo": 15.0},
    {"Producto": "Cumin", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 3.0, "Oleo": 20.0},
    {"Producto": "Coriander", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 0.8, "Oleo": 6.0},
    {"Producto": "Caraway", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 4.0, "Oleo": 15.0},
    {"Producto": "Fennel", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 4.0, "Oleo": 12.0},
    {"Producto": "Anise", "Parametro": "Volatile oil (anethole)", "Unidad": "%", "Nat": 2.5, "Oleo": 15.0},
    {"Producto": "Star anise", "Parametro": "Volatile oil (anethole)", "Unidad": "%", "Nat": 8.0, "Oleo": 18.0},
    {"Producto": "Dill seed", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 3.0, "Oleo": 15.0},
    {"Producto": "Celery seed", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 2.5, "Oleo": 13.0},
    {"Producto": "Angelica seed", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 1.0, "Oleo": 4.0},
    {"Producto": "Cubeb", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 12.0, "Oleo": 65.0},
    {"Producto": "Parsley leaf", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 0.2, "Oleo": 6.0},
    {"Producto": "Parsley seed", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 3.0, "Oleo": 4.0},
    {"Producto": "Basil", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 1.0, "Oleo": 10.0},
    {"Producto": "Marjoram (sweet)", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 1.5, "Oleo": 13.0},
    {"Producto": "Oregano / origanum", "Parametro": "Volatile oil (carvacrol)", "Unidad": "%", "Nat": 4.0, "Oleo": 32.0},
    {"Producto": "Thyme", "Parametro": "Volatile oil (thymol)", "Unidad": "%", "Nat": 1.8, "Oleo": 8.0},
    {"Producto": "Sage", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 2.0, "Oleo": 12.0},
    {"Producto": "Rosemary (flavor)", "Parametro": "Volatile oil", "Unidad": "%", "Nat": 1.5, "Oleo": 12.0},
    {"Producto": "Fenugreek", "Parametro": "Volatile oil / sotolon", "Unidad": "%", "Nat": 0.3, "Oleo": 2.0},
    {"Producto": "Mustard", "Parametro": "Volatile oil (allyl ITC)", "Unidad": "%", "Nat": 0.8, "Oleo": 20.0},
    {"Producto": "Garlic", "Parametro": "Volatile oil (sulfur cpds)", "Unidad": "%", "Nat": 0.3, "Oleo": 5.0},
    {"Producto": "Onion", "Parametro": "Volatile oil (sulfur cpds)", "Unidad": "%", "Nat": 0.1, "Oleo": 3.0},
    {"Producto": "Hop", "Parametro": "Volatile oil / α-acids", "Unidad": "%", "Nat": 1.0, "Oleo": 25.0},
    {"Producto": "Vanilla", "Parametro": "Vanillin", "Unidad": "%", "Nat": 2.0, "Oleo": 25.0},
    {"Producto": "Custom / other", "Parametro": "Custom Marker", "Unidad": "%", "Nat": 1.0, "Oleo": 1.0}
]
df = pd.DataFrame(datos)

# 3. Paso 1: Selección
st.subheader("1. Selección de Producto")
nombres_productos = df["Producto"].tolist()
seleccion = st.selectbox("Busca y elige la especia:", nombres_productos)

datos_prod = df[df["Producto"] == seleccion].iloc[0]
unidad = datos_prod["Unidad"]

# 4. Paso 2: Concentración
st.subheader("2. Concentración del Marcador")
st.info(f"**Parámetro clave:** {datos_prod['Parametro']}")

col1, col2 = st.columns(2)
with col1:
    c_nat = st.number_input(f"En Especia Natural ({unidad})", value=float(datos_prod["Nat"]), step=0.1, format="%.2f")
with col2:
    c_oleo = st.number_input(f"En Oleoresina ({unidad})", value=float(datos_prod["Oleo"]), step=0.1, format="%.2f")

# Validar que no haya ceros para no romper la división
if c_nat > 0 and c_oleo > 0:
    ratio = c_oleo / c_nat
    st.success(f"### Factor de Reemplazo: 1 : {ratio:.1f}")
    st.caption(f"1 kg de oleoresina reemplaza a {ratio:.2f} kg de {seleccion.lower()}")
else:
    ratio = 0
    st.warning("Ingresa valores mayores a 0 para calcular el reemplazo.")

# 5. Paso 3: Precios y Moneda
st.markdown("---")
st.subheader("3. Precios y Ahorro")

moneda = st.radio("Moneda:", ["USD ($)", "EUR (€)", "MXN ($)"], horizontal=True)
simbolo = moneda.split(" ")[1]

col_p1, col_p2 = st.columns(2)
with col_p1:
    p_oleo = st.number_input(f"Precio Oleoresina ({simbolo}/kg)", value=80.0, step=1.0)
with col_p2:
    p_nat = st.number_input(f"Precio Especia Natural ({simbolo}/kg)", value=15.0, step=1.0)

# Matemáticas de Ahorro
if ratio > 0 and p_oleo > 0:
    costo_en_uso = p_oleo / ratio
    ahorro_kg = p_nat - costo_en_uso
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric(label="Costo en Uso Equivalente", value=f"{simbolo} {costo_en_uso:.2f}")
    
    if ahorro_kg > 0:
        porcentaje = (ahorro_kg / p_nat) * 100
        c2.metric(label="Ahorro por kg (Vs Natural)", value=f"{simbolo} {ahorro_kg:.2f}", delta=f"{porcentaje:.1f}% ahorro")
    else:
        porcentaje = (abs(ahorro_kg) / p_nat) * 100
        c2.metric(label="Costo Extra por kg", value=f"{simbolo} {abs(ahorro_kg):.2f}", delta=f"-{porcentaje:.1f}% más caro", delta_color="inverse")

# 6. Cálculo por Lote (Batch Calculation)
st.markdown("---")
st.subheader("Cálculo por Lote (Opcional)")
target = st.number_input("Especia natural que deseas reemplazar (kg):", value=0.0, step=10.0)

if target > 0 and ratio > 0:
    oleo_necesaria = target / ratio
    costo_total_oleo = oleo_necesaria * p_oleo
    costo_total_nat = target * p_nat
    ahorro_lote = costo_total_nat - costo_total_oleo
    
    c_b1, c_b2, c_b3 = st.columns(3)
    c_b1.metric("Oleoresina Necesaria", f"{oleo_necesaria:.2f} kg")
    c_b2.metric("Costo con Oleoresina", f"{simbolo} {costo_total_oleo:,.2f}")
    
    if ahorro_lote > 0:
        c_b3.metric("Ahorro Total", f"{simbolo} {ahorro_lote:,.2f}")
    else:
        c_b3.metric("Costo Adicional", f"{simbolo} {abs(ahorro_lote):,.2f}")
