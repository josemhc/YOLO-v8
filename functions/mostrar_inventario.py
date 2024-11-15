import streamlit as st

inventario = {
    'yogurt-yogoyogo': {'cantidad': 0, 'precio': '6 lucas', 'imagen': 'https://cdn-icons-png.flaticon.com/128/1047/1047469.png'},
    'Papas-margarita-pollo': {'cantidad': 0, 'precio':'4 lucas','imagen': 'https://cdn-icons-png.flaticon.com/128/3050/3050268.png'},
    'coca-cola': {'cantidad': 0, 'precio':'3 lucas', 'imagen': 'https://cdn-icons-png.flaticon.com/128/5718/5718243.png'},
    'crema-colgate': {'cantidad': 0, 'precio':'6 lucas','imagen': 'https://cdn-icons-png.flaticon.com/128/1386/1386860.png'}
}

def mostrar_inventario(inventario_container):
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