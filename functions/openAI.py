from utils import chatCompletion
from gtts import gTTS
import speech_recognition as sr


import streamlit as st

def listen_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Escuchando...")
        audio = recognizer.listen(source)
    try:
        user_input = recognizer.recognize_google(audio, language="es-ES")
        st.write(f"Has dicho: {user_input}")
        return user_input
    except sr.UnknownValueError:
        st.write("No se pudo entender el audio.")
        return ""
    except sr.RequestError as e:
        st.write(f"Error de reconocimiento de voz: {e}")
        return ""


# Callback para actualizar el input del usuario
def submit(inventario):
    user_input = st.session_state.user_input
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        print(inventario)
        bot_response = chatCompletion(user_input, st.session_state.messages, inventario)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        text_to_speech(bot_response)
        st.session_state.user_input = ""

def text_to_speech(text):
    tts = gTTS(text=text, lang='es')
    tts.save("response.mp3")
    # Reproducir el archivo de audio generado
    audio_file = open("response.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3", start_time=0, autoplay=True)
    audio_file.close()

def chat(inventario):

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

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


    # Capturar la entrada del usuario con un botón para audio
    if st.button("🎤 Escuchar"):
        # Llamar a la función para escuchar audio y actualizar el input del usuario
        print("Escuchando audio")
        audio_input = listen_audio()
        print("Audio escuchado")
        if audio_input:
            st.session_state.user_input = audio_input
            submit(inventario)

    st.text_input("Escribe tu mensaje:", key="user_input", on_change=submit(inventario))


    # if prompt:
    #     with st.chat_message("user"):
    #         st.write(prompt)

    #     response = chatCompletion(prompt, st.session_state.messages, inventario)
    #     st.session_state.messages.append({"role": "user", "content": prompt})


    #     with st.chat_message("assistant"):
    #             st.write(response)
    #     st.session_state.messages.append({"role": "assistant", "content": response})
