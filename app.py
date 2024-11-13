import streamlit as st

st.set_page_config(
    page_title="Proyecto corte 2",
    page_icon=""
)
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

# Definir variables a utilizar, entre ellas arreglo de contador de detección para cada producto
# para compararlo con los nuevos productos detectados en cada frame, y boleano de persona detectada
conteo_productos = {
    'yogurt-yogoyogo': 0,
    'Papas-margarita-pollo': 0,
    'coca-cola': 0,
    'crema-colgate': 0
}
persona_detectada_anteriormente = False
cap = cv2.VideoCapture(0)


def deteccion_tiempo_real():
    global persona_detectada_anteriormente

    # Estado de productos/persona en el frame anterior
    productos_anteriores = {'yogurt-yogoyogo': 0, 'Papas-margarita-pollo': 0, 'coca-cola': 0, 'crema-colgate': 0}
    persona_antes = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("No se puede acceder a la cámara.")
            break

        results = model(frame)

        # Contadores temporales de los productos detectados en este frame
        detecciones_frame_actual = {'yogurt-yogoyogo': 0, 'Papas-margarita-pollo': 0, 'coca-cola': 0,
                                    'crema-colgate': 0}
        persona_detectada = False

        for result in results:
            for obj in result.boxes.data:
                clase = int(obj[5])
                etiqueta = model.names[clase]
                confianza = obj[4]  # Confianza de la detección

                # Aplicar la confianza para filtrar detecciones (si es >= 0.5)
                if confianza >= 0.2:
                    # Si se detecta una persona
                    if etiqueta == 'person':
                        persona_detectada = True

                    # Si se detectan productos
                    if etiqueta in detecciones_frame_actual:
                        detecciones_frame_actual[etiqueta] += 1

        # Comparar los productos detectados en este frame con el inventario actual
        inventario_actualizado = False
        for producto, cantidad_detectada in detecciones_frame_actual.items():
            cantidad_anterior = conteo_productos[producto]

            # Si la cantidad detectada cambia, ajustar el inventario
            if cantidad_detectada > cantidad_anterior:
                inventario[producto]['cantidad'] += (cantidad_detectada - cantidad_anterior)
                inventario_actualizado = True
            elif cantidad_detectada < cantidad_anterior:
                inventario[producto]['cantidad'] -= (cantidad_anterior - cantidad_detectada)
                inventario_actualizado = True

            # Actualizar el conteo de productos para el próximo frame
            conteo_productos[producto] = cantidad_detectada

        # Si el inventario se ha actualizado, mostrarlo
        if inventario_actualizado:
            mostrar_inventario(inventario_container)

        # Si la persona desaparece y uno o varios productos también desaparecen, mostrar el mensaje de "Compra realizada"
        if persona_antes and not persona_detectada:
            for producto, cantidad in conteo_productos.items():
                if cantidad == 0 and productos_anteriores[producto] > 0:
                    with mensaje_container:
                        st.warning(f"Compra realizada del producto {producto}")
                        time.sleep(2)
                    break

        # Guardar el estado actual para el próximo frame
        productos_anteriores = detecciones_frame_actual.copy()
        persona_antes = persona_detectada

        # Mostrar los resultados en el frame
        frame = results[0].plot()

        # Convertir BGR a RGB para mostrarlo correctamente en Streamlit
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Mostrar el frame actual en el contenedor
        video_container.image(frame_rgb, channels="RGB", use_column_width=True)

        # Delay para que no capture tan rápido
        time.sleep(0.1)


    cap.release()


# Botón para iniciar la detección
if st.button("Iniciar Detección"):
    deteccion_tiempo_real()

# Botón para detener la detección
if st.button("Detener Detección"):
    cap.release()

chat()