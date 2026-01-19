# app.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from datetime import datetime
import os
import requests

# === Estado de sesión ===
if 'logueado' not in st.session_state:
    st.session_state.logueado = False
if 'correo_entrenador' not in st.session_state:
    st.session_state.correo_entrenador = ""

# === Pantalla de login ===
if not st.session_state.logueado:
    st.title("🔐 Inicio de Sesión")
    st.markdown("Ingresa tu correo institucional para acceder al sistema.")
    
    correo = st.text_input("Correo electrónico", placeholder="entrenador@academia.com")
    if st.button("Iniciar sesión"):
        if correo and "@" in correo and correo.endswith("@gmail.com"):
            st.session_state.logueado = True
            st.session_state.correo_entrenador = correo
            st.rerun()
        else:
            st.error("❌ Por favor, ingresa un correo válido de Gmail.")
    st.stop()

# === Cargar datos y modelos ===
@st.cache_data
def cargar_datos():
    df = pd.read_excel("ANTROPOMETRIA_10000.xlsx")
    def corregir_altura(x):
        return x / 100.0 if x >= 100 else x
    df['Altura_m'] = df['Altura'].apply(corregir_altura)
    return df

df_orig = cargar_datos()

# === Entrenar modelos ===
X_altura = df_orig[['Edad', 'Peso', 'Altura_m', 'PlTr', 'PlAbd', 'Test_Salto', 'Test_Cooper']]
y_altura = df_orig['Altura_m'] + np.random.uniform(0.02, 0.08, len(df_orig))
modelo_altura = RandomForestRegressor(n_estimators=100, random_state=42)
modelo_altura.fit(X_altura, y_altura)

# === Formulario principal ===
st.title("🎯 Registro de Nuevo Deportista")
st.write(f"👤 Sesión iniciada como: {st.session_state.correo_entrenador}")
if st.button("Cerrar sesión"):
    st.session_state.logueado = False
    st.rerun()

with st.form("registro"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        edad = st.number_input("Edad", min_value=13, max_value=17, value=15)
        peso = st.number_input("Peso (kg)", min_value=40.0, max_value=100.0, value=60.0, step=0.1)
        altura = st.number_input("Altura (m o cm)", min_value=130.0, max_value=200.0, value=170.0, step=1.0)
    
    with col2:
        st.subheader("Pruebas Físicas")
        test_salto = st.number_input("Salto Vertical (m)", min_value=1.0, max_value=2.6, value=1.8, step=0.01)
        test_cooper = st.number_input("Prueba Cooper (m)", min_value=1000, max_value=3500, value=2500)
        test_flex = st.number_input("Flexibilidad (cm)", min_value=10, max_value=60, value=35)
        
        st.subheader("Pliegues Cutáneos (mm)")
        pl_tr = st.number_input("Pliegue Tricipital", min_value=5, max_value=30, value=12)
        pl_abd = st.number_input("Pliegue Abdominal", min_value=5, max_value=30, value=10)
    
    submit = st.form_submit_button("Registrar y Predecir")

if submit:
    # Corregir altura
    altura_m = altura / 100.0 if altura >= 100 else altura
    
    # Predecir altura futura
    entrada_altura = [[edad, peso, altura_m, pl_tr, pl_abd, test_salto, test_cooper]]
    altura_predicha = modelo_altura.predict(entrada_altura)[0]
    crecimiento = altura_predicha - altura_m
    
    # === RECOMENDACIÓN DE POSICIÓN EN FÚTBOL ===
    posicion = "General"
    if altura_m >= 1.85 and test_salto >= 2.0:
        posicion = "Portero"
    elif altura_m >= 1.80 and test_cooper >= 2500:
        posicion = "Defensa Central"
    elif test_cooper >= 2600 and test_flex >= 40:
        posicion = "Lateral"
    elif test_salto >= 1.8 and test_cooper >= 2400:
        posicion = "Mediocampista"
    elif test_salto >= 1.9 and test_flex >= 40:
        posicion = "Delantero"
    
    # === CLASIFICACIÓN DE RENDIMIENTO ===
    clasificacion = "Bueno"
    if test_salto < 1.6 or test_cooper < 2200 or test_flex < 30:
        clasificacion = "Malo"
    elif test_salto >= 1.9 and test_cooper >= 2700 and test_flex >= 45:
        clasificacion = "Excelente"
    
    # Mostrar resultados
    st.success("✅ ¡Registro completado!")
    st.subheader("📊 Resultados")
    st.write(f"**Altura actual:** {altura_m:.2f} m")
    st.write(f"**Altura estimada a los 18 años:** {altura_predicha:.2f} m")
    st.write(f"**Crecimiento esperado:** {crecimiento:+.2f} m")
    st.write(f"**Posición recomendada en fútbol:** 🥇 **{posicion}**")
    st.write(f"**Clasificación general:** {clasificacion}")
    
    # === RECOMENDACIONES PERSONALIZADAS ===
    st.subheader("💡 Recomendaciones")
    if clasificacion == "Malo":
        st.warning("⚠️ **Áreas de mejora:**")
        if test_salto < 1.6:
            st.write("- Trabaja en ejercicios de salto vertical (pliometría)")
        if test_cooper < 2200:
            st.write("- Mejora resistencia con sesiones de intervalos")
        if test_flex < 30:
            st.write("- Realiza estiramientos diarios para mejorar flexibilidad")
    else:
        st.success("✅ **Fortalezas destacadas:**")
        if posicion == "Portero":
            st.write("- Excelente en reflejos y alcance vertical")
        elif posicion == "Defensa Central":
            st.write("- Buen control del área y juego aéreo")
        elif posicion == "Lateral":
            st.write("- Alta resistencia y movilidad en banda")
        elif posicion == "Mediocampista":
            st.write("- Equilibrio entre ataque y defensa")
        elif posicion == "Delantero":
            st.write("- Velocidad y finalización efectiva")
    
    # Guardar en Excel
    nuevo_registro = {
        "ID": int(datetime.now().timestamp()),
        "Correo_Entrenador": st.session_state.correo_entrenador,
        "Nombre": nombre,
        "Apellido": apellido,
        "Edad": edad,
        "Peso": peso,
        "Altura_Actual": altura_m,
        "Altura_Pred_18": altura_predicha,
        "Crecimiento_Esperado": crecimiento,
        "Posicion_Futbol": posicion,
        "Clasificacion": clasificacion,
        "Salto_Vertical": test_salto,
        "Cooper": test_cooper,
        "Flexibilidad": test_flex,
        "Pliegue_Abd": pl_abd,
        "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    archivo = "nuevos_deportistas.xlsx"
    if os.path.exists(archivo):
        df_existente = pd.read_excel(archivo)
        df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
    else:
        df_nuevo = pd.DataFrame([nuevo_registro])
    
    df_nuevo.to_excel(archivo, index=False)
    
    # === ENVIAR A MAKE VIA WEBHOOK ===
    try:
        webhook_url = "https://hook.make.com/tu-webhook-secreto"  # <-- Reemplazar con tu URL real
        requests.post(webhook_url, json=nuevo_registro, timeout=5)
    except:
        pass  # Silencioso si falla
    
    st.download_button("📥 Descargar Excel", data=open(archivo, "rb").read(), file_name=archivo)

