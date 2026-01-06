# app.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import os

# === Cargar datos reales (tu Excel) ===
@st.cache_data
def cargar_datos_originales():
    # Si estás en Colab, sube el archivo primero
    df = pd.read_excel("ANTROPOMETRIA_ALEMANA_CORREGIDA.xlsx")
    
    # Corregir altura
    def corregir_altura(x):
        return x / 100.0 if x >= 100 else x
    df['Altura_m'] = df['Altura'].apply(corregir_altura)
    return df

df_orig = cargar_datos_originales()

# === Entrenar modelo de crecimiento ===
X_altura = df_orig[['Edad', 'Peso', 'Altura_m']]
y_altura = df_orig['Altura_m']

X_train, X_test, y_train, y_test = train_test_split(X_altura, y_altura, test_size=0.2, random_state=42)
modelo_altura = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
modelo_altura.fit(X_train, y_train)

# === Entrenar modelo de recomendación de deporte ===
# Crear etiqueta de deporte (simulada basada en tu lógica)
def recomendar_deporte(row):
    if row['Test_Salto'] >= 2.0 and row['Test_Cooper'] >= 2500:
        return 'Baloncesto'
    elif row['Test_Salto'] >= 1.8 and row['Test_Cooper'] >= 2800:
        return 'Voleibol'
    elif row['Test_Cooper'] >= 2900:
        return 'Atletismo'
    elif row['Test_FlexCLS'] >= 45 and row['Test_Salto'] >= 1.6:
        return 'Gimnasia'
    else:
        return 'Fútbol'

df_orig['Deporte_Recomendado'] = df_orig.apply(recomendar_deporte, axis=1)

X_deporte = df_orig[['Edad', 'Peso', 'Altura_m', 'Test_Salto', 'Test_Cooper', 'Test_FlexCLS']]
y_deporte = df_orig['Deporte_Recomendado']

modelo_deporte = RandomForestClassifier(random_state=42)
modelo_deporte.fit(X_deporte, y_deporte)

# === Interfaz de Streamlit ===
st.set_page_config(page_title="Registro Deportista - Academia Alemana", layout="centered")
st.title("🎯 Registro de Nuevo Deportista")
st.markdown("Ingrese los datos del deportista para predecir su crecimiento y deporte ideal.")

# Formulario
with st.form("registro"):
    nombre = st.text_input("Nombre")
    apellido = st.text_input("Apellido")
    institucion = st.text_input("Institución", value="Academia Alemana")
    edad = st.number_input("Edad", min_value=13, max_value=17, value=15)
    peso = st.number_input("Peso (kg)", min_value=40.0, max_value=100.0, value=60.0, step=0.1)
    altura = st.number_input("Altura (m o cm)", min_value=130.0, max_value=200.0, value=170.0, step=1.0)
    
    st.subheader("Pliegues Cutáneos (mm)")
    col1, col2, col3, col4 = st.columns(4)
    pl_tr = col1.number_input("Pliegue Tricipital", min_value=5, max_value=30, value=12)
    pl_sub = col2.number_input("Pliegue Subescapular", min_value=5, max_value=30, value=10)
    pl_ci = col3.number_input("Pliegue Cresta Ilíaca", min_value=5, max_value=30, value=12)
    pl_abd = col4.number_input("Pliegue Abdominal", min_value=5, max_value=30, value=10)
    
    st.subheader("Pruebas Físicas")
    test_abd = st.number_input("Abdominales (30 seg)", min_value=10, max_value=50, value=25)
    test_flex = st.number_input("Flexibilidad (cm)", min_value=10, max_value=60, value=35)
    test_salto = st.number_input("Salto Vertical (m)", min_value=1.0, max_value=2.6, value=1.8, step=0.01)
    test_cooper = st.number_input("Prueba Cooper (m en 12 min)", min_value=1000, max_value=3500, value=2500)
    
    submit = st.form_submit_button("Registrar y Predecir")

# === Procesar datos ===
if submit:
    # Corregir altura
    if altura >= 100:
        altura_m = altura / 100.0
    else:
        altura_m = altura
    
    # Predecir altura a los 18
    altura_predicha = modelo_altura.predict([[18, peso, altura_m]])[0]
    crecimiento = altura_predicha - altura_m
    
    # Predecir deporte
    deporte_pred = modelo_deporte.predict([[edad, peso, altura_m, test_salto, test_cooper, test_flex]])[0]
    
    # Mostrar resultados
    st.success("✅ Registro procesado con éxito")
    st.subheader("📊 Predicciones")
    st.write(f"**Altura actual:** {altura_m:.2f} m")
    st.write(f"**Altura estimada a los 18 años:** {altura_predicha:.2f} m")
    st.write(f"**Crecimiento esperado:** {crecimiento:+.2f} m")
    st.write(f"**Deporte recomendado:** 🥇 **{deporte_pred}**")
    
    # Guardar en Excel
    nuevo_registro = {
        "ID": int(datetime.now().timestamp()),
        "Insititucion": institucion,
        "Nombre": nombre,
        "Apelllido": apellido,
        "Sexo": "Hombre",  # puedes agregar selector si quieres
        "Edad": edad,
        "Peso": peso,
        "Altura": altura,
        "PlTr": pl_tr,
        "PlSubEsc": pl_sub,
        "PlCI": pl_ci,
        "PlSup": 10,  # puedes añadir más campos si lo deseas
        "PlAbd": pl_abd,
        "PlMM": 12,
        "PlPant": 10,
        "PerBrazoRel": 28.0,
        "PerBrazoCon": 32.0,
        "PerT": 85.0,
        "PerCin": 75.0,
        "PerCad": 90.0,
        "PerMuslo": 52.0,
        "PerPier": 35.0,
        "Test_Abd": test_abd,
        "Clasi_ClsAbd": "Bueno",
        "Test_FlexCLS": test_flex,
        "Clasi_ClsFlex": "Bueno",
        "Test_Salto": test_salto,
        "Clasi_salto": "Bueno",
        "Test_Cooper": test_cooper,
        "Clasi_Coop": "Bueno",
        "Altura_Pred_18": altura_predicha,
        "Deporte_Recomendado": deporte_pred
    }
    
    archivo = "nuevos_deportistas.xlsx"
    if os.path.exists(archivo):
        df_existente = pd.read_excel(archivo)
        df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
    else:
        df_nuevo = pd.DataFrame([nuevo_registro])
    
    df_nuevo.to_excel(archivo, index=False)
    st.download_button("📥 Descargar Excel actualizado", 
                       data=open(archivo, "rb").read(), 
                       file_name=archivo)

st.markdown("---")
st.caption("Desarrollado por Juan David Gutiérrez Ramírez – Proyecto Formativo SENA")