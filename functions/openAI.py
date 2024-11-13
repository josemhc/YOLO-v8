from utils import chatCompletion
from gtts import gTTS


import streamlit as st


def text_to_speech(text):
    tts = gTTS(text=text, lang='es')
    tts.save("response.mp3")
    # Reproducir el archivo de audio generado
    audio_file = open("response.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3", start_time=0, autoplay=True)
    audio_file.close()

def chat(inventario):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("Preguntale tus dudas a nuestro esclavo")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    if len(st.session_state.messages) == 0:

        with st.chat_message("assistant"):
            saludo = "Hola, en que te puedo ayudar hoy"
            st.write(saludo)

        st.session_state.messages.append({"role": "assistant", "content": saludo})


    prompt = st.chat_input("Say something")

    if prompt:
        with st.chat_message("user"):
            st.write(prompt)

        response = chatCompletion(prompt, st.session_state.messages, inventario)
        st.session_state.messages.append({"role": "user", "content": prompt})


        with st.chat_message("assistant"):
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        text_to_speech(response)
