# Quiz API com FastAPI e Redis

Este projeto implementa uma API para quizzes utilizando **FastAPI** e **Redis** para armazenar e gerenciar quizzes, perguntas, alternativas de respostas e resultados em tempo real. Ele permite criar quizzes, registrar votos, consultar resultados e rankings, além de controlar o tempo de resposta dos usuários.

---

## Pré-requisitos

Antes de rodar o projeto, você precisará de:

- **Python 3.7+**
- **Redis**: Um servidor Redis ativo para armazenar os dados (você pode usar Redis na nuvem ou localmente).

Instale as dependências necessárias com o seguinte comando:

- `pip install fastapi redis uvicorn`
- `pip install python-dotenv`

Para iniciar o servidor FastAPI, execute o comando:

- `uvicorn main:app --reload`

Caso você tiver problemas com o dotenv não estar funcionando com o modulo do uvicorn, tente utilizar o seguinte comando:

- `python3 -m uvicorn main:app --reload`

A aplicação estará disponível no endereço: <http://127.0.0.1:8000>.

# Endpoints

1. Criar Quiz
`POST /quizzes/`

Cria um ou mais quizzes, cada um com suas respectivas perguntas e alternativas.

Exemplo de Body (JSON):

```json
{
  "quizzes": [
    {
      "title": "Quiz de Exemplos",
      "questions": [
        {
          "question": "Qual é a cor do céu?",
          "alternatives": [
            ["A", "Azul"],
            ["B", "Verde"],
            ["C", "Vermelho"],
            ["D", "Amarelo"]
          ],
          "correct_answer": "A"
        }
      ]
    }
  ]
}
```

Exemplo de Resposta (JSON):

```json
{
  "message": "Quizzes criados com sucesso!",
  "quiz_ids": ["quiz:quiz_de_exemplos"]
}
````

2. Obter Todos os Quizzes
`GET /quizzes/`

Retorna todos os quizzes armazenados.

Exemplo de Resposta (JSON):

```json
{
  "quizzes": [
    {
      "quiz_id": "quiz:quiz_de_exemplos",
      "title": "Quiz de Exemplos",
      "questions": [...]
    }
  ]
}
```

3. Obter Quiz Específico
`GET /quizzes/{quiz_id}`

Obtém os detalhes de um quiz específico pelo ID.

Exemplo de Resposta (JSON):

```json
{
  "quiz": {
    "quiz_id": "quiz:quiz_de_exemplos",
    "title": "Quiz de Exemplos",
    "questions": [...]
  }
}
```

4. Votar em uma Alternativa
`POST /quizzes/{quiz_id}/votar/`

Registra o voto de um usuário em uma pergunta específica de um quiz.

Parâmetros:

- quiz_id: ID do quiz.
- question_index: Índice da pergunta no quiz.
- alternative: Alternativa selecionada.
- user_id: ID do usuário.

Exemplo de Body (JSON):

```json

{
  "question_index": 0,
  "alternative": "A",
  "user_id": "user_1"
}
```

Exemplo de Resposta (JSON):

```json
{
  "message": "Voto registrado com sucesso!"
}
```

5. Visualizar Resultados
`GET /quizzes/{quiz_id}/resultados/`

Retorna os resultados (votos) de todas as perguntas de um quiz.

Exemplo de Resposta (JSON):

```json
{
  "resultados": [
    {
      "pergunta": "Qual é a cor do céu?",
      "votos": {
        "A": 10,
        "B": 2,
        "C": 0,
        "D": 0
      }
    }
  ]
}
```

6. Ranking de Alternativas Mais Votadas
`GET /quizzes/{quiz_id}/ranking/alternativas/`

Retorna o ranking de alternativas mais votadas para cada pergunta de um quiz.

Exemplo de Resposta (JSON):

```json
{
  "ranking": [
    {
      "question": "Qual é a cor do céu?",
      "alternative": "A",
      "votes": 10
    }
  ]
}
```

7. Ranking de Questões Mais Acertadas
`GET /quizzes/{quiz_id}/ranking/questoes/`

Retorna o ranking de questões mais acertadas pelos usuários.

Exemplo de Resposta (JSON):

```json
{
  "question_ranking": [
    {
      "question": "Qual é a cor do céu?",
      "correct_answers": 12
    }
  ]
}
```

8. Ranking de Abstenções
`GET /quizzes/{quiz_id}/ranking/abstencao/`

Retorna o ranking de questões com mais abstenções.

Exemplo de Resposta (JSON):

```json
{
  "abstencao_ranking": [
    {
      "question": "Qual é a cor do céu?",
      "abstencao": 5
    }
  ]
}
```

9. Ranking de Tempo Médio de Resposta
`GET /quizzes/{quiz_id}/ranking/tempo_medio/`

Retorna o tempo médio de resposta por questão.

Exemplo de Resposta (JSON):

```json
{
  "tempo_medio_ranking": [
    {
      "question": "Qual é a cor do céu?",
      "avg_time": 12.5
    }
  ]
}
```

10. Excluir Todos os Quizzes
`DELETE /quizzes/`

Remove todos os quizzes armazenados no Redis.

Exemplo de Resposta (JSON):

```json
{
  "message": "Todos os quizzes foram apagados."
}
```

11. Excluir Todos os Votos e Respostas de Usuários
`DELETE /quizzes/votos-e-respostas/`

Remove todos os votos e respostas de usuários.

Exemplo de Resposta (JSON):

```json
{
  "message": "Todos os votos e respostas de usuários foram apagados."
}
```

# Tecnologias Utilizadas

- FastAPI: Framework para construção da API.
- Redis: Banco de dados em memória para armazenamento de quizzes, votos e rankings.
- Uvicorn: Servidor ASGI para executar a aplicação FastAPI.
