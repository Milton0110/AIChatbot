import os
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing import Annotated, List, TypedDict

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

st.set_page_config(page_title="NutriGuía", page_icon="🥗")

# Rutas resueltas relativas a este archivo (no al directorio de trabajo), para que la app
# funcione igual sea cual sea el cwd desde el que se lance `streamlit run`.
PROYECTO_DIR = Path(__file__).resolve().parent
CHROMA_DIR = PROYECTO_DIR / "chroma_db"
ENV_PATH = PROYECTO_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)
try:
    secreto = st.secrets.get("GOOGLE_API_KEY")
except Exception:
    secreto = None
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or secreto
if not GOOGLE_API_KEY:
    st.error(
        "Falta GOOGLE_API_KEY. Configúrala en .env (ejecución local) o en "
        "los secrets de Streamlit Cloud (despliegue público)."
    )
    st.stop()
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Mismo system prompt que el notebook (agente_nutricion.ipynb, sección 3), duplicado a
# propósito: el notebook debe quedar autocontenido para su entrega y esta app es un
# artefacto de despliegue independiente.
SYSTEM_PROMPT = """Eres NutriGuía, un asistente experto en nutrición y planificación de comidas para personas adultas.

Tu conocimiento se apoya en el contexto recuperado de una base de conocimiento con guías oficiales
(AESAN, SENC/FESNAD, EFSA, USDA/HHS, OMS y FAO/WHO/UNU). Usa siempre ese contexto como fuente
principal de verdad. Si el contexto no contiene información suficiente para responder con
seguridad, dilo explícitamente antes de dar cualquier orientación general adicional.

Comportamiento que debes seguir:
1. Personalización: cuando el usuario pida un plan de comidas o sus necesidades calóricas, solicita
   (si aún no las tienes) su edad, sexo, peso, altura y nivel de actividad física. Calcula su Tasa
   Metabólica Basal y su Gasto Energético Total con las ecuaciones y factores de actividad de la
   fuente FAO/WHO/UNU, y reparte los macronutrientes dentro de los rangos (AMDR) de EFSA/USDA.
2. Menús: estructura cada menú diario en desayuno, comida, cena y, si procede, snacks, indicando
   alimentos, raciones aproximadas y por qué cumplen las recomendaciones (grupos de alimentos,
   fibra, sal, azúcar, grasas).
3. Límites: no eres un profesional médico ni dietista-nutricionista colegiado. No debes dar
   recomendaciones para patologías, embarazo, menores de edad ni déficits calóricos agresivos; en
   esos casos indica que se debe consultar a un profesional sanitario.
4. Idioma: responde siempre en el mismo idioma en que el usuario te escribe (español o inglés),
   incluso si el contexto recuperado está en el otro idioma.
5. Tono: cercano, claro y motivador, sin tecnicismos innecesarios, citando de forma natural la
   fuente en la que te basas (p. ej. "según las guías de la OMS...").
6. Memoria: usa el historial de la conversación para no repetir preguntas ya respondidas por el
   usuario y para mantener coherencia (p. ej. si ya calculaste sus calorías, reutilízalas después).
"""


class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    context: str


@st.cache_resource(show_spinner="Cargando la base de conocimiento y el agente...")
def cargar_agente():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)

    def retrieve_node(state: AgentState):
        pregunta = state["messages"][-1].content
        docs = retriever.invoke(pregunta)
        contexto = "\n\n".join(
            f"[Fuente: {d.metadata.get('source_name', '?')}] {d.page_content}" for d in docs
        )
        return {"context": contexto}

    def generate_node(state: AgentState):
        system_msg = SystemMessage(content=SYSTEM_PROMPT)
        contexto_msg = SystemMessage(
            content=f"Contexto recuperado de la base de conocimiento:\n{state.get('context', '')}"
        )
        mensajes = [system_msg, contexto_msg] + state["messages"]
        respuesta = llm.invoke(mensajes)
        return {"messages": [respuesta]}

    grafo = StateGraph(AgentState)
    grafo.add_node("retrieve", retrieve_node)
    grafo.add_node("generate", generate_node)
    grafo.add_edge(START, "retrieve")
    grafo.add_edge("retrieve", "generate")
    grafo.add_edge("generate", END)
    return grafo.compile(checkpointer=MemorySaver())


agente = cargar_agente()

st.title("🥗 NutriGuía")
st.caption(
    "Asistente de nutrición y planes de comidas diarios, basado en RAG (ChromaDB) + "
    "Gemini + LangGraph, con memoria de conversación."
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "historial" not in st.session_state:
    st.session_state.historial = []

for autor, texto in st.session_state.historial:
    with st.chat_message(autor):
        st.markdown(texto)

pregunta = st.chat_input("Pregúntame sobre nutrición o pide tu menú diario...")
if pregunta:
    st.session_state.historial.append(("user", pregunta))
    with st.chat_message("user"):
        st.markdown(pregunta)

    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    with st.chat_message("assistant"):
        with st.spinner("Consultando la base de conocimiento y pensando..."):
            resultado = agente.invoke({"messages": [HumanMessage(content=pregunta)]}, config=config)
            respuesta = resultado["messages"][-1].content
        st.markdown(respuesta)
    st.session_state.historial.append(("assistant", respuesta))
