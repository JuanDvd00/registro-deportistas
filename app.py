# app.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from datetime import datetime
import os

# === Cargar datos ===
@st.cache_data
def cargar_datos():
    df = pd.read_excel("ANTROPOMETRIA_10000_FINAL.xlsx")
    
    # Corregir altura
    def corregir_altura(x):
        return x / 100.0 if x >= 100 else x
    df['Altura_m'] = df['Altura'].apply(corregir_altura)
    
    # Crear columna de deporte recomendado
    def recomendar_deporte(row):
        if row['Test_Salto'] >= 2.0 and row['Test_Cooper'] >= 2500:
            return 'Baloncesto'
        elif row['Test_Salto'] >= 1.8 and row['Test_Cooper'] >= 2800:
            return 'Voleibol'
        elif row['Test_Cooper'] >= 2900:
            return 'Atletismo'
        elif row['Test_FlexCLS'] >= 45 and row['Test_Salto'] >= 1.6:
            return 'Gimnasia'
        elif row['Test_Salto'] >= 1.7 and row['Test_Cooper'] >= 2400:
            return 'Fútbol'
        else:
            return 'General'
    
    df['Deporte_Recomendado'] = df.apply(recomendar_deporte, axis=1)
    return df

df_orig = cargar_datos()

# === Entrenar modelo de altura futura (con todos los pliegues y perímetros) ===
X_altura = df_orig[[
    'Edad', 'Peso', 'Altura_m',
    'PlTr', 'PlSubEsc', 'PlCI', 'PlAbd', 'PlMM', 'PlPant',  # Pliegues
    'PerBrazoRel', 'PerBrazoCon', 'PerT', 'PerCin', 'PerCad', 'PerMuslo', 'PerPier',  # Perímetros
    'Test_Salto', 'Test_Cooper', 'Test_FlexCLS'  # Pruebas físicas
]]
y_altura = df_orig['Altura_m'] + np.random.uniform(0.02, 0.08, len(df_orig))  # Simular crecimiento

X_train, X_test, y_train, y_test = train_test_split(X_altura, y_altura, test_size=0.2, random_state=42)
modelo_altura = RandomForestRegressor(n_estimators=100, random_state=42)
modelo_altura.fit(X_train, y_train)

# === Entrenar modelo de recomendación ===
X_deporte = df_orig[[
    'Edad', 'Peso', 'Altura_m',
    'PlTr', 'PlSubEsc', 'PlCI', 'PlAbd', 'PlMM', 'PlPant',
    'PerBrazoRel', 'PerBrazoCon', 'PerT', 'PerCin', 'PerCad', 'PerMuslo', 'PerPier',
    'Test_Salto', 'Test_Cooper', 'Test_FlexCLS'
]]
y_deporte = df_orig['Deporte_Recomendado']
modelo_deporte = RandomForestClassifier(n_estimators=100, random_state=42)
modelo_deporte.fit(X_deporte, y_deporte)

# === Interfaz ===
st.set_page_config(page_title="Análisis Antropométrico Deportivo", layout="centered")
st.title("🎯 Análisis Antropométrico Deportivo")
st.markdown("Ingrese los datos del deportista para predecir su crecimiento y obtener recomendaciones personalizadas.")

