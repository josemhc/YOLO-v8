import streamlit as st
import time
import cv2
from ultralytics import YOLO  # YOLOv8
from functions.mostrar_inventario import inventario
from functions.mostrar_inventario import mostrar_inventario
from functions.configST import configurarStreamlit
from functions.openAI import chat

# Cargar el modelo YOLOv8 entrenado
model = YOLO('C:/Users/josem/OneDrive/Escritorio/best (3).pt')

configurarStreamlit()

# Contenedores de video, inventario y mensaje
video_container = st.empty()
mensaje_container = st.empty()
inventario_container = st.empty()

# Manejo del estado con session_state
if "deteccion_activa" not in st.session_state:
    st.session_state.deteccion_activa = False
if "cap" not in st.session_state:
    st.session_state.cap = None  # Inicializamos como None para manejar el reinicio

# Variables para conteo de productos
conteo_productos = {
    'yogurt-yogoyogo': 0,
    'Papas-margarita-pollo': 0,
    'coca-cola': 0,
    'crema-colgate': 0
}

def iniciar_camara():
    if st.session_state.cap is None or not st.session_state.cap.isOpened():
        st.session_state.cap = cv2.VideoCapture(0)  # Reiniciar la cámara

def deteccion_tiempo_real():
    global conteo_productos
    iniciar_camara()  # Inicializar/reiniciar la cámara
    persona_detectada_anteriormente = False
    productos_anteriores = {key: 0 for key in conteo_productos.keys()}
    persona_antes = False

    while st.session_state.deteccion_activa:
        ret, frame = st.session_state.cap.read()
        if not ret:
            st.error("No se puede acceder a la cámara.")
            break

        results = model(frame)
        detecciones_frame_actual = {key: 0 for key in conteo_productos.keys()}
        persona_detectada = False

        for result in results:
            for obj in result.boxes.data:
                clase = int(obj[5])
                etiqueta = model.names[clase]
                confianza = obj[4]

                if confianza >= 0.2:
                    if etiqueta == 'person':
                        persona_detectada = True
                    if etiqueta in detecciones_frame_actual:
                        detecciones_frame_actual[etiqueta] += 1

        # Actualizar inventario si hay cambios
        inventario_actualizado = False
        for producto, cantidad_detectada in detecciones_frame_actual.items():
            cantidad_anterior = conteo_productos[producto]
            if cantidad_detectada != cantidad_anterior:
                inventario[producto]['cantidad'] += (cantidad_detectada - cantidad_anterior)
                conteo_productos[producto] = cantidad_detectada
                inventario_actualizado = True

        if inventario_actualizado:
            mostrar_inventario(inventario_container)

        # Mensaje de compra realizada
        if persona_antes and not persona_detectada:
            for producto, cantidad in conteo_productos.items():
                if cantidad == 0 and productos_anteriores[producto] > 0:
                    with mensaje_container:
                        st.warning(f"Compra realizada del producto {producto}")
                        time.sleep(1)
                    break

        productos_anteriores = detecciones_frame_actual.copy()
        persona_antes = persona_detectada

        # Mostrar resultados en la interfaz
        frame = results[0].plot()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_container.image(frame_rgb, channels="RGB", use_column_width=True)
        time.sleep(0.1)

    # Liberar la cámara solo si se cierra la detección
    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None

# Botón para iniciar la detección
if st.button("Iniciar Detección"):
    if not st.session_state.deteccion_activa:
        st.session_state.deteccion_activa = True
        deteccion_tiempo_real()

# Botón para detener la detección
if st.button("Detener Detección"):
    st.session_state.deteccion_activa = False
    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None

# Llamada al chat para que siempre esté disponible
chat(inventario)
