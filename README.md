# Asistente Experto en Nutrición y Planes de Comidas

Agente de IA generativa que responde preguntas de nutrición y genera planes de comidas diarios
personalizados para una persona adulta, usando RAG sobre guías oficiales de nutrición, Google
Gemini como LLM/embeddings, ChromaDB como base de conocimiento vectorial y LangGraph como
framework de agente con memoria de conversación.

**App desplegada:** **[nutriguia.streamlit.app](https://nutriguia.streamlit.app/)**

## Dominio elegido

**Nutrición y generación de menús diarios**, cubriendo calorías, macronutrientes y recomendaciones
de una dieta completa y sana para adultos. El agente puede:

- Calcular el Gasto Energético Total (GET) de una persona a partir de su edad, sexo, peso, altura
  y nivel de actividad física.
- Repartir ese GET en macronutrientes dentro de los rangos recomendados.
- Proponer un menú diario (desayuno, comida, cena y snacks) coherente con esos objetivos.
- Responder preguntas generales de nutrición (fibra, agua, sal, azúcar, grupos de alimentos...).

Es un dominio con reglas cuantificables (calorías, macronutrientes, raciones por grupo de
alimentos), lo que se presta bien a RAG combinado con generación estructurada, y admite
personalización real en vez de un menú genérico.

## Base de conocimiento

6 documentos públicos oficiales combinando fuentes españolas/UE y anglosajonas/OMS —ninguna fuente
única cubre calorías + macros + micros + fórmulas de cálculo, así que se combinan para dar
robustez—, en [`data/base_conocimiento/`](data/base_conocimiento/) (detalle y enlaces en
[`fuentes.md`](data/base_conocimiento/fuentes.md)):

1. AESAN (2022) — Recomendaciones dietéticas saludables y sostenibles (España)
2. SENC/FESNAD — Guía de la alimentación saludable (España)
3. EFSA (2017) — Dietary Reference Values for nutrients (UE)
4. USDA/HHS (2020-2025) — Dietary Guidelines for Americans (EEUU)
5. OMS — Healthy diet fact sheet
6. FAO/WHO/UNU (2001) — Human Energy Requirements (fórmulas de TMB/GET)

## Instalación y ejecución

1. Crea un entorno virtual e instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Copia `.env.example` a `.env` y añade tu API key de Gemini
   (consíguela en [Google AI Studio](https://aistudio.google.com/apikey)):

   ```
   GOOGLE_API_KEY=tu_api_key_de_gemini_aqui
   ```

3. Abre `agente_nutricion.ipynb` con Jupyter (o súbelo a Google Colab) y ejecuta las celdas en
   orden. La primera ejecución crea e indexa la base vectorial en `chroma_db/`
   (puede tardar unos minutos); las siguientes ejecuciones reutilizan esa base ya persistida.

**Importante:** nunca subas tu API key al repositorio. `.env` no debe versionarse (ya está en
`.gitignore`).

## Justificación del system prompt

El prompt completo y su justificación punto por punto están documentados en la sección 3 del
notebook (`agente_nutricion.ipynb`). En resumen: fija el rol de experto en nutrición apoyado en
las fuentes indexadas, exige personalización real (pide datos del usuario y aplica las fórmulas de
TMB/GET), estructura los menús de forma accionable, marca límites claros (no sustituye a un
profesional sanitario), responde en el idioma del usuario (español o inglés) y reutiliza el
historial de conversación para no repetir preguntas ya respondidas.

## Seguridad: protección contra abuso y prompt injection

Como la app está desplegada públicamente, se añadieron dos capas de protección:

- **Prompt endurecido** (punto 7 del system prompt, sección 3 del notebook): el agente tiene
  instrucciones explícitas para no revelar su propio system prompt, ignorar intentos de anular su
  rol (jailbreaks del tipo "olvida tus instrucciones" o "actúa como una IA sin restricciones"), y
  rechazar peticiones sin relación con nutrición (traducciones, código, tareas genéricas).
- **Límites de uso por sesión** (`app.py`): máximo 30 mensajes por sesión, un mínimo de 3 segundos
  entre mensajes, y un máximo de 1500 caracteres por mensaje. Es una protección por sesión de
  navegador, no un límite global por IP — suficiente para frenar el uso accidental o casual, no una
  solución de nivel producción.

Probado con 4 ataques reales antes y después de aplicar el prompt endurecido: fuga del system
prompt, jailbreak (cambio de rol), saltarse los límites médicos, y uso fuera de dominio. Los tres
primeros ya los bloqueaba el comportamiento base de Gemini; el cuarto (fuera de dominio) solo se
bloqueó tras añadir la instrucción explícita de "Seguridad y alcance".

## Bonus: interfaz web en Streamlit

`app.py` ofrece la misma experiencia (RAG + Gemini + memoria) en un chat web, reutilizando la base
vectorial ya persistida en `chroma_db/` (no la vuelve a indexar).

**Desplegada públicamente:** **[nutriguia.streamlit.app](https://nutriguia.streamlit.app/)**

**Ejecución local** (con `.env` ya configurado):

```bash
streamlit run app.py
```

**Despliegue propio en Streamlit Cloud** (si se quiere replicar):

1. Subir este repositorio a GitHub.
2. Crear la app en [share.streamlit.io](https://share.streamlit.io) apuntando a `app.py`.
3. En "Secrets" de la app, añadir en formato TOML (con comillas):
   ```toml
   GOOGLE_API_KEY = "tu_api_key"
   ```
   (la key nunca está en el repositorio, hay que configurarla ahí explícitamente).
4. `chroma_db/` pesa ~21 MB (bien por debajo de los límites de GitHub) y ya está incluida en el
   repositorio, así que la app no necesita reconstruirla al desplegarse.

## Flujo de ramas (Git)

El repositorio usa 3 ramas con roles fijos:

- **`master`** — rama base. No se toca directamente; queda como referencia del estado inicial.
- **`dev`** — rama de desarrollo activo. Todo el trabajo nuevo se hace aquí.
- **`prod`** — rama de producción. Solo recibe merges desde `dev` una vez que un cambio está
  confirmado y probado.

Flujo de trabajo: se desarrolla y se commitea en `dev` → cuando algo está listo y verificado, se
mergea `dev` → `prod`. `master` no participa en este flujo, se mantiene como punto de partida fijo.

## Estructura del repositorio

- `agente_nutricion.ipynb` — notebook principal (base de conocimiento, agente RAG, chat, ejemplos).
- `app.py` — interfaz web de Streamlit (bonus).
- `data/base_conocimiento/` — los 6 documentos PDF fuente y su ficha descriptiva (`fuentes.md`).
- `chroma_db/` — base vectorial ya indexada y persistida.
- `requirements.txt`, `.env.example` — dependencias y plantilla de configuración.

## Requisitos

- Python 3.10+
- Cuenta de Google AI Studio con API key de Gemini habilitada
- Dependencias listadas en `requirements.txt`

## Ejemplos de uso

El notebook incluye 5 preguntas de ejemplo documentadas (sección 7) y una demostración explícita
de que la memoria de conversación funciona (sección 5: una pregunta hace referencia directa al
cálculo de calorías de la respuesta anterior). Las salidas de estas celdas ya quedan guardadas en
`agente_nutricion.ipynb` (ejecutado con la base vectorial real), por lo que se pueden ver
directamente abriendo el notebook sin necesidad de ejecutarlo primero.
