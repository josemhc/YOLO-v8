import time
import cv2
from ultralytics import YOLO  # YOLOv8
from functions.mostrar_inventario import inventario, mostrar_inventario
from functions.configST import configurarStreamlit
from functions.openAI import chat
import streamlit as st

# Cargar el modelo YOLOv8 entrenado
model = YOLO('C:/Users/josem/OneDrive/Escritorio/best (3).pt')

configurarStreamlit()

# Contenedores de video, inventario y mensaje
video_container = st.empty()
mensaje_container = st.empty()
inventario_container = st.empty()

# Inicializar session_state para guardar el frame e inventario
if 'frame_actual' not in st.session_state:
    st.session_state.frame_actual = None
if 'inventario_actualizado' not in st.session_state:
    st.session_state.inventario_actualizado = False
if 'deteccion_activa' not in st.session_state:
    st.session_state.deteccion_activa = False

# Variables para conteo de productos
conteo_productos = {
    'yogurt-yogoyogo': 0,
    'Papas-margarita-pollo': 0,
    'coca-cola': 0,
    'crema-colgate': 0
}

# Contador de frames por producto
frames_detectados = {producto: 0 for producto in conteo_productos.keys()}
frames_ausentes = {producto: 0 for producto in conteo_productos.keys()}

mostrar_inventario(inventario_container)

def deteccion_tiempo_real():

    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        st.error("No se puede acceder a la cámara.")
        return

    while st.session_state.deteccion_activa:
        ret, frame = cap.read()
        if not ret:
          st.error("No se puede leer el frame de la cámara.")
          break

        # Realizar detección
        results = model(frame)
        detecciones_frame_actual = {key: 0 for key in conteo_productos.keys()}
      # Resetear contador de frames
        for producto in conteo_productos:
            frames_ausentes[producto] += 1  # Incrementar el contador de frames ausentes

        for result in results:
            for obj in result.boxes.data:
                clase = int(obj[5])
                etiqueta = model.names[clase]
                confianza = obj[4]

                if confianza >= 0.6 and etiqueta in conteo_productos:
                    detecciones_frame_actual[etiqueta] += 1
                    frames_detectados[etiqueta] += 1  # Incrementar el contador de frames detectados
                    frames_ausentes[etiqueta] = 0  # Reiniciar el contador de ausentes cuando el producto es detectado

 # Actualizar inventario solo si el producto ha estado en pantalla por 10 frames seguidos
        for producto, cantidad_detectada in detecciones_frame_actual.items():
            if frames_detectados[producto] >= 10:  # Si el producto ha estado 10 frames en pantalla
                cantidad_anterior = conteo_productos[producto]
                if cantidad_detectada != cantidad_anterior:
                    inventario[producto]['cantidad'] += (cantidad_detectada - cantidad_anterior)
                    conteo_productos[producto] = cantidad_detectada
                    st.session_state.inventario_actualizado = True

        # Eliminar producto si ha estado ausente durante 10 frames
        for producto, frames_perdidos in frames_ausentes.items():
            if frames_perdidos >= 10:  # Si el producto ha estado ausente durante 10 frames
                if conteo_productos[producto] > 0:
                    inventario[producto]['cantidad'] = 0  # Eliminar producto
                    conteo_productos[producto] = 0
                    st.session_state.inventario_actualizado = True

        # Mostrar frame con detecciones
        frame = results[0].plot()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_container.image(frame_rgb, channels="RGB", use_column_width=True)
         # Actualizar inventario
        if st.session_state.inventario_actualizado:
            mostrar_inventario(inventario_container)
            st.session_state.inventario_actualizado = False
            # Control de frecuencia de actualización
        time.sleep(0.05)
    cap.release()

# Funciones de control
def iniciar_deteccion():
    for producto in inventario:
        inventario[producto]['cantidad'] = 0
    st.session_state.deteccion_activa = True
    deteccion_tiempo_real()

def detener_deteccion():
    st.session_state.deteccion_activa = False

# Botón para iniciar la detección
if st.button("Iniciar Detección"):
    iniciar_deteccion()

# Botón para detener la detección
if st.button("Detener Detección"):
    detener_deteccion()

# Llamada al chat para que siempre esté disponible
chat(inventario)