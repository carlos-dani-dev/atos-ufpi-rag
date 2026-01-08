# 🧠 Atos-UFPI-RAG

**Atos-UFPI-RAG** é uma implementação em Python de um sistema de **RAG (Retrieval-Augmented Generation)** que permite realizar consultas inteligentes em dados textuais em pdf de atos normativos da UFPI de 2025, combinando **recuperação de informações** com **geração de respostas** por meio de modelos de linguagem.

Este projeto organiza os principais componentes de um pipeline RAG completo, incluindo preparação de dados, vetorização/embedding e interface de chat.

O projeto se encontra atualmente em fase de execução local para testes e apresentação do funcionamento da interface como projeto final da disciplina de Tópicos em Inteligência Artificial em sala de aula.
---

## 🚀 Funcionalidades

✔ Pré-processamento e preparação de dados para RAG
✔ Criação de embeddings para buscas semânticas
✔ Chat interativo com respostas contextualizadas sobre o conjunto de dados
✔ Pipeline modular e fácil de estender

---

## 📦 Estrutura do Projeto

```text
├── data_prep/         # Scripts para coletar e preparar dados brutos
├── embedder/          # Geração de embeddings vetoriais
├── rag_chat/          # Lógica de chat RAG para perguntas e respostas
├── requirements.txt   # Dependências Python
```

---

## 🛠 Instalação

Clone o repositório:

```bash
git clone https://github.com/carlos-dani-dev/atos-ufpi-rag.git
cd atos-ufpi-rag
```

Crie um ambiente virtual (recomendado):

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🧩 Como usar

### 📌 1. Preparar os dados

Execute em ordem os seguintes arquivos para limpar e organizar os textos antes de criar os embeddings.

```bash
python data_prep/atos_scrapper.py
```
```bash
python data_prep/atos_to_csv.py
```
```bash
python data_prep/to_md.py
```

### 📌 2. Criar Embeddings

Use o módulo `embedder` para gerar vetores a partir dos textos preparados. Para isso, acesse o collab para download da pasta zipada faiss_index.
A pasta descompactada deve ser anexada à pasta rag_chat antes da execução da 3ª parte do caso de uso definido.

### 📌 3. Chat RAG

Inicie a interface de chat localmente para fazer perguntas com base no conteúdo indexado.

```bash
python rag_chat/main.py
```

O script irá:

* carregar os embeddings
* realizar buscas semânticas e léxicas
* disparar o modelo de geração para formular respostas

---

## 📌 Exemplo de Pergunta

Após iniciar o chat você pode perguntar, por exemplo:

```
> Qual é o conteúdo principal dos documentos?
```

E o sistema retornará uma resposta gerada com base nos textos processados.

---

## 📁 Estruturas de Dados

| Pasta        | Objetivo                                   |
| ------------ | ------------------------------------------ |
| `data_prep/` | Scripts de extração e limpeza de dados     |
| `embedder/`  | Construção e gerenciamento de embeddings   |
| `rag_chat/`  | Interface de perguntas e respostas com RAG |

---
