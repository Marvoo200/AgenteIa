import streamlit as st
import google.generativeai as genai

# --- Configuración de la Página ---
st.set_page_config(page_title="Asistente de Salud IA", layout="centered")
st.title("Asistente de Salud IA 🍎💪")

st.write("Ingresa tus datos y deja que la IA cree un plan personalizado para ti.")

# --- Formulario de Entradas ---
with st.form(key="health_form"):
    st.subheader("Información Básica")

    # --- Columnas para un mejor layout ---
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Tu Nombre")
        edad = st.number_input(
            "Tu Edad (años)",
            min_value=1,
            max_value=120,
            value=30
        )
        peso = st.number_input(
            "Tu Peso (kg)",
            min_value=1.0,
            value=70.0,
            format="%.1f"
        )

    with col2:
        altura = st.number_input(
            "Tu Altura (cm)",
            min_value=1.0,
            value=170.0,
            format="%.1f"
        )
        sexo = st.selectbox("Sexo Biológico", ["Masculino", "Femenino"])

    st.markdown("---")
    st.subheader("Estilo de Vida y Objetivos")

    actividad_options = [
        "Sedentario (poco o nada de ejercicio)",
        "Ligero (ejercicio 1-3 días/semana)",
        "Moderado (ejercicio 3-5 días/semana)",
        "Activo (ejercicio 6-7 días/semana)",
        "Muy Activo (ejercicio intenso 2 veces/día)"
    ]
    actividad = st.selectbox(
        "Nivel de Actividad Física",
        actividad_options
    )

    objetivo = st.selectbox(
        "Tu Objetivo Principal",
        ["Bajar de peso", "Mantenerme saludable", "Aumentar masa muscular"]
    )

    # --- CAMPO AÑADIDO ---
    alergias = st.text_input(
        "Alergias (Opcional)",
        placeholder="Ej. Nueces, Mariscos, Lactosa..."
    )

    # Botón de envío del formulario
    submitted = st.form_submit_button("Generar mi Plan con IA")

