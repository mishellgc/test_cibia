# Este código realiza las siguientes acciones:

# Importa las bibliotecas necesarias para el funcionamiento del programa, incluyendo openai para interactuar con la API de OpenAI, dotenv para cargar variables de entorno, os para acceder a variables de entorno, y streamlit para crear una interfaz web.
# Carga las variables de entorno del archivo .env para acceder a la clave de API de OpenAI.
# Inicializa un cliente de OpenAI con la clave de API obtenida de las variables de entorno.
# Establece el título de la aplicación web como "Cibia".
# Verifica si la lista de mensajes no existe en el estado de la sesión de Streamlit. Si no existe, la inicializa con un mensaje de bienvenida del asistente.
# Itera sobre los mensajes almacenados en el estado de la sesión y los muestra en la interfaz web como mensajes de chat.
# Espera a que el usuario ingrese un mensaje a través de un campo de entrada de chat. Cuando se recibe un mensaje:
# Añade el mensaje del usuario al estado de la sesión.
# Envía el mensaje del usuario a la API de OpenAI, junto con los mensajes previos, para obtener una respuesta.
# Añade la respuesta de la IA al estado de la sesión y la muestra en la interfaz web como un mensaje del asistente.
# En resumen, este código crea una interfaz de chat web donde los usuarios pueden interactuar con una IA (utilizando la API de OpenAI), y mantiene un registro de la conversación en el estado de la sesión de Streamlit.

from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

client = OpenAI(
   api_key=os.getenv("OPENAI_API_KEY"),
)

st.title("Cibia")

if "messages" not in st.session_state:
  st.session_state["messages"] = [{"role": "assistant", "content": "Hola, soy Cibia la IA de CIB, ¿En qué puedo ayudarte?"}]

for msg in st.session_state["messages"]:
  st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input():
  st.session_state["messages"].append({"role": "user", "content": user_input})
  st.chat_message("user").write(user_input)
  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=st.session_state["messages"]
  )
  responseMessage = response.choices[0].message.content
  st.session_state["messages"].append({"role": "assistant", "content": responseMessage})
  st.chat_message("assistant").write(responseMessage)
