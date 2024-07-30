import os
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import time
import base64

# Configurar la página de Streamlit
st.set_page_config(page_title="Cibia", page_icon=":speech_balloon:")

# Título y descripción de la página
# Mostrar el título y la descripción de Cibia con los estilos CSS
st.markdown(
    """
    <div class="cibia-container">
        <h1 class="cibia-title">CIBIA</h1>
        <p class="cibia-description"><strong>Tu aliada inteligente en negocios</strong></p>
    </div>
    """,
    unsafe_allow_html=True
)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener el ID del asistente desde las variables de entorno
assistant_id = os.getenv("ASSISTANT_ID")

# Crear un cliente de OpenAI utilizando la API key
client = OpenAI(
   api_key=os.getenv("OPENAI_API_KEY"),
)

# Imágenes de perfil para el asistente y el usuario
# Directorio donde se encuentra app.py
script_dir = os.path.dirname(__file__)

# Ruta al archivo CSS personalizado
css_path = os.path.join(script_dir, 'style.css')

# Leer el contenido del archivo CSS
with open(css_path, 'r') as f:
    custom_css = f.read()

# Leer la imagen del asistente en formato Base64
with open(os.path.join(script_dir, '..', 'img', 'chat_bot.png'), 'rb') as f:
    assistant_image = base64.b64encode(f.read()).decode()

#Leer la img de Usuario
user_image_path = os.path.join(script_dir, '..', 'img', 'User.png')

# Leer la imagen del usuario en formato Base64
with open(user_image_path, 'rb') as f:
    user_image = base64.b64encode(f.read()).decode()

# Agregar una imagen a la barra lateral
sidebar_image_path = os.path.join(script_dir, '..', 'img', 'chat_bot.png')
sidebar_image_base64 = base64.b64encode(open(sidebar_image_path, "rb").read()).decode()

st.sidebar.markdown(f"""
<div class="sidebar-image-container">
    <img src="data:image/png;base64,{sidebar_image_base64}" class="sidebar-image" alt="Sidebar Image">
</div>
""", unsafe_allow_html=True)

# Insertar el CSS personalizado en la aplicación de Streamlit
st.markdown(f'<style>{custom_css}</style>', unsafe_allow_html=True)

# Inicializar el estado de la sesión para el chat
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Iniciar el chat al presionar el botón en la barra lateral
if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# Salir del chat y reiniciar el estado al presionar el botón de salir
if st.button("Exit Chat"):
    st.session_state.messages = []  # Limpiar el historial de mensajes
    st.session_state.start_chat = False  # Reiniciar el estado del chat
    st.session_state.thread_id = None

# Si el chat ha comenzado
if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4o"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar los mensajes en la interfaz
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.markdown(f"""
                <div class="chat-message">
                    <img src="data:image/png;base64,{assistant_image}" class="chat-image" alt="Asistente">
                    <div class="chat-text assistant-text">{message["content"]}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message">
                    <img src="data:image/png;base64,{user_image}" class="chat-image" alt="Usuario">
                    <div class="chat-text user-text">{message["content"]}</div>
                </div>
            """, unsafe_allow_html=True)

    # Si se ingresa un nuevo mensaje
    if prompt := st.chat_input("What would you like to say"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Crear un nuevo mensaje en el hilo de la conversación
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Aquí se hace el cambio para usar el asistente que creaste en lugar del "CatGPT"
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id
        )

        # Esperar hasta que el run se complete
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Obtener los mensajes del hilo
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Procesar y mostrar los mensajes del asistente
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            st.markdown(f"""
                <div class="chat-message">
                    <img src="data:image/png;base64,{assistant_image}" class="chat-image" alt="Asistente">
                    <div class="chat-text">{message.content[0].text.value}</div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.write("Click 'Start Chat' to begin.")
