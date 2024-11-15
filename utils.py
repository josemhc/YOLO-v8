from dotenv import load_dotenv
import os
from openai import OpenAI

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave de API desde la variable de entorno
api_key = os.getenv('OPENAI_API_KEY2')

# Usar la clave en la creación del cliente OpenAI

client = OpenAI(api_key='OPENAI_API_KEY2')


# Le indica al modelo la pregunta actual del usuario y le da contexto de la conversacion
# guardandolo en una variable prompt
def chatCompletion(question, historial, inventario):
    prompt = f"""
    Debes responder a la pregunta del usuario basándote en el historial de la conversación y la información del inventario de productos.
    
    Si la pregunta se refiere a uno o mas productos, tu respuesta debe basarse solo en el inventario.
    
    Pregunta:
    {question}

    Historial de conversación:
    {historial}
    
    Inventario de productos:
    {inventario}
    
    Tu respuesta debe ser breve y precisa, brindando solo la información necesaria.
    """
    # Utiliza el metodo create para crear una respuesta del modelo de acuerdo al prompt anterior
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente de una tienda de productos llamada 'D1' que se comunica por voz con los clientes"},
            {"role": "user", "content": f"{prompt}"}
        ]
    )
    return completion.choices[0].message.content
