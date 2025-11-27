import re
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


def search_type_agent(question, aux_prompt):
    response = llm.invoke(aux_prompt.format_messages(aux_input=question))
    print("RESPONSE: ", response.content)
    return response.content
    

def normalizar_processos(texto):
    padrao = r"\b\d{5}\.\d{6}/\d{4}-\d{2}\b"

    def normalizar(match):
        original = match.group(0)
        normalizado = re.sub(r"[./-]", "", original)
        return f"{normalizado} (original: {original})"

    return re.sub(padrao, normalizar, texto)


def lexical_search_preprocess(question):
    special_char = ['?', '/', '-', ',', '.', ';']

    question = normalizar_processos(question)

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

aux_prompt_template = """
Você é um assistente especializado em analisar documentos oficiais da Universidade Federal do Piauí (UFPI).
Analisando o seguinte questionamento {aux_input}. Retorne '0' para caso o questionamento demande
uma busca LEXICAL do modelo de RAG e retorne '1' para caso o questionamento demande uma busca
exclusivamente SEMÂNTICA do modelo de RAG.

Uma busca LEXICAL deverá atender à questionamentos que solicitem o acesso a determinada informação
exclusivamente pelo número do ato normativo ou pelo número do processo contido no texto do ato.
Um exemplo fixo e bem definido de número de processo é XXXXX.XXXXXX.XXXX-XX em que X é um dígito
de 0 à 9. Veja exemplos de questionamentos que demandam uma busca LEXICAL do modelo de RAG:
Exemplo 1: 'O que diz o ato de número 120?'
Exemplo 2: 'Do que trata o ato 140?'

Uma busca SEMÂNTICA deverá atender à questionamentos que solicitem o acesso a determinada informação
sem fazer referência ao número do ato normativo ou ao número do processo contido no texto do ato.
Veja exemplos de questionamentos que demandam uma busca SEMÂNTICA do modelo de RAG:
Exemplo 1: 'Quais atos citam André Castelo Branco Soares?'
Exemplo 2: 'O que foi definido, em 2025, em relação ao programa de doutorado do Departamento de Computação?'

De forma concisa e objetiva, atenda ao solicitado inicialmente neste prompt.
"""

main_prompt_template = """
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
main_prompt = ChatPromptTemplate.from_template(main_prompt_template)
aux_prompt = ChatPromptTemplate.from_template(aux_prompt_template)

document_chain = create_stuff_documents_chain(llm, main_prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)
bm25_retrieval_chain = create_retrieval_chain(bm25_retriever, document_chain)

# --- INTERFACE PRINCIPAL ---
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

        sem_lex_search = search_type_agent(question, aux_prompt)

        if sem_lex_search == "1":
            with st.spinner("Consultando (Análise Semântica) a base de conhecimento e gerando a resposta..."):
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
        elif sem_lex_search == "0":
            with st.spinner("Consultando (Análise Lexical) a base de conhecimento e gerando a resposta..."):
                try:            
                    question_proc = lexical_search_preprocess(question)
                    
                    print(question_proc)
                    
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
