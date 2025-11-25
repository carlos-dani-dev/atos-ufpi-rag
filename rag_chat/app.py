import os
from langchain_text_splitters import MarkdownHeaderTextSplitter
import streamlit as st
from dotenv import load_dotenv

from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain


def lexical_search_preprocess(question):
    special_char = ['?', '/', '-', ',', '.', ';']
    for char in special_char:
        question = question.replace(char, f" {char}")
    return question


load_dotenv()

st.set_page_config(
    page_title="RAG UFPI - Atos da Reitoria",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("RAG para Atos da Reitoria da UFPI")
st.markdown("Consulte os atos oficiais da UFPI usando os modelos de embedding da Qwen e LLMs do OpenRouter.")

# --- INTERFACE DA SIDEBAR ---
search_type_choice = None
with st.sidebar:
    st.header("⚙️ Configurações")
    model_id = st.selectbox(
        "🤖 Escolha um Modelo LLM",
    ["deepseek/deepseek-chat-v3.1:free", "qwen/qwen3-235b-a22b:free", "deepseek/deepseek-r1-0528:free", "openai/gpt-oss-120b:free", "openai/gpt-oss-20b:free", "qwen/qwen3-coder:free", "moonshotai/kimi-k2:free", "google/gemini-2.5-pro-exp-03-25", "google/gemma-3-flash-e2b-it:free"],
        index=0,
        help="Escolha o modelo de linguagem que irá gerar as respostas."
    )
    
    search_type_choice = st.selectbox(
        "🔍 Tipo de Busca",
        ["Semântica (Qwen 0.6B Embedding)", "Lexical (BM25)"],
        index=0,
        help="Escolha entre busca por similaridade vetorial (semântica) ou por palavras-chave (lexical)."
    )

    st.markdown("---")
    st.write("")
    st.header("Ajuste de Parâmetros da LLM:")
    st.write("")
    st.write("")
    
    
    temperature = st.slider("🌡️ Temperatura", 0.0, 1.5, 0.0, help="Define a criatividade do modelo.")

    k = st.slider("Resultados Finais:", 3, 15, 15, help="Número de documentos que o LLM usará.")
    #fetch_k = st.slider("Documentos Pré-selecionados:", 20, 100, 40, help="Documentos recuperados para MMR.")
    #lambda_mult = st.slider("Diversidade:", 0.0, 1.0, 1.0, help="0.0 para relevância, 1.0 para diversidade.")
    
# --- LÓGICA DE CARREGAMENTO COM CACHE ---
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
    
    index_path = "../embedder/faiss_index_2"
    if not os.path.isdir(index_path):
        st.error(f"Pasta do índice ('{index_path}') não encontrada. Certifique-se de descompactar o arquivo do Colab aqui.")
        return None, None
        
    vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    st.session_state.embeddings_loaded = True
    return embeddings, vector_store

embeddings_model, vector_store = load_components()

if vector_store is None:
    st.stop()

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": k}
)

headers_to_split_on = [("#", "Ato")]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
with open("../data_prep/atos_md.txt", "r", encoding="utf-8") as f:
    md_content = f.read()
docs_por_ato = markdown_splitter.split_text(md_content)

bm25_retriever = BM25Retriever.from_documents(
    docs_por_ato, k=k)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    st.warning("A chave da API OpenRouter não foi encontrada no arquivo `.env`.")
    st.stop()

llm = ChatOpenAI(
    openai_api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    model_name=model_id,
    temperature=temperature,
    max_tokens=2048,
)

prompt_template = """
Você é um assistente especializado em analisar documentos oficiais da Universidade Federal do Piauí (UFPI).
Responda à pergunta do usuário com base EXCLUSIVAMENTE no contexto fornecido abaixo.
Se a informação não estiver no contexto, diga "A informação não foi encontrada nos atos fornecidos.".
Seja claro, objetivo e cite os números dos atos e processos que basearam sua resposta.

**Contexto:**
{context}

**Pergunta:**
{input}

**Resposta Detalhada:**
"""
prompt = ChatPromptTemplate.from_template(prompt_template)
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)
bm25_retrieval_chain = create_retrieval_chain(bm25_retriever, document_chain)

# --- INTERFACE PRINCIPAL ---
texto_btn = "Analisar semanticamente"
if search_type_choice == "Semântica (Qwen 0.6B Embedding)" or search_type_choice == None:
    question = st.text_input(
        "Faça sua pergunta sobre os atos da reitoria:",
        placeholder="Ex: Quem foi nomeado para o cargo de Assistente em Administração em junho de 2022?"
    )
    texto_btn = "Analisar semanticamente"
else:
    question = st.text_input(
        "Palavras-chave (Busca Lexical):",
        placeholder="Ex: '2022', 00017.000057/2025-95",
        help="Na busca lexical, digite termos literais presentes nos documentos."
    )
    texto_btn = "Analisar lexicalmente"

if st.button(texto_btn, type="primary"):
    if not question:
        st.warning("Por favor, digite uma pergunta.")
    else:
        if search_type_choice == "Semântica (Qwen 0.6B Embedding)":
            with st.spinner("Consultando a base de conhecimento e gerando a resposta..."):
                try:                
                    docs_with_scores = vector_store.similarity_search_with_score(question, k=k)
                    
                    response = retrieval_chain.invoke({"input": question})
                    
                    st.markdown("### Resposta")
                    st.info(response['answer'])

                    if 'context' in response and response['context']:
                        st.markdown("---")
                        st.markdown("### Fontes Utilizadas")
                        for doc, score in docs_with_scores:
                            metadata = doc.metadata
                            ato = metadata.get("Ato", "N/A")
                            processos = ', '.join(metadata.get('processos', [])) or 'Não identificado'

                            similaridade = 1 / (1 + score)

                            with st.expander(f"**{ato}** - Similaridade: {similaridade:.4f}"):
                                st.caption(f"Processos: {processos}")
                                st.write(doc.page_content)

                                
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")
                    st.error(f"Detalhes do erro: {str(e)}")
        else:
            with st.spinner("Consultando a base de conhecimento e gerando a resposta..."):
                try:
                    question_proc = lexical_search_preprocess(question)
                    
                    docs = bm25_retriever.get_relevant_documents(question_proc)
                    context = "\n\n".join([d.page_content for d in docs])

                    response = bm25_retrieval_chain.invoke({"input":question_proc})

                    st.markdown("### Resposta")
                    st.info(response['answer'])

                    if 'context' in response and response['context']:
                        st.markdown("---")
                        st.markdown("### Fontes Utilizadas")
                        for doc in docs:
                            metadata = doc.metadata
                            ato = metadata.get("Ato", "N/A")
                            processos = ', '.join(metadata.get('processos', [])) or 'Não identificado'


                            with st.expander(f"**{ato}** - Score de similaridade XXX"):
                                st.caption(f"Processos: {processos}")
                                st.write(doc.page_content)

                                
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")
                    st.error(f"Detalhes do erro: {str(e)}")
            

st.markdown("---")
st.caption("Desenvolvido com LangChain, Streamlit e modelos de IA de ponta.")
