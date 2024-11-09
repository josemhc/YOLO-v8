# Proyecto de Detección de Compras y Hurtos - Tiendas D1

Este proyecto es una aplicación en tiempo real para la detección de personas y productos en tiendas D1 utilizando el modelo YOLOv8, desarrollado con Streamlit. Permite la detección en tiempo real y muestra un inventario de productos detectados.

## Requisitos

- Python 3.8 o superior
- Cámara conectada al equipo para la detección en tiempo real
- Modelo YOLOv8 entrenado (`best (3).pt`), que debe estar en una ubicación accesible en tu sistema.

## Instalación

Sigue estos pasos para clonar el repositorio, crear un entorno virtual y ejecutar la aplicación.

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/josemhc/YOLO-v8.git
   cd YOLO-v8
Crea y activa un entorno virtual (opcional, pero recomendado):

``````
python -m venv .venv
``````

En Windows:
``````
.venv\Scripts\activate
``````

En macOS/Linux:

``````
source .venv/bin/activate
``````

## Instala las dependencias:

``````
pip install -r requirements.txt
``````

## Configura el modelo YOLOv8:

Asegúrate de que el modelo YOLOv8 (best (3).pt) esté disponible en la ruta especificada en app.py.
Si necesitas cambiar la ruta, edita la línea correspondiente en app.py:
``````
model = YOLO('ruta/a/tu/modelo/best (3).pt')
``````

## Ejecución

Para ejecutar la aplicación, usa el siguiente comando:

``````
streamlit run app.py
``````

Una vez ejecutado el comando, abre tu navegador y visita la URL que Streamlit proporciona, generalmente es http://localhost:8501.

## Características

Detección en tiempo real de productos y personas usando un modelo YOLOv8.

Muestra un inventario de productos detectados con una barra de progreso dinámica.

Notificación de "Compra realizada" cuando una persona desaparece del frame y se detecta un cambio en el inventario.

Notas adicionales
Este proyecto requiere conexión a una cámara para la detección en tiempo real.

Las imágenes de los productos y el logotipo se cargan desde URLs. Asegúrate de estar conectado a Internet para visualizarlas correctamente.

Contacto
Para dudas o comentarios, puedes contactar a José.