with st.form("registro"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        institucion = st.text_input("Institución", value="Academia Alemana")
        edad = st.number_input("Edad", min_value=13, max_value=17, value=15)
        peso = st.number_input("Peso (kg)", min_value=40.0, max_value=100.0, value=60.0, step=0.1)
        altura = st.number_input("Altura (m o cm)", min_value=130.0, max_value=200.0, value=170.0, step=1.0)
    
    with col2:
        st.subheader("Pliegues Cutáneos (mm)")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pl_tr = st.number_input("Pliegue Tricipital", min_value=5, max_value=30, value=12)
            pl_sub = st.number_input("Pliegue Subescapular", min_value=5, max_value=30, value=10)
            pl_ci = st.number_input("Pliegue Cresta Ilíaca", min_value=5, max_value=30, value=12)
        with col_p2:
            pl_abd = st.number_input("Pliegue Abdominal", min_value=5, max_value=30, value=10)
            pl_mm = st.number_input("Pliegue Muslo Medial", min_value=5, max_value=30, value=12)
            pl_pant = st.number_input("Pliegue Pantorrilla", min_value=5, max_value=30, value=8)
        
        st.subheader("Perímetros Corporales (cm)")
        col_per1, col_per2 = st.columns(2)
        with col_per1:
            per_brazo_rel = st.number_input("Brazo Relajado", min_value=20.0, max_value=40.0, value=28.0, step=0.1)
            per_brazo_con = st.number_input("Brazo Contraído", min_value=25.0, max_value=45.0, value=32.0, step=0.1)
            per_t = st.number_input("Torax", min_value=70.0, max_value=100.0, value=85.0, step=0.1)
        with col_per2:
            per_cin = st.number_input("Cintura", min_value=60.0, max_value=90.0, value=75.0, step=0.1)
            per_cad = st.number_input("Cadera", min_value=80.0, max_value=100.0, value=90.0, step=0.1)
            per_muslo = st.number_input("Muslo", min_value=40.0, max_value=60.0, value=52.0, step=0.1)
            per_pier = st.number_input("Pierna", min_value=30.0, max_value=40.0, value=35.0, step=0.1)
        
        st.subheader("Pruebas Físicas")
        test_salto = st.number_input("Salto Vertical (m)", min_value=1.0, max_value=2.6, value=1.8, step=0.01)
        test_cooper = st.number_input("Prueba Cooper (m)", min_value=1000, max_value=3500, value=2500)
        test_flex = st.number_input("Flexibilidad (cm)", min_value=10, max_value=60, value=35)
    
    submit = st.form_submit_button("Registrar y Predecir")

if submit:
    # Corregir altura
    altura_m = altura / 100.0 if altura >= 100 else altura
    
    # Predecir altura futura
    entrada_altura = [[
        edad, peso, altura_m,
        pl_tr, pl_sub, pl_ci, pl_abd, pl_mm, pl_pant,
        per_brazo_rel, per_brazo_con, per_t, per_cin, per_cad, per_muslo, per_pier,
        test_salto, test_cooper, test_flex
    ]]
    altura_predicha = modelo_altura.predict(entrada_altura)[0]
    crecimiento = altura_predicha - altura_m
    
    # Predecir deporte
    entrada_deporte = [[
        edad, peso, altura_m,
        pl_tr, pl_sub, pl_ci, pl_abd, pl_mm, pl_pant,
        per_brazo_rel, per_brazo_con, per_t, per_cin, per_cad, per_muslo, per_pier,
        test_salto, test_cooper, test_flex
    ]]
    deporte_pred = modelo_deporte.predict(entrada_deporte)[0]
    
    # Mostrar resultados
    st.success("✅ ¡Análisis completado!")
    st.subheader("📊 Resultados")
    st.write(f"**Altura actual:** {altura_m:.2f} m")
    st.write(f"**Altura estimada a los 18 años:** {altura_predicha:.2f} m")
    st.write(f"**Crecimiento esperado:** {crecimiento:+.2f} m")
    st.write(f"**Deporte recomendado:** 🥇 **{deporte_pred}**")
    
    # Recomendaciones específicas
    st.subheader("💡 Recomendaciones Personalizadas")
    if deporte_pred == "Baloncesto":
        st.write("- Enfócate en ejercicios de salto vertical y coordinación.")
        st.write("- Monitorea el crecimiento mensual para ajustar la técnica.")
    elif deporte_pred == "Voleibol":
        st.write("- Desarrolla potencia en piernas y movimientos laterales.")
        st.write("- Trabaja en la flexibilidad para mejorar la recepción.")
    elif deporte_pred == "Fútbol":
        st.write("- Mejora la resistencia aeróbica con sesiones de intervalos.")
        st.write("- Fortalece el core para mayor estabilidad en cambios de dirección.")
    elif deporte_pred == "Atletismo":
        st.write("- Entrena velocidad y explosividad con sprints cortos.")
        st.write("- Controla la técnica de carrera para evitar lesiones.")
    else:
        st.write("- Realiza una evaluación completa con un entrenador especializado.")
    
    # Guardar en Excel
    nuevo_registro = {
        "ID": int(datetime.now().timestamp()),
        "Institución": institucion,
        "Nombre": nombre,
        "Apellido": apellido,
        "Edad": edad,
        "Peso": peso,
        "Altura_Actual": altura_m,
        "Altura_Pred_18": altura_predicha,
        "Crecimiento_Esperado": crecimiento,
        "Deporte_Recomendado": deporte_pred,
        "Salto_Vertical": test_salto,
        "Cooper": test_cooper,
        "Flexibilidad": test_flex,
        "Pliegue_Abd": pl_abd,
        "Pliegue_Tr": pl_tr,
        "Pliegue_Sub": pl_sub,
        "Perimetro_Brazo_Rel": per_brazo_rel,
        "Perimetro_Brazo_Con": per_brazo_con
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


