import time
import streamlit as st
import cv2
from ultralytics import YOLO  # YOLOv8
import numpy as np

# Cargar el modelo YOLOv8 entrenado
model = YOLO('C:/Users/josem/OneDrive/Escritorio/Parcial 2/Parcial 2/best (3).pt')

# Nombre e icono de la pagina
st.set_page_config(
    page_title="Proyecto corte 2",
    page_icon=""
)

# Se muestra el logo de D1
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Tiendas_D1_logo.svg/768px-Tiendas_D1_logo.svg.png",
         width=200)

# Se personaliza el titulo con un estilo
st.markdown(
    "<h1 style='color: white;'>Bienvenido al inventario de tiendas D1 - Detección de compras y/o hurtos</h1>",
    unsafe_allow_html=True)

st.write("Sistema en tiempo real para la detección de personas y productos utilizando un modelo YOLOv8.")

# Inventario inicial de los productos (sin detecciones al empezar)
inventario = {
    'yogurt-yogoyogo': {'cantidad': 0, 'imagen': 'https://cdn-icons-png.flaticon.com/128/1047/1047469.png'},
    'Papas-margarita-pollo': {'cantidad': 0, 'imagen': 'https://cdn-icons-png.flaticon.com/128/3050/3050268.png'},
    'coca-cola': {'cantidad': 0, 'imagen': 'https://cdn-icons-png.flaticon.com/128/5718/5718243.png'},
    'crema-colgate': {'cantidad': 0, 'imagen': 'https://cdn-icons-png.flaticon.com/128/1386/1386860.png'}
}

# Contador de detección para cada producto para compararlo con los nuevos productos detectados en cada frame
conteo_productos = {
    'yogurt-yogoyogo': 0,
    'Papas-margarita-pollo': 0,
    'coca-cola': 0,
    'crema-colgate': 0
}

# Variable para detectar si hay una persona en el frame anterior
persona_detectada_anteriormente = False

# Crear el contenedor vacío para el video que es dinámico y se actualiza por cada frame
video_container = st.empty()

# Crear el contenedor vacío para el inventario que es dinámico y se actualiza con cada detección
inventario_container = st.empty()

# Contenedor para mostrar el mensaje de "Compra realizada"
mensaje_container = st.empty()

# Usar la cámara para la detección en tiempo real
cap = cv2.VideoCapture(1)

# Función para mostrar el inventario con barras de progreso, de 0 a 10 productos, irá cambiando el color de rojo a verde respectivamente
def mostrar_inventario():
    with inventario_container.container():
        st.subheader("Inventario Actual")
        for producto, info in inventario.items():
            st.image(info['imagen'], width=50)
            st.markdown(f"<strong>{producto}</strong>", unsafe_allow_html=True)
            progreso = info['cantidad'] / 10  # Supongamos que 10 es la cantidad máxima
            barra_color = "green" if info['cantidad'] >= 5 else "orange" if info['cantidad'] >= 2 else "red"
            st.progress(progreso)
            st.markdown(f"<span style='color:{barra_color};'>{info['cantidad']} unidades</span>",
                        unsafe_allow_html=True)

# Función para detectar en tiempo real los objetos del inventario
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
        detecciones_frame_actual = {'yogurt-yogoyogo': 0, 'Papas-margarita-pollo': 0, 'coca-cola': 0, 'crema-colgate': 0}
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
            mostrar_inventario()

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
