# Projeto: Gerenciador de Quizzes com FastAPI

Este projeto é uma API para criação, gestão e análise de quizzes. Ele foi desenvolvido usando FastAPI e integra o uso do Redis para armazenamento e recuperação de dados.

## Estrutura do Projeto

A estrutura de pastas está organizada da seguinte forma:

```
api_redis/
│
├── api/
│   ├── __init__.py            # Inicialização do módulo API
│   ├── export_files.py        # Exportação e importação de arquivos JSON
│   └── main.py                # Arquivo principal com todos os endpoints
│
├── database/
│   ├── redis_export.json      # Backup de dados exportados do Redis
│   └── redis.json             # Arquivo de configuração ou importação
│
├── tests/
│   ├── test_unitarios_main.py # Testes unitários para os endpoints
│── |__init__.py            # Inicialização do módulo de testes
|
│── __init__.py
│── api_redis.postman_collection.json  # Coleção para Postman
│
└── readme.md                  # Documentação principal do projeto
```

## Como Instalar e Executar o Projeto

### Pré-requisitos

- Python 3.8 ou superior.
- Redis configurado e rodando na máquina.

### Passos para Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/annamatias/dataengineer.git
   cd dataengineer

2. Crie um ambiente virtual e ative-o:

```
python -m venv venv
source venv/bin/activate  # Para sistemas Unix
venv\Scripts\activate     # Para Windows
```

3. Instale as dependências:

`pip install -r requirements.txt`

Configure o Redis: Certifique-se de que o Redis está em execução e configure as variáveis de ambiente no arquivo .env:

```
REDIS_HOST=<seu-host-redis>
REDIS_PORT=<sua-porta-redis>
REDIS_PASSWORD=<sua-senha-redis>
```

4. Inicie o servidor FastAPI:

`uvicorn app.main:app --reload`

Acesse a documentação interativa em <http://127.0.0.1:8000/docs>.

# Endpoints da API

1. Criar um novo quiz

POST `/quizzes/`

Request Body:

```
{
  "title": "Quiz de Exemplo",
  "questions": [
    {
      "question": "Qual a capital do Brasil?",
      "alternatives": [["Brasília", true], ["Rio de Janeiro", false]],
      "correct_answer": "Brasília"
    }
  ]
}
```

Response:

```
{
  "message": "Quiz criado com sucesso!",
  "quiz_id": "abc123"
}
```

2. Listar todos os quizzes

GET `/quizzes/`

Response:

```
[
  {
    "quiz_id": "abc123",
    "title": "Quiz de Exemplo"
  }
]
```

3. Buscar um quiz pelo ID

GET `/quizzes/{quiz_id}`

Response:

```
{
  "quiz_id": "abc123",
  "title": "Quiz de Exemplo",
  "questions": [...]
}
```

4. Votar em uma pergunta de um quiz

POST `/quizzes/{quiz_id}/votar/`

Query Params:

```
question_index: Índice da pergunta.
alternative: Alternativa escolhida.
user_id: Identificação do usuário.
```

Response:

```
{
  "message": "Voto registrado com sucesso!"
}
```

5. Visualizar resultados de um quiz

GET `/quizzes/{quiz_id}/resultados/`

Response:

```
{
  "resultados": {
    "question_1": {
      "alternatives": {
        "Brasília": 10,
        "Rio de Janeiro": 2
      }
    }
  }
}
```

6. Ranking de alternativas

GET `/quizzes/{quiz_id}/ranking/alternativas/`

Response:

```
{
  "ranking": [
    {"alternative": "Brasília", "votes": 10},
    {"alternative": "Rio de Janeiro", "votes": 2}
  ]
}
```

7. Ranking por questão

GET `/quizzes/{quiz_id}/ranking/questoes/`

Response:

```
{
  "question_ranking": [
    {"question": "Qual a capital do Brasil?", "votes": 12}
  ]
}
```

8. Ranking de abstenção

GET `/quizzes/{quiz_id}/ranking/abstencao/`

Response:

```
{
  "abstencao_ranking": [
    {"question": "Qual a capital do Brasil?", "abstencoes": 5}
  ]
}
```

9. Ranking de tempo médio de resposta

GET `/quizzes/{quiz_id}/ranking/tempo_medio/`

Response:

```
{
  "tempo_medio_ranking": [
    {"question": "Qual a capital do Brasil?", "tempo_medio": 2.5}
  ]
}
```

10. Ranking de rapidez

GET `/quizzes/{quiz_id}/ranking/rapidez/`

Response:

```
{
  "rapidez_ranking": [
    {"user_id": "user1", "response_time": 1.2}
  ]
}
```

11. Ranking de acertos

GET `/quizzes/{quiz_id}/ranking/acerto/`

Response:

```
{
  "ranking_acerto": [
    {"user_id": "user1", "acertos": 5}
  ]
}
```

12. Ranking geral

GET `/quizzes/{quiz_id}/ranking/geral/`

Response:

```
{
  "ranking_geral": [
    {"user_id": "user1", "pontos": 50}
  ]
}
```

13. Deletar todos os votos e respostas de usuários

DELETE `/quizzes/votos-e-respostas/`

Response:

```
{
  "message": "Todos os votos e respostas foram excluídos."
}
```

14. Deletar respostas e tempos de resposta

DELETE `/quizzes/responses-time-and-aswers/`

Response:

```
{
  "message": "Respostas e tempos de resposta excluídos."
}
```

15. Deletar todos os quizzes

DELETE `/quizzes/`

Response:

```
{
  "message": "Todos os quizzes foram excluídos."
}
```

16. Deletar um quiz específico

DELETE `/quizzes/{quiz_id}`

Response:

```
{
  "message": "Quiz excluído com sucesso."
}
```
