import re
import os
import time
from langchain_text_splitters import MarkdownHeaderTextSplitter
import streamlit as st
from dotenv import load_dotenv

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


def lexical_retriever_instance():
    headers_to_split_on = [("#", "Ato")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    with open("../data_prep/atos_md.txt", "r", encoding="utf-8") as f:
        md_content = f.read()
    docs_por_ato = markdown_splitter.split_text(md_content)

    return BM25Retriever.from_documents(docs_por_ato, k=k)
    

def normalizar_processos(question):
    padrao = r"\b(\d{5})[.\s]?(\d{6})[.\s]?(\d{4})[-\s]?(\d{2})\b"
    match = re.search(padrao, question)

    if match:
        normalizado = "".join(match.groups())
        original = match.group(0)
        return question.replace(original, normalizado)

    print("Padrão não encontrado!")
    return question


def lexical_search_preprocess(question):
    special_char = ['/', '-', ',', '.', ';']

    question = question.replace('?', ' ?')
    #question = question.replace('/', ' /')

    question = normalizar_processos(question)

    for char in special_char:
        question = question.replace(char, f"")

    print("question: ", question)

    return question

main_prompt_template = """
Você é um assistente especializado em analisar documentos oficiais da Universidade Federal do Piauí (UFPI).
Responda à pergunta do usuário com base EXCLUSIVAMENTE no contexto fornecido abaixo.
Se a informação não estiver no contexto, diga "A informação não foi encontrada nos atos fornecidos.".
Seja claro, objetivo e cite os números dos atos e processos que basearam sua resposta.

**Contexto:**
{context}

**Pergunta:**
{input}

Além disso, é importante destacar que algumas palavras possuem sinônimos que devem conduzir igualmente a
sua resposta à pergunta. Por exemplo:
- lotar e lotado: cargo, exercer cargo, participar, integrar
- membro: integrante, funcionário

**Resposta Detalhada:**
"""


load_dotenv()

st.set_page_config(
    page_title="RAG UFPI - Atos da Reitoria",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("RAG para Atos da Reitoria da UFPI")
st.markdown("Consulte os atos oficiais da UFPI usando os modelos de embedding da Qwen e LLMs do OpenRouter.")


search_type_choice = None
with st.sidebar:
    st.header("⚙️ Configurações")
    model_id = st.selectbox(
        "🤖 Escolha um Modelo LLM",
    ["openai/gpt-oss-20b:free", "qwen/qwen3-coder:free", "x-ai/grok-4.1-fast:free", ],
        index=0,
        help="Escolha o modelo de linguagem que irá gerar as respostas."
    )

    st.markdown("---")
    st.write("")
    st.header("Ajuste de Parâmetros da LLM:")
    st.write("")
    
    temperature = st.slider("🌡️ Temperatura", 0.0, 1.5, 0.0, help="Define a criatividade do modelo.")

    k = st.slider("Resultados Finais:", 3, 15, 15, help="Número de documentos que o LLM usará.")


class Embeddings(Embeddings):
    
    def __init__(self, device="cpu"):
        self.model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", device=device)

    def embed_documents(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text):
        return self.model.encode([text], prompt_name="query", normalize_embeddings=True)[0].tolist()


# Inicializa o estado da sessão para controlar a mensagem de carregamento
if 'embeddings_loaded' not in st.session_state:
    st.session_state.embeddings_loaded = False


@st.cache_resource
def load_components():
    """Função única para carregar todos os componentes pesados."""
    
    embeddings = Embeddings(device="cpu")
    
    index_path = "../embedder/faiss_index"
    if not os.path.isdir(index_path):
        st.error(f"Pasta do índice ('{index_path}') não encontrada. Certifique-se de descompactar o arquivo do Colab aqui.")
        return None, None
        
    vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    st.session_state.embeddings_loaded = True
    return embeddings, vector_store


embeddings_model, vector_store = load_components()

if vector_store is None:
    st.stop()

qwen_semantic_retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": k})
bm25_lexical_retriever = lexical_retriever_instance()

hybrid_retriever = EnsembleRetriever(
    retrievers=[qwen_semantic_retriever, bm25_lexical_retriever],
    weights=[0.65, 0.35]  # pode ajustar depois
)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    st.warning("A chave da API OpenRouter não foi encontrada no arquivo `.env`.")
    st.stop()

llm_rag_response = ChatOpenAI(
    openai_api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    model_name=model_id,
    temperature=temperature,
    max_tokens=2048,
)

main_prompt = ChatPromptTemplate.from_template(main_prompt_template)

document_chain = create_stuff_documents_chain(llm_rag_response, main_prompt)
hybrid_chain = create_retrieval_chain(hybrid_retriever, document_chain)


texto_btn = "Analisar semanticamente"
question = st.text_input(
    "Faça sua pergunta sobre os atos da reitoria:",
    placeholder="Ex: Quem foi nomeado para o cargo de Assistente em Administração em junho de 2022?"
)
texto_btn = "Analisar"

if st.button(texto_btn, type="primary"):
    if not question:
        st.warning("Por favor, digite uma pergunta.")
    else:
        with st.spinner("Consultando a base e gerando resposta..."):
            try:
                question = lexical_search_preprocess(question)
                
                t0 = time.time()
                docs = hybrid_retriever.invoke(question)
                retrieval_time = time.time() - t0
                
                t1 = time.time()
                response = document_chain.invoke(
                    {"context": docs, "input": question}
                )
                generation_time = time.time() - t1

                st.markdown("### Resposta")
                st.info(response)
                
                st.markdown(f"**Tempo de retrieval:**  {retrieval_time:.3f} segundos")
                st.markdown(f"**Tempo de geração (LLM):**  {generation_time:.3f} segundos")

                st.markdown("---")
                st.markdown("### Fontes Utilizadas")

                for doc in docs:
                    metadata = doc.metadata
                    ato = metadata.get("Ato", "N/A")
                    processos = ', '.join(metadata.get('processos', [])) or 'Não identificado'

                    with st.expander(f"**{ato}**"):
                        st.caption(f"Processos: {processos}")
                        st.write(doc.page_content)

            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
            

st.markdown("---")
st.caption("Desenvolvido com LangChain, Streamlit e modelos de IA de ponta.")
