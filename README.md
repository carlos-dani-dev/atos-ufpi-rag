# RAG de atos normativos da UFPI

<p>Atos normativos são documentos que regulamentam, instruem e padronizam o funcionamento das atividades da Universidade Federal. Eles são publicados ao decorrer do tempo e podem
tratar os mais variados assuntos. O RAG desenvolvido neste repositório utiliza os modelos de IA generativa mais famosos para responder à perguntas sob contexto.
Veja um exemplo de ato normativo abaixo:</p>
<p align="center"><img width="756" height="234" alt="image" src="https://github.com/user-attachments/assets/270a663e-80ff-4f4b-8e3c-f92e1b37fad9" /></p>

[![](https://mermaid.ink/img/pako:eNpVkE1uwjAQha9izapIZFGWWVSCBFZUVCq7mMXInjSW_Fdji6Ikp2HRg3CxmmRDZzV633uj0etBOElQQqvdRXQYIjvW3LI862bttRJ4_73fHHs9saJ4GwJ9JzrHgW1enulqMWc2DxOr-u0PGa_dOKvVFD1YGljd7NFH50_P5HhxA9s26qNzlv6TLlBO7ZoWyxYLgYFVGCYLLMFQMKhk_r5_KBxiR4Y4lHmV1GLSkQO3Y7Ziiu7zagWUMSRaQvISI9UKvwIayLf1OaskVXThfW5kKmb8AyAeX3o?type=png)](https://mermaid.live/edit#pako:eNpVkE1uwjAQha9izapIZFGWWVSCBFZUVCq7mMXInjSW_Fdji6Ikp2HRg3CxmmRDZzV633uj0etBOElQQqvdRXQYIjvW3LI862bttRJ4_73fHHs9saJ4GwJ9JzrHgW1enulqMWc2DxOr-u0PGa_dOKvVFD1YGljd7NFH50_P5HhxA9s26qNzlv6TLlBO7ZoWyxYLgYFVGCYLLMFQMKhk_r5_KBxiR4Y4lHmV1GLSkQO3Y7Ziiu7zagWUMSRaQvISI9UKvwIayLf1OaskVXThfW5kKmb8AyAeX3o)

### Tecnologias Utilizadas

* [Python](https://www.python.org/) - A linguagem base de todo o projeto.
* [Streamlit](https://streamlit.io/) - Framework python para crianção da interface gráfica.
* [OpenRouter](https://openrouter.ai/) - Plataforma usada para centralização do acesso às IA's generativas.
* [Langchain](https://www.langchain.com/) - Framework python que sistematiza tanto a produção dos prompts, como a separação do texto base em markdown para posterior vetorização
* [SenteceTransformers](https://sbert.net/) - Framework python utilizado para o chamamento do modelo que realiza a vetorização do texto base separado


## Dependências e Versões Necessárias

Liste as dependências necessárias para rodar o projeto e as versões que você utilizou.

* Docker - Versão: X.X

## Como rodar o projeto ✅

Descreva o passo a passo necessário para rodar sua aplicação. Lembre-se: a pessoa nunca rodou seu projeto. Não tenha medo de detalhar o máximo possível. Isso é necessário!

Uma boa forma de descrever o passo a passo é:

```
Comando 1
```

Depois, rode o seguinte comando:

```
Comando 2
```

Deixe claro como a pessoa pode confirmar que a aplicação está rodando da forma correta. Pode ser com prints ou a mensagem que ela deve esperar.

## Como rodar os testes

Explique como rodar os testes da aplicação. Exemplo de um comando usando Makefile para rodar os testes:

```
make test
```

## 📌 (Título) - Informações importantes sobre a aplicação (exemplo) 📌

Esse é o local para você preencher com outras informações que possam ser importantes para a aplicação. Coloquei um exemplo de título, mas você deve preencher de acordo com a necessidade do projeto. Pode ser que não seja necessário.

Um bom exemplo: se você estiver construindo uma API, liste as rotas da aplicação e quais serão os seus retornos. Isso facilita para quem vai consumir a API.


## ⚠️ Problemas enfrentados

Liste os problemas que você enfrentou construindo a aplicação e como você resolveu cada um deles. Você que desenvolveu o projeto é a pessoa que mais conhece/entende os possíveis problemas que uma pessoa pode enfrentar rodando a aplicação. Compartilhe esse conhecimento e facilite a vida da pessoa descrevendo-os.

Exemplo:

### Problema 1:
Descrição do problema
* Como solucionar: explicar a solução.

### Problema 2:
Descrição do problema
* Como solucionar: explicar a solução.

## ⏭️ Próximos passos

Descreva se você pretende, pensou ou gostaria de elaborar uma nova feature para o seu projeto definindo os próximos passos.
