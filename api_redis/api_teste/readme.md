# README - API de Quizzes com FastAPI e Redis

Esta API permite criar quizzes, votar em alternativas de um quiz, visualizar os resultados em tempo real e excluir quizzes. Os dados dos quizzes e os votos são armazenados no Redis.

## Tecnologias Utilizadas

- **FastAPI**: Framework moderno para construir APIs rápidas e com validação automática.
- **Redis**: Banco de dados em memória utilizado para armazenar os dados dos quizzes e os votos.
- **Python**: Linguagem de programação utilizada para construir a aplicação.

## Endpoints da API

### 1. **Criar Quiz**

- **Método**: `POST`
- **URL**: `/quizzes/`
- **Descrição**: Cria um ou mais quizzes.
- **Body (JSON)**:

  ```json
  {
    "quizzes": [
      {
        "title": "Geografia do Mundo",
        "questions": [
          {
            "question": "Qual é a capital da França?",
            "alternatives": ["A. Paris", "B. Londres", "C. Roma"]
          },
          {
            "question": "Qual é o maior país do mundo?",
            "alternatives": ["A. Rússia", "B. Canadá", "C. China"]
          }
        ]
      }
    ]
  }
  ```

- **Resposta (JSON)**:

  ```json
  {
    "message": "Quizzes criados com sucesso!",
    "quiz_ids": ["quiz:geografia_do_mundo"]
  }
  ```

### 2. **Obter Todos os Quizzes**

- **Método**: `GET`
- **URL**: `/quizzes/`
- **Descrição**: Obtém todos os quizzes criados.
- **Resposta (JSON)**:

  ```json
  {
    "quizzes": [
      {
        "quiz_id": "quiz:geografia_do_mundo",
        "title": "Geografia do Mundo",
        "questions": [
          {
            "question": "Qual é a capital da França?",
            "alternatives": ["A. Paris", "B. Londres", "C. Roma"]
          }
        ]
      }
    ]
  }
  ```

### 3. **Votar em uma Alternativa**

- **Método**: `POST`
- **URL**: `/quizzes/{quiz_id}/votar/`
- **Parâmetros**:
  - `quiz_id`: ID do quiz.
  - `question_index`: Índice da pergunta.
  - `alternative`: Alternativa escolhida (por exemplo, "A. Paris").
- **Descrição**: Registra um voto para uma alternativa em uma pergunta de um quiz.
- **Resposta (JSON)**:

  ```json
  {
    "message": "Voto registrado com sucesso!"
  }
  ```

### 4. **Obter um Quiz Específico**

- **Método**: `GET`
- **URL**: `/quizzes/{quiz_id}`
- **Parâmetros**:
  - `quiz_id`: ID do quiz.
- **Descrição**: Obtém os detalhes de um quiz específico.
- **Resposta (JSON)**:

  ```json
  {
    "quiz_id": "quiz:geografia_do_mundo",
    "title": "Geografia do Mundo",
    "questions": [
      {
        "question": "Qual é a capital da França?",
        "alternatives": ["A. Paris", "B. Londres", "C. Roma"]
      }
    ]
  }
  ```

### 5. **Visualizar Resultados em Tempo Real**

- **Método**: `GET`
- **URL**: `/quizzes/{quiz_id}/resultados/`
- **Parâmetros**:
  - `quiz_id`: ID do quiz.
- **Descrição**: Exibe os resultados de todos os votos registrados para cada alternativa.
- **Resposta (JSON)**:

  ```json
  {
    "resultados": [
      {
        "pergunta": "Qual é a capital da França?",
        "votos": {
          "A. Paris": 10,
          "B. Londres": 5,
          "C. Roma": 2
        }
      }
    ]
  }
  ```

### 6. **Excluir Todos os Quizzes**

- **Método**: `DELETE`
- **URL**: `/quizzes/`
- **Descrição**: Exclui todos os quizzes armazenados no Redis.
- **Resposta (JSON)**:

  ```json
  {
    "message": "Todos os quizzes foram apagados."
  }
  ```

## Como Rodar a Aplicação

### Pré-requisitos

- Python 3.7 ou superior.
- Redis em execução (local ou remoto).
- Instalar as dependências com o comando:

  ```bash
  pip install fastapi redis uvicorn
  ```

### Executando a API

Execute o servidor utilizando o Uvicorn:

```bash
uvicorn main:app --reload
```

Isso iniciará a API localmente na URL `http://127.0.0.1:8000`.

## Testando a API com o Postman

### 1. **Criar Quiz**

- **Método**: POST
- **URL**: `http://127.0.0.1:8000/quizzes/`
- **Body**: Insira o JSON de criação de quizzes.

### 2. **Obter Todos os Quizzes**

- **Método**: GET
- **URL**: `http://127.0.0.1:8000/quizzes/`

### 3. **Votar em Alternativa**

- **Método**: POST
- **URL**: `http://127.0.0.1:8000/quizzes/quiz:geografia_do_mundo/votar/?question_index=0&alternative=A`

### 4. **Obter Quiz Específico**

- **Método**: GET
- **URL**: `http://127.0.0.1:8000/quizzes/{quiz_id}`

### 5. **Visualizar Resultados**

- **Método**: GET
- **URL**: `http://127.0.0.1:8000/quizzes/{quiz_id}/resultados/`

### 6. **Excluir Todos os Quizzes**

- **Método**: DELETE
- **URL**: `http://127.0.0.1:8000/quizzes/`

---

# Próximos Passos

- Adicionar/verificar o tempo de resposta para cada pergunta e parar a requisição
  - Tem que ter até 20 segundos para responder cada pergunta

- Verificar o motivo de não estar registrando quando enviamos uma resposta errada
  - `POST http://127.0.0.1:8000/quizzes/quiz:geografia_do_mundo/votar/?question_index=0&alternative=A`

- Verificar o motivo de não estar registrando em tempo real as respostas e realizar a contagem
  - Pode ser algum problema na hora de armazenar os dados no Redis
  - `GET http://127.0.0.1:8000/quizzes/geografia_do_mundo/resultados/`

- Verificar novamente o armazenamento no Redis:
  - Os dados dos quizzes (perguntas, alternativas e votos) serão armazenados no Redis.
  - Utilize estruturas de dados do Redis, como hashes ou sets, para representar as informações relevantes.
  - IMPORTANTE: utilize a estrutura mais adequada para cada entidade.

- Criar um Ranking
  - O sistema exibirá os seguintes rankings:
    - Alternativas Mais Votadas: Alternativas que receberam mais votos por questão
    - Questões mais acertadas: Questões com maior índice de acerto
    - Questões com mais abstenções: Ou seja, que tiveram menos votos válidos
    - Tempo médio de resposta por questão: Tempo médio que os alunos responderam cada questão
    - Alunos com maior acerto e mais rápidos: rank final dos alunos
    - Alunos com maior acerto: Independente do tempo que levaram para responder cada pergunta
    - Alunos mais rápidos: Independente do número de acertos