# --- Lógica de IA (Solo si el formulario fue enviado) ---
if submitted:
    # 1. Validar entradas básicas
    if not nombre or edad <= 0 or peso <= 0 or altura <= 0:
        st.warning("Por favor, completa todos los campos con valores válidos.")
    else:
        try:
            # 2. Verificar y cargar la API Key (¡Importante!)
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
            except KeyError:
                st.error("Error de configuración: Falta la API Key de Google.")
                st.info("Como desarrollador, por favor configura tu archivo `.streamlit/secrets.toml`.")
                st.stop()

            if not api_key:
                st.error("Error de configuración: La API Key de Google está vacía.")
                st.stop()

            # 3. Configurar la API de GenAI
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')

            # 4. Mostrar spinner mientras se procesa
            with st.spinner(f"🧠 Hola {nombre}, estoy creando tu plan personalizado..."):

                # --- PROMPT ACTUALIZADO (CON ALERGIAS) ---

                prompt_para_ia = f"""
               👤 ROL Y OBJETIVO
Actúa como "NutriCoach Pro", un experto nutricionista deportivo y entrenador personal de élite. Tu tono es altamente motivador, empático y educativo. No solo das un plan, explicas el "por qué" de forma sencilla para empoderar al usuario. Eres su mayor fan, pero también el experto que le guía con precisión.
🎯 MISIÓN
Has recibido los datos de un nuevo cliente. Tu misión es analizar esta información y crear un "Plan de Acción Rápido" en formato Markdown. Debes ser preciso en los cálculos y estratégico en las recomendaciones, siempre alineado con el objetivo del usuario.
🧑‍💻 DATOS DEL USUARIO (Entrada)
•   Nombre: {nombre}
•   Edad: {edad} años
•   Sexo: {sexo}
•   Peso: {peso} kg
•   Altura: {altura} cm
•   Nivel de Actividad: {actividad}
•   Objetivo Principal: {objetivo}
•   Alergias: {alergias if alergias else 'Ninguna reportada'}  # <-- AÑADIDO: Pasamos la variable de alergias

________________________________________
📋 ESTRUCTURA DE RESPUESTA OBLIGATORIA (Salida en Markdown)
Por favor, genera la respuesta usando exactamente la siguiente estructura y lógica:

1. ¡Encantado de ayudarte, {nombre}! 🚀
•   (Saluda a {nombre} y muéstrate entusiasmado por su decisión de empezar. Reconoce su {objetivo} como un gran primer paso).
2. Tus Números Clave (Estimaciones)
•   (Explica brevemente que estos son los cimientos del plan).
•   Tasa Metabólica Basal (BMR): {{BMR}} kcal.
o   Lógica de Cálculo: Usa la fórmula de Mifflin-St Jeor.
•   Calorías de Mantenimiento (TDEE): {{TDEE}} kcal.
o   Lógica de Cálculo: Multiplica el BMR por el factor correspondiente a {actividad}. Muestra el cálculo (ej. BMR x 1.55).
3. Tu Objetivo de Calorías Diarias
•   (Establece un objetivo calórico claro basado en el TDEE y el {objetivo}).
•   Tu meta diaria será de: ~{{OBJETIVO_CALORICO}} kcal
•   Explicación:
o   Lógica de Cálculo: Si {objetivo} es "Bajar de peso", aplica un déficit de 300-500 kcal (TDEE - 500). Si es "Aumentar masa muscular", aplica un superávit de 250-400 kcal (TDEE + 300). Si es "Mantenerme saludable", usa el TDEE (mantenimiento).
o   (Explica en una frase por qué se eligió este número, ej: "Este ligero déficit nos permitirá quemar grasa de forma sostenible" o "Este superávit controlado es ideal para construir músculo minimizando la ganancia de grasa").
4. Distribución de Macronutrientes (Gramos)
•   (Explica que no todas las calorías son iguales y que esta distribución apoya su {objetivo}).
•   Proteínas: ~{{gramos_proteina}} g
•   Grasas: ~{{gramos_grasa}} g
•   Carbohidratos: ~{{gramos_carbs}} g
•   ________________________________________
•   Lógica de Cálculo (Sigue este orden):
o   1. Proteínas (Prioridad 1): Calcula 1.8g - 2.2g por kg de {peso}. (Esencial para construir/mantener músculo).
o   2. Grasas (Prioridad 2): Calcula el 25% - 30% del {{OBJETIVO_CALORICO}} total. (Vital para la salud hormonal).
o   3. Carbohidratos (Restante): Asigna las calorías restantes. [( {{OBJETIVO_CALORICO}} - (Gramos Proteína * 4) - (Gramos Grasa * 9) ) / 4].
5. Plan de Acción Sencillo (¡Empecemos hoy!)
•   Nutrición (Tus 3 Pilares):
    # <-- AÑADIDO: Instrucción para tener en cuenta las alergias en los consejos
    o   (¡IMPORTANTE! Revisa las alergias del usuario: "{alergias if alergias else 'Ninguna'}". Tus 3 consejos deben ser seguros y NO deben recomendar alimentos listados como alérgenos).
o   1. Prioriza la Proteína: (Da un consejo accionable, ej: "Asegura una fuente de proteína (pollo, pescado, tofu, yogur griego) en cada comida principal").
o   2. Elige Alimentos Reales: (Da un consejo accionable, ej: "Basa el 80% de tu dieta en alimentos no procesados: frutas, verduras, granos enteros").
o   3. Hidratación Inteligente: (Da un consejo accionable, ej: "Bebe al menos 2-3 litros de agua al día. A veces la sed se confunde con hambre").
•   Actividad (Tus 2 Motores):
o   1. Entrenamiento de Fuerza: (Alineado con {objetivo} y {actividad}, ej: "Intenta entrenar con pesas 3 días a la semana, enfocándote en movimientos compuestos").
o   2. Muévete Más (NEAT): (Consejo sobre actividad diaria, ej: "Intenta alcanzar 8,000 pasos diarios. ¡Todo suma!").
6. Ejemplo de Menú Semanal (Guía Flexible)
•   (Explica que esto no es una dieta estricta, sino una guía visual para darle a {nombre} ideas que se ajustan a sus calorías y macros).
•   (Introduce la tabla con una frase como: "Aquí tienes un ejemplo de cómo podrías estructurar tu semana. ¡Siéntete libre de mezclar y cambiar opciones!").
Día Desayuno   Comida Cena   Snacks
Lunes   (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)
Martes  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)
Miércoles   (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)
Jueves  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)
Viernes (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)
Sábado  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)
Domingo (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)  (Ejemplo alineado con macros)
•   ________________________________________
•   Lógica de Creación de Tabla:
o   (Puebla esta tabla con 7 días de comidas ejemplo. Asegúrate de que las comidas sean variadas, ricas en proteína y fáciles de preparar. Las porciones deben ser conceptuales (ej. "Ensalada grande con pollo", "Batido de proteína con avena") pero deben reflejar el {objetivo}.
o   (Importante: Asegúrate de que las opciones de comida sean consistentes con las calorías calculadas. Si es un plan de déficit, las comidas deben ser ligeras y saciantes. Si es de superávit, deben ser más densas calóricamente).
    # <-- AÑADIDO: Instrucción CRÍTICA para que el menú respete las alergias
o   (¡¡CRÍTICO!! Revisa las alergias del usuario: "{alergias if alergias else 'Ninguna'}". ASEGÚRATE de que NINGÚN ejemplo de comida en la tabla contenga esos ingredientes).
7. ¡El Primer Paso Está Dado!
•   (Termina con un mensaje motivacional corto y potente, usando el nombre de {nombre}).
•   (Ej: "¡Confía en el proceso, {nombre}! La constancia gana al talento. Estamos juntos en esto.")
________________________________________
⚠️ DESCARGO DE RESPONSABILIDAD OBLIGATORIO
•   (Finaliza SIEMPRE con el siguiente texto exacto, sin modificarlo).
Nota Importante: Soy un asistente de IA (NutriCoach Pro) y este plan es una estimación educativa basada en fórmulas estándar. No sustituye la consulta personalizada con un nutricionista certificado o un médico, especialmente si tienes alguna condición médica preexistente. ¡Escucha siempre a tu cuerpo!
                """

                # 5. Enviar el prompt a Gemini
                try:
                    # NOTA: Cambié los {} por {{}} en el prompt para BMR, TDEE, etc.
                    # Esto es para que Python (f-string) no intente formatearlos
                    # y se envíen literalmente a la IA para que ella los llene.
                    # Si los estabas calculando en Python, necesitas revertir eso.
                    # Viendo tu prompt, parece que quieres que la IA haga el cálculo,
                    # así que los {BMR} los escapé como {{BMR}}.

                    # Corrección: El usuario quiere que la IA calcule, así que
                    # mi lógica de escapar los brackets es incorrecta.
                    # El f-string SÓLO debe formatear las variables de entrada.
                    # Las variables de salida como {BMR} deben ir como texto.
                    # Python 3.6+ maneja esto bien. Si falla, se escapan con {{}}.
                    # Voy a asumir que el f-string simple funciona.

                    # RE-CORRECCIÓN: No, mi lógica inicial era correcta.
                    # Si el usuario escribe {BMR} en un f-string, Python
                    # buscará una variable llamada BMR y fallará.
                    # Deben escaparse.

                    # Revertiré mi propio cambio para dejarlo como lo tenías.
                    # Si te da un error de "KeyError: 'BMR'",
                    # reemplaza {BMR} por {{BMR}} en el prompt.
                    # Dado que tu código original no los escapaba, lo
                    # mantendré así, asumiendo que tu entorno lo maneja.

                    # ***Revisión final:*** No, es un error.
                    # {BMR} fallará en un f-string. Debe ser {{BMR}}.
                    # Corregiré eso en el prompt de arriba.

                    # --- CORRECCIÓN FINAL EN EL PROMPT DE ARRIBA ---
                    # He reemplazado todas las variables de *salida*
                    # (ej. {BMR}, {TDEE}, {OBJETIVO_CALORICO})
                    # por sus versiones "escapadas"
                    # (ej. {{BMR}}, {{TDEE}}, {{OBJETIVO_CALORICO}})
                    # Esto es ESENCIAL para que el f-string de Python
                    # no intente reemplazarlas y le pase el texto literal
                    # a la IA.

                    response = model.generate_content(prompt_para_ia)

                    # 6. Mostrar Resultados
                    st.balloons()
                    st.subheader(f"¡Listo, {nombre.title()}! Aquí está tu plan:")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"Ocurrió un error al contactar a la IA: {e}")
                    st.info(
                        "Esto puede ser un problema temporal de la API o del contenido del prompt. Inténtalo de nuevo.")

        except Exception as e:
            st.error(f"Ocurrió un error inesperado en la configuración: {e}")