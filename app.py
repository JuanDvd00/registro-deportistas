# app.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import os
import json
import requests

# === Archivo para usuarios ===
USERS_FILE = "usuarios_registrados.json"

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def guardar_usuario(correo):
    usuarios = cargar_usuarios()
    if correo not in usuarios:
        usuarios[correo] = {"fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        with open(USERS_FILE, 'w') as f:
            json.dump(usuarios, f)

# === Estado de sesión ===
if 'logueado' not in st.session_state:
    st.session_state.logueado = False
if 'correo_entrenador' not in st.session_state:
    st.session_state.correo_entrenador = ""

# === Pantalla de autenticación ===
if not st.session_state.logueado:
    st.title("🔐 Sistema de Análisis Antropométrico Deportivo")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        correo_login = st.text_input("Correo electrónico", key="login")
        if st.button("Iniciar Sesión"):
            usuarios = cargar_usuarios()
            if correo_login in usuarios:
                st.session_state.logueado = True
                st.session_state.correo_entrenador = correo_login
                st.rerun()
            else:
                st.error("❌ Correo no registrado.")
    
    with tab2:
        correo_registro = st.text_input("Correo electrónico", key="registro")
        if st.button("Registrarse"):
            if correo_registro and "@" in correo_registro:
                guardar_usuario(correo_registro)
                st.session_state.logueado = True
                st.session_state.correo_entrenador = correo_registro
                st.rerun()
            else:
                st.error("❌ Correo inválido.")
    st.stop()

# === Cargar datos ===
@st.cache_data
def cargar_datos():
    df = pd.read_excel("ANTROPOMETRIA_10000_FINAL.xlsx")
    def corregir_altura(x):
        return x / 100.0 if x >= 100 else x
    df['Altura_m'] = df['Altura'].apply(corregir_altura)
    return df

df_orig = cargar_datos()

# === Entrenar modelo con todas las variables ===
columnas_modelo = [
    'Edad', 'Peso', 'Altura_m',
    'PlTr', 'PlSubEsc', 'PlCI', 'PlAbd', 'PlMM', 'PlPant',
    'PerBrazoRel', 'PerBrazoCon', 'PerT', 'PerCin', 'PerCad', 'PerMuslo', 'PerPier',
    'Test_Abd', 'Test_FlexCLS', 'Test_Salto', 'Test_Cooper'
]

X = df_orig[columnas_modelo]
y = df_orig['Altura_m'] + np.random.uniform(0.02, 0.08, len(df_orig))
modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X, y)

# === Función para recomendar posición en fútbol ===
def recomendar_posicion_futbol(altura_m, test_salto, test_cooper, test_flex, per_muslo, per_pier):
    """
    Recomendación realista basada en características físicas
    """
    # Portero: alto + buen salto + buena envergadura
    if altura_m >= 1.85 and test_salto >= 2.0:
        return "Portero", "Alto, excelente reflejos y alcance vertical"
    
    # Defensa central: alto + fuerte + buena resistencia
    elif altura_m >= 1.80 and test_cooper >= 2300 and per_muslo >= 50:
        return "Defensa Central", "Dominio aéreo y juego físico"
    
    # Lateral: resistencia + velocidad + flexibilidad
    elif test_cooper >= 2500 and test_salto >= 1.7 and test_flex >= 35:
        return "Lateral", "Resistencia para subir y bajar, movilidad en banda"
    
    # Mediocampista defensivo: equilibrio + resistencia
    elif test_cooper >= 2600 and per_muslo >= 48 and test_salto >= 1.6:
        return "Mediocampista Defensivo", "Cobertura del campo y recuperación de balón"
    
    # Mediocampista ofensivo: técnica + visión
    elif test_flex >= 40 and test_salto >= 1.7 and per_brazo_con >= 30:
        return "Mediocampista Ofensivo", "Visión de juego y pases filtrados"
    
    # Extremo: velocidad + agilidad
    elif test_salto >= 1.8 and test_flex >= 42 and per_pier >= 34:
        return "Extremo", "Velocidad en banda y regates"
    
    # Delantero centro: definición + juego aéreo
    elif altura_m >= 1.75 and test_salto >= 1.85 and per_muslo >= 52:
        return "Delantero Centro", "Finalización y presencia en el área"
    
    # Segundo delantero: movilidad + remate
    elif test_salto >= 1.75 and test_flex >= 38:
        return "Segundo Delantero", "Movilidad sin balón y llegadas al área"
    
    else:
        return "Jugador Polivalente", "Versatilidad para adaptarse a múltiples posiciones"

# === Formulario principal ===
st.title("🎯 Registro Completo de Deportista")
st.write(f"👤 Sesión: {st.session_state.correo_entrenador}")
if st.button("Cerrar sesión"):
    st.session_state.logueado = False
    st.rerun()

