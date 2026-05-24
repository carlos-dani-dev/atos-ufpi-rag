# RAG para atos normativos da UFPI


<p>Atos normativos são documentos que regulamentam, instruem e padronizam o funcionamento das atividades da Universidade Federal.<br>
Eles são publicados ao decorrer do tempo e podem tratar dos mais variados assuntos. O RAG desenvolvido neste repositório utiliza os modelos de IA generativa mais famosos para responder à perguntas sob contexto.</p>
<p>Veja um exemplo de ato normativo abaixo:</p>

| Nº | Data | Envolvido | Descrição |
| :--- | :--- | :--- | :--- |
| 663 | 5/4/2026 | PAD | **Processo nº 23111.004938/2024-03**<br><br>1. Reconduzir a Comissão de Processo Administrativo Disciplinar de Rito Ordinário, constituída pelo Ato da Reitoria n.º 2400/25, de 29/12/2025, publicado no Boletim de Serviço Especial em 05/01/2026, para, no prazo de 60 (sessenta) dias, continuar a apuração de possíveis irregularidades sobre as quais versam os autos do Processo n.º 23111. 23111.004938/2024-03;<br><br>2. Os servidores designados ficam dispensados de suas atividades funcionais nos horários em que se dedicarão à realização dos trabalhos da Comissão, nos termos do § 1° do artigo 152 da Lei 8.112/90. |

### Tecnologias Utilizadas

<table>
    <tr>
        <td>
            <strong>Ferramenta</strong>
        </td>
        <td>
            <strong>Descrição do uso</strong>
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://www.python.org/" target="_blank">Python</a>
        </td>
        <td>
            A linguagem base de todo o projeto.
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://streamlit.io/" target="_blank">Streamlit</a>
        </td>
        <td>
            Framework Python para criação da interface gráfica.
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://openrouter.ai/" target="_blank">OpenRouter</a>
        </td>
        <td>
            Plataforma usada para centralização do acesso às IAs generativas.
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://www.langchain.com/" target="_blank">Langchain</a>
        </td>
        <td>
            Framework Python que sistematiza tanto a produção dos prompts, como a separação do texto base em markdown para posterior vetorização.
        </td>
    </tr>
    <tr>
        <td>
            <a href="https://sbert.net/" target="_blank">SentenceTransformers</a>
        </td>
        <td>
            Framework Python utilizado para o chamamento do modelo que realiza a vetorização do texto base separado.
        </td>
    </tr>
</table>

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
<p>1) A primeira etapa é a preparação dos dados, que envolve o webscrapping dos atos normativos via script python e salvamento em arquivo csv intermediário. Este arquivo
intermediário é lido e transformado em um arquivo de texto base .txt em formato markdown.</p>
<p>2) Após isso, o laboratório colab invoca o SentenceTransformer e vetoriza o arquivo .txt em formato markdown, ato por ato. O resultado desse processo é uma pasta zipada
com o Faiss Index (dataset vetorizado nativo da Meta, otimizado para buscas por proximidade).</p>
<p>3) A etapa final é a busca por semelhança da pergunta vetorizada dentro do dataset vetorizado resultante da etapa anterior. Os atos normativos mais semelhantes compõem
o system prompt que será enviado às IA's generativas por meio da API do OpenRouter. A resposta é exibida ao usuário.</p>

<p align="center"><img width="5901" height="2157" alt="image" src="https://github.com/user-attachments/assets/feea077f-f79c-4f70-a21c-79858ddb49ac" /></p>

### Problemas enfrentados

<table>
  <tr>
    <td>
      <strong>Principal problema da aplicação:</strong>
    </td>
    <td>
      Qual o ponto ótimo de separação do texto base?
Inicialmente vetorizamos batches de tamanho fixo, o que prejudicava o processo de recuperação dos batches por semelhança e retornava um contexto inútil para a IA generativa explorar.
    </td>
  </tr>
  <tr>
    <td>
      <strong>Como solucionamos:</strong>
    </td>
    <td>O tamanho de cada batch passou a ser variável, a depender exclusivamente do tamanho do ato normativo que ele comporta. Além disso, misturamos busca semântica com busca lexical, em caso de busca exata por números de processo e identificadores pessoais.
    </td>
  </tr>
</table>
