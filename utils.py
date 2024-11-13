from dotenv import load_dotenv
import os
from openai import OpenAI

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave de API desde la variable de entorno
api_key = os.getenv('OPENAI_API_KEY')

# Usar la clave en la creación del cliente OpenAI
client = OpenAI(api_key=api_key)


# Le indica al modelo la pregunta actual del usuario y le da contexto de la conversacion
# guardandolo en una variable prompt
def chatCompletion(question, historial, inventario):
    prompt = f"""
    Debes responder a las preguntas que realice el usuario, teniendo en cuenta
    el historial de la conversacion y el inventario de productos (no es necesario brindar imagenes):

    pregunta:
    {question}

    historial:
    {historial}
    
    inventario:
    {inventario}
    """
    # Utiliza el metodo create para crear una respuesta del modelo de acuerdo al prompt anterior
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente de una tienda de productos llamada 'D1'"},
            {"role": "user", "content": f"{prompt}"}
        ]
    )
    return completion.choices[0].message.content