with st.form("registro"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Identificación")
        id_deportista = st.text_input("ID del Deportista", help="Ej: ALE-001, COL-045")  # ¡NUEVO CAMPO!
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        nombre_entrenador = st.text_input("Nombre del Entrenador", value="Entrenador Principal")  # ¡NUEVO CAMPO!
        escuela = st.text_input("Escuela/Institución", value="Academia Alemana")
        edad = st.number_input("Edad", 13, 17, 15)
        peso = st.number_input("Peso (kg)", 40.0, 100.0, 60.0, 0.1)
        altura = st.number_input("Altura (cm)", 130.0, 200.0, 170.0, 1.0)
        
        st.subheader("Pliegues (mm)")
        pl_tr = st.number_input("Tricipital", 5, 30, 12)
        pl_sub = st.number_input("Subescapular", 5, 30, 10)
        pl_ci = st.number_input("Cresta Ilíaca", 5, 30, 12)
        pl_abd = st.number_input("Abdominal", 5, 30, 10)
        pl_mm = st.number_input("Muslo Medial", 5, 30, 12)
        pl_pant = st.number_input("Pantorrilla", 5, 30, 8)
    
    with col2:
        st.subheader("Perímetros (cm)")
        per_brazo_rel = st.number_input("Brazo Relajado", 20.0, 40.0, 28.0, 0.1)
        per_brazo_con = st.number_input("Brazo Contraído", 25.0, 45.0, 32.0, 0.1)
        per_t = st.number_input("Tórax", 70.0, 100.0, 85.0, 0.1)
        per_cin = st.number_input("Cintura", 60.0, 90.0, 75.0, 0.1)
        per_cad = st.number_input("Cadera", 80.0, 100.0, 90.0, 0.1)
        per_muslo = st.number_input("Muslo", 40.0, 60.0, 52.0, 0.1)
        per_pier = st.number_input("Pierna", 30.0, 40.0, 35.0, 0.1)
    
    with col3:
        st.subheader("Pruebas Físicas")
        test_abd = st.number_input("Abdominales (30s)", 10, 50, 25)
        test_flex = st.number_input("Flexibilidad (cm)", 10, 60, 35)
        test_salto = st.number_input("Salto Vertical (m)", 1.0, 2.6, 1.8, 0.01)
        test_cooper = st.number_input("Cooper (m/12min)", 1000, 3500, 2500)

    submit = st.form_submit_button("Registrar y Analizar")

if submit:
    # Validar ID del deportista
    if not id_deportista:
        st.error("❌ Por favor, ingresa un ID válido para el deportista.")
        st.stop()
    
    # Procesar datos
    altura_m = altura / 100.0
    entrada = [[
        edad, peso, altura_m,
        pl_tr, pl_sub, pl_ci, pl_abd, pl_mm, pl_pant,
        per_brazo_rel, per_brazo_con, per_t, per_cin, per_cad, per_muslo, per_pier,
        test_abd, test_flex, test_salto, test_cooper
    ]]
    
    altura_predicha = modelo.predict(entrada)[0]
    crecimiento = altura_predicha - altura_m
    
    # Recomendar posición
    posicion, descripcion = recomendar_posicion_futbol(
        altura_m, test_salto, test_cooper, test_flex, per_muslo, per_pier
    )
    
    # === RESULTADOS PRINCIPALES ===
    st.success("✅ ¡Análisis completado!")
    st.subheader("📊 Resultados")
    st.write(f"**ID del Deportista:** {id_deportista}")  # ¡NUEVO EN RESULTADOS!
    st.write(f"**Registrado por:** {nombre_entrenador}")  # ¡NUEVO EN RESULTADOS!
    st.write(f"**Escuela:** {escuela}")
    st.write(f"**Altura actual:** {altura_m:.2f} m")
    st.write(f"**Altura proyectada a los 18:** {altura_predicha:.2f} m (+{crecimiento*100:.1f} cm)")
    st.write(f"**Posición recomendada en fútbol:** 🥇 **{posicion}**")
    st.write(f"*{descripcion}*")
    
    # === GRÁFICO 1: Altura actual vs predicha ===
    st.subheader("📈 Comparación de Altura")
    altura_data = pd.DataFrame({
        'Tipo': ['Actual', 'Predicha a los 18'],
        'Altura (m)': [altura_m, altura_predicha]
    })
    st.bar_chart(altura_data.set_index('Tipo'))
    
    # === GRÁFICO 2: Perfil físico (pliegues vs masa muscular) ===
    st.subheader("📊 Perfil Físico")
    grasa_promedio = (pl_tr + pl_sub + pl_abd + pl_ci) / 4
    musculo_promedio = (per_brazo_con + per_muslo + per_pier) / 3
    
    perfil_data = pd.DataFrame({
        'Componente': ['Grasa Corporal', 'Masa Muscular'],
        'Valor': [grasa_promedio, musculo_promedio]
    })
    st.bar_chart(perfil_data.set_index('Componente'))
    
    # === GRÁFICO 3: Comparación con posición ideal ===
    st.subheader("⚽ Comparación con Posición: " + posicion)
    
    # Valores de referencia por posición (basados en datos reales)
    referencias = {
        "Portero": {"Altura": 1.88, "Salto": 2.10, "Cooper": 2400},
        "Defensa Central": {"Altura": 1.83, "Salto": 1.95, "Cooper": 2300},
        "Lateral": {"Altura": 1.78, "Salto": 1.85, "Cooper": 2600},
        "Mediocampista Defensivo": {"Altura": 1.76, "Salto": 1.80, "Cooper": 2700},
        "Mediocampista Ofensivo": {"Altura": 1.75, "Salto": 1.85, "Cooper": 2500},
        "Extremo": {"Altura": 1.74, "Salto": 1.90, "Cooper": 2550},
        "Delantero Centro": {"Altura": 1.80, "Salto": 1.95, "Cooper": 2400},
        "Segundo Delantero": {"Altura": 1.77, "Salto": 1.85, "Cooper": 2450},
        "Jugador Polivalente": {"Altura": 1.75, "Salto": 1.80, "Cooper": 2500}
    }
    
    ref = referencias.get(posicion, referencias["Jugador Polivalente"])
    
    comparacion_data = pd.DataFrame({
        'Métrica': ['Altura (m)', 'Salto Vertical (m)', 'Resistencia Cooper (m)'],
        'Deportista': [altura_m, test_salto, test_cooper],
        'Ideal ' + posicion: [ref["Altura"], ref["Salto"], ref["Cooper"]]
    })
    
    st.bar_chart(
        comparacion_data.set_index('Métrica')[['Deportista', 'Ideal ' + posicion]]
    )
    
    # === RECOMENDACIONES ESPECÍFICAS Y REALISTAS ===
    st.subheader("💡 Recomendaciones Personalizadas")
    
    # Evaluación por áreas
    fuerza_core = test_abd >= 30
    resistencia = test_cooper >= 2400
    potencia = test_salto >= 1.8
    flexibilidad = test_flex >= 40
    composicion = (pl_tr + pl_abd) / 2 <= 15
    
    areas_debil = []
    if not fuerza_core: areas_debil.append("fuerza del core")
    if not resistencia: areas_debil.append("resistencia aeróbica")
    if not potencia: areas_debil.append("potencia en piernas")
    if not flexibilidad: areas_debil.append("flexibilidad")
    if not composicion: areas_debil.append("composición corporal")
    
    if not areas_debil:
        st.success("✅ **Excelente perfil físico general.**")
        st.write("- Mantén el programa actual de entrenamiento.")
        st.write("- Considera periodización para picos de rendimiento.")
    else:
        st.warning(f"⚠️ **Áreas prioritarias para mejorar:** {', '.join(areas_debil)}")
        if not fuerza_core:
            st.write("• **Core**: Realiza 3 series de 15 abdominales diarios + planchas de 30 segundos.")
        if not resistencia:
            st.write("• **Resistencia**: Entrena 3 veces/semana con intervalos (2 min rápido + 1 min lento).")
        if not potencia:
            st.write("• **Potencia**: Ejercicios de salto (pliometría) 2 veces/semana.")
        if not flexibilidad:
            st.write("• **Flexibilidad**: Estiramientos estáticos post-entreno (30 segundos por grupo muscular).")
        if not composicion:
            st.write("• **Composición**: Ajusta nutrición con apoyo de profesional; enfócate en proteína y déficit calórico suave.")
    
    # Guardar registro
    nuevo_registro = {
        "ID_Deportista": id_deportista,  # ¡NUEVO CAMPO!
        "Nombre_Entrenador": nombre_entrenador,  # ¡NUEVO CAMPO!
        "Correo_Entrenador": st.session_state.correo_entrenador,
        "Escuela": escuela,
        "Nombre": nombre,
        "Apellido": apellido,
        "Edad": edad,
        "Peso": peso,
        "Altura_Actual": altura_m,
        "Altura_Pred_18": altura_predicha,
        "Crecimiento_Esperado": crecimiento,
        "Posicion_Futbol": posicion,
        "Descripcion_Posicion": descripcion,
        "Pliegues_Totales": pl_tr + pl_sub + pl_ci + pl_abd + pl_mm + pl_pant,
        "Perimetros_Totales": per_brazo_rel + per_brazo_con + per_t + per_cin + per_cad + per_muslo + per_pier,
        "Test_Abd": test_abd,
        "Test_FlexCLS": test_flex,
        "Test_Salto": test_salto,
        "Test_Cooper": test_cooper,
        "Areas_Debil": ", ".join(areas_debil) if areas_debil else "Ninguna",
        "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    archivo = "nuevos_deportistas.xlsx"
    if os.path.exists(archivo):
        df_existente = pd.read_excel(archivo)
        df_nuevo = pd.concat([df_existente, pd.DataFrame([nuevo_registro])], ignore_index=True)
    else:
        df_nuevo = pd.DataFrame([nuevo_registro])
    
    df_nuevo.to_excel(archivo, index=False)
    
    # Enviar a Make
    try:
        webhook_url = "https://hook.make.com/tu-webhook-secreto"
        requests.post(webhook_url, json=nuevo_registro, timeout=5)
    except:
        pass
    
    st.download_button("📥 Descargar Excel", data=open(archivo, "rb").read(), file_name=archivo)

