import streamlit as st

# Funcion para configurar la interfaz de streamlit
def configurarStreamlit ():

    # Se muestra el logo de D1
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Tiendas_D1_logo.svg/768px-Tiendas_D1_logo.svg.png",
             width=200)

    # Se personaliza el titulo con un estilo
    st.markdown(
        "<h1 style='color: white;'>Bienvenido al inventario de tiendas D1 - Detección de compras y/o hurtos</h1>",
        unsafe_allow_html=True)

    st.write("Sistema en tiempo real para la detección de personas y productos utilizando un modelo YOLOv8.")