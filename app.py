import streamlit as st
from PIL import Image
import google.generativeai as genai
import io

# --- Configuración de la Página ---
st.set_page_config(page_title="Analizador de Platillos", layout="wide")
st.title("Analizador de Platillos 🍽️")

# --- (SE ELIMINÓ LA BARRA LATERAL) ---
# La API key ahora se carga de forma segura desde los secretos del servidor.
# El usuario final (tu cliente) no necesita ingresar nada.

# --- Cuerpo Principal de la App ---
st.write("Sube la foto de un platillo (JPG, PNG) y la IA analizará sus calorías y nutrición.")

uploaded_file = st.file_uploader(
    "Elige una imagen de comida...",
    type=["jpg", "jpeg", "png"],
    help="Sube un archivo de imagen en formato JPG, JPEG o PNG."
)

if uploaded_file is not None:
    try:
        # Abrir y mostrar la imagen subida
        image = Image.open(uploaded_file)

        st.image(
            image,
            caption=f"Imagen subida: {uploaded_file.name}",
            width=300  # Ajustar ancho para mejor layout
        )

        # Botón para iniciar el análisis
        if st.button("Analizar Platillo"):
            # 1. Verificar si la API Key fue ingresada (desde st.secrets)
            try:
                # Esta línea lee la clave de los secretos de Streamlit
                api_key = st.secrets["GOOGLE_API_KEY"]
            except KeyError:
                # Este error es para ti (el desarrollador), no para el cliente.
                st.error("Error de configuración del servicio: Falta la API Key de Google.")
                st.info("Como desarrollador, por favor configura tu archivo `.streamlit/secrets.toml`.")
                st.stop()

            if not api_key:
                st.error("Error de configuración del servicio: La API Key de Google está vacía.")
                st.info("Como desarrollador, revisa tu archivo `.streamlit/secrets.toml`.")
                st.stop()

            # 2. Configurar la API de GenAI
            try:
                genai.configure(api_key=api_key)
            except Exception as e:
                st.error(f"Error al configurar la API de Google: {e}")
                st.stop()

            # 3. Mostrar spinner mientras se procesa
            with st.spinner("🧠 Analizando la imagen con IA... Esto puede tardar un momento."):
                try:
                    # 4. Convertir imagen a formato compatible (bytes)
                    image_bytes = io.BytesIO()
                    # Guardar como JPEG, ya que es un formato común para la API
                    image.save(image_bytes, format='JPEG')
                    image_bytes = image_bytes.getvalue()

                    # 5. Crear el modelo multimodal
                    model = genai.GenerativeModel(model_name="gemini-2.0-flash")

                    # 6. Crear el prompt (del script del usuario)
                    prompt = """
                    Analiza la imagen de un platillo de comida.

                    1. ¿Qué alimento o platillo aparece en la imagen?
                    2. Estima la cantidad de calorías visibles basándote en el tamaño y la porción.
                    3. Si es posible, incluye una breve descripción nutricional general.

                    Devuélvelo de forma clara para el usuario final en formato Markdown.
                    """

                    # 7. Definir la parte de la imagen para la API
                    image_part = {
                        "mime_type": "image/jpeg",
                        "data": image_bytes
                    }

                    # 8. Enviar imagen y prompt a Gemini
                    response = model.generate_content([prompt, image_part])

                    # 9. Mostrar resultado
                    st.subheader("🧠 Resultado del Análisis:")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Ocurrió un error durante el análisis de IA: {e}")

    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        st.warning("Por favor, intenta subir un archivo de imagen válido.")

else:
    st.info("Esperando a que subas un archivo de imagen.")