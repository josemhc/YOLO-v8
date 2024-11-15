import time
import cv2
from ultralytics import YOLO  # YOLOv8
from functions.mostrar_inventario import inventario, mostrar_inventario
from functions.configST import configurarStreamlit
from functions.openAI import chat
import streamlit as st

# Cargar los modelos YOLO
modelo_productos = YOLO('C:/Users/josem/OneDrive/Escritorio/best (3).pt')  # Modelo para productos
modelo_personas = YOLO('yolov8n.pt')  # Modelo para detección de personas

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

# Variables para conteo de productos y personas
conteo_productos = {
    'yogurt-yogoyogo': 0,
    'Papas-margarita-pollo': 0,
    'coca-cola': 0,
    'crema-colgate': 0
}
conteo_personas = 0  # Número total de personas detectadas

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

        # Realizar detección con ambos modelos
        results_productos = modelo_productos(frame)  # Detección de productos
        results_personas = modelo_personas(frame)   # Detección de personas

        # --- Detección de productos ---
        detecciones_frame_actual = {key: 0 for key in conteo_productos.keys()}
        for producto in conteo_productos:
            frames_ausentes[producto] += 1  # Incrementar el contador de frames ausentes

        for result in results_productos:
            for obj in result.boxes.data:
                clase = int(obj[5])
                etiqueta = modelo_productos.names[clase]
                confianza = obj[4]

                # Ignorar detecciones de la clase "person"
                if etiqueta == "person":
                    continue

                # Procesar solo las clases relevantes de productos
                if confianza >= 0.6 and etiqueta in conteo_productos:
                    detecciones_frame_actual[etiqueta] += 1
                    frames_detectados[etiqueta] += 1
                    frames_ausentes[etiqueta] = 0

        for producto, cantidad_detectada in detecciones_frame_actual.items():
            if frames_detectados[producto] >= 10:
                cantidad_anterior = conteo_productos[producto]
                if cantidad_detectada != cantidad_anterior:
                    inventario[producto]['cantidad'] += (cantidad_detectada - cantidad_anterior)
                    conteo_productos[producto] = cantidad_detectada
                    st.session_state.inventario_actualizado = True

        for producto, frames_perdidos in frames_ausentes.items():
            if frames_perdidos >= 10:
                if conteo_productos[producto] > 0:
                    inventario[producto]['cantidad'] = 0
                    conteo_productos[producto] = 0
                    st.session_state.inventario_actualizado = True

        # --- Detección de personas ---
        global conteo_personas
        detecciones_personas = 0
        personas_boxes = []  # Lista para almacenar las detecciones de personas

        for result in results_personas:
            for obj in result.boxes.data:
                clase = int(obj[5])
                etiqueta = modelo_personas.names[clase]
                confianza = obj[4]

                if confianza >= 0.6 and etiqueta == "person":  # Filtrar solo personas
                    detecciones_personas += 1
                    personas_boxes.append(obj[:4])  # Guardar las coordenadas del recuadro

        conteo_personas = detecciones_personas  # Actualizar conteo de personas detectadas

        # --- Dibujar detecciones ---
        # Crear una copia del frame original para dibujar productos y personas
        frame_detecciones = frame.copy()

        # Dibujar detecciones de productos en el frame, ignorando "person"
        for result in results_productos:
            for obj in result.boxes.data:
                clase = int(obj[5])
                etiqueta = modelo_productos.names[clase]
                confianza = obj[4]

                if etiqueta == "person":
                    continue  # Ignorar la clase "person"

                if confianza >= 0.6 and etiqueta in conteo_productos:
                    x1, y1, x2, y2 = map(int, obj[:4])  # Coordenadas del recuadro
                    cv2.rectangle(frame_detecciones, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Recuadro azul
                    cv2.putText(frame_detecciones, etiqueta, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Dibujar únicamente recuadros de personas en el frame
        for box in personas_boxes:
            x1, y1, x2, y2 = map(int, box)  # Convertir coordenadas a enteros
            cv2.rectangle(frame_detecciones, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Recuadro verde para personas
            cv2.putText(frame_detecciones, "person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convertir el frame a RGB y mostrar en Streamlit
        frame_rgb = cv2.cvtColor(frame_detecciones, cv2.COLOR_BGR2RGB)
        video_container.image(frame_rgb, channels="RGB", use_column_width=True)

        # Actualizar inventario
        if st.session_state.inventario_actualizado:
            mostrar_inventario(inventario_container)
            st.session_state.inventario_actualizado = False

        # Mostrar conteo de personas
        mensaje_container.write(f"Personas detectadas: {conteo_personas}")

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
