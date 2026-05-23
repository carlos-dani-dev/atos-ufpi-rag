# RAG de atos normativos da UFPI

<p>Atos normativos são documentos que regulamentam, instruem e padronizam o funcionamento das atividades da Universidade Federal.</p>
<p>Eles são publicados ao decorrer do tempo e podem tratar os mais variados assuntos. O RAG desenvolvido neste repositório utiliza os modelos de IA generativa mais famosos para responder à perguntas sob contexto.</p>
<p>Veja um exemplo de ato normativo abaixo:</p>
<p align="center"><img width="756" height="234" alt="image" src="https://github.com/user-attachments/assets/270a663e-80ff-4f4b-8e3c-f92e1b37fad9" /></p>

### Tecnologias Utilizadas

* [Python](https://www.python.org/) : A linguagem base de todo o projeto.
* [Streamlit](https://streamlit.io/) : Framework python para crianção da interface gráfica.
* [OpenRouter](https://openrouter.ai/) : Plataforma usada para centralização do acesso às IA's generativas.
* [Langchain](https://www.langchain.com/) : Framework python que sistematiza tanto a produção dos prompts, como a separação do texto base em markdown para posterior vetorização.
* [SenteceTransformers](https://sbert.net/) : Framework python utilizado para o chamamento do modelo que realiza a vetorização do texto base separado.


### Dependências e Versões Necessárias

* langchain : Versão 0.2.11
* langchain-community : Versão 0.2.5
* langchain-text-splitters : Versão 0.2.1

---

### Como rodar o projeto

<p>Para rodar a aplicação é necessário, antes de tudo, solicitar uma chave de api do OpenRouter, configurando-a como parte do arquivo de variáveis de ambiente.
Após isso, siga os passos a seguir:</p>

<p>Entre dentro do diretório atos-ufpi-rag. Você consegue fazê-lo via terminal da seguinte forma:</p>

```
cd ./atos-ufpi-rag
```

<p>Depois disso, rode a aplicação streamlit com o comando abaixo: </p>

```
streamlit run app.py
```

Acesse http://localhost:8000/ e verifique se a aplicação está rodando corretamente.

---

### Informações importantes sobre a aplicação

<p>Abaixo, veja o pipeline detalhado de todo o RAG.</p>
<p>A primeira etapa é a preparação dos dados, que envolve o webscrapping dos atos normativos via script python e salvamento em arquivo csv intermediário. Este arquivo
intermediário é lido e transformado em um arquivo de texto base .txt em formato markdown.</p>
<p>Após isso, o laboratório colab invoca o SentenceTransformer e vetoriza o arquivo .txt em formato markdown, ato por ato. O resultado desse processo é uma pasta zipada
com o Faiss Index (dataset vetorizado nativo da Meta, otimizado para buscas por proximidade).</p>
<p>A etapa final é a busca por semelhança da pergunta vetorizada dentro do dataset vetorizado resultante da etapa anterior. Os atos normativos mais semelhantes compõem
o system prompt que será enviado às IA's generativas por meio da API do OpenRouter. A resposta é exibida ao usuário.</p>

<img width="5901" height="2157" alt="image" src="https://github.com/user-attachments/assets/feea077f-f79c-4f70-a21c-79858ddb49ac" />

### Problemas enfrentados

#### Principal problema da aplicação:
Qual o ponto ótimo de separação do texto base?
Inicialmente vetorizamos batches de tamanho fixo, o que prejudicava o processo de recuperação dos batches por semelhança e retornava um contexto inútil para a IA generativa explorar.
#### Como solucionamos: O tamanho de cada batch passou a ser variável, a depender exclusivamente do tamanho do ato normativo que ele comporta. Além disso, misturamos busca semântica com busca lexical, em caso de busca exata por números de processo e identificadores pessoais.
