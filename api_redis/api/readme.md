# Quiz API

Este projeto implementa uma API de quizzes usando FastAPI e Redis para armazenar e gerenciar quizzes, perguntas, alternativas de respostas e resultados em tempo real. Ele permite a criação, votação, consulta de resultados e rankings de quizzes, além de controlar o tempo de resposta dos usuários.

## Pré-requisitos

Antes de rodar o projeto, você precisará de:

- Python 3.7+
- Redis: um servidor Redis ativo para armazenar os dados (Você pode usar o Redis em nuvem ou localmente).
- Instale as dependências do projeto:

```bash
pip install fastapi redis uvicorn
````

## Como Rodar

Para rodar o servidor FastAPI, execute:

```bash
uvicorn main:app --reload
```

Isso iniciará a API no endereço <http://127.0.0.1:8000>.

# Endpoints

1. Criar Quiz
`POST /quizzes/`

Cria um ou mais quizzes, cada um com suas respectivas perguntas e alternativas.

Body (JSON):

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

Resposta (JSON):

```json
{
  "message": "Quizzes criados com sucesso!",
  "quiz_ids": ["quiz:quiz_de_exemplos"]
}
```

2. Obter Todos os Quizzes
`GET /quizzes/`

Obtém todos os quizzes armazenados.

Resposta (JSON):

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

Obtém um quiz específico baseado no quiz_id.

Resposta (JSON):

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

Registra o voto de um usuário para uma pergunta específica.

Parâmetros:

quiz_id: ID do quiz
question_index: Índice da pergunta no quiz
alternative: Alternativa selecionada
user_id: ID do usuário

Body (JSON):

```json
{
  "question_index": 0,
  "alternative": "A",
  "user_id": "user_1"
}
```

Resposta (JSON):

```json
{
  "message": "Voto registrado com sucesso!"
}
```

5. Visualizar Resultados
`GET /quizzes/{quiz_id}/resultados/`

Obtém os resultados (votos) de todas as perguntas de um quiz.

Resposta (JSON):

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

Obtém o ranking de alternativas mais votadas para cada pergunta de um quiz.

Resposta (JSON):

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

Obtém o ranking de questões mais acertadas por todos os usuários.

Resposta (JSON):

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

Obtém o ranking de questões com mais abstenções de votos.

Resposta (JSON):

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

Obtém o ranking de tempo médio de resposta por questão.

Resposta (JSON):

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

Exclui todos os quizzes armazenados no Redis.

Resposta (JSON):

```json
{
  "message": "Todos os quizzes foram apagados."
}
```

11. Excluir Todos os Votos e Respostas de Usuários
`DELETE /quizzes/votos-e-respostas/`

Exclui todos os votos e respostas de usuários armazenadas no Redis.

Resposta (JSON):

```json
{
  "message": "Todos os votos e respostas de usuários foram apagados."
}
```

# Como Funciona?

O projeto utiliza o Redis para armazenar e gerenciar os dados dos quizzes, como:

- Quizzes e suas perguntas
- Alternativas e seus votos
- Tempo de resposta dos usuários
- Rankings de questões e alternativas

# Tecnologias Utilizadas

- FastAPI: Framework para construir a API REST.
- Redis: Banco de dados em memória para armazenar os dados de quizzes, votos e rankings.
- Uvicorn: Servidor ASGI para rodar o FastAPI.

---

# Próximos Passos

- Testar:
  - Para cada pergunta, será mantido um contador para cada alternativa.

- Adicionar:
  - Uma vez o voto realizado, ele não poderá ser alterado;
  - Alunos com maior acerto e mais rápidos: rank final dos alunos;
  - Alunos com maior acerto: Independente do tempo que levaram para responder cada pergunta;
  - Alunos mais rápidos: Independente do número de acertos;

- Verificar erro 500
  - <http://127.0.0.1:8000/quizzes/quiz_de_geografia/resultados/>
  - <http://127.0.0.1:8000/quizzes/quiz_de_geografia/ranking/alternativas/>

- Verificar tempo medio
  - <http://127.0.0.1:8000/quizzes/quiz_de_geografia/ranking/tempo_medio/>
