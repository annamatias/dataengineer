from fastapi import FastAPI, HTTPException
import redis
import json
import time
from datetime import timedelta

# Configuração do cliente Redis
redis_client = redis.Redis(
    host='redis-17224.c93.us-east-1-3.ec2.redns.redis-cloud.com',
    port=17224,
    password='UtRsPtFRSlKJWTCc21uWvkiO4jyGgfA3')

# Inicializa o FastAPI
app = FastAPI()

# Função para gerenciar o tempo de votação e garantir que a votação seja feita dentro de 20 segundos


def get_vote_time(quiz_id: str, question_index: int, user_id: str):
    start_time = time.time()
    redis_client.setex(f"vote_time:{quiz_id}:{question_index}:{user_id}", timedelta(
        seconds=20), start_time)
    return start_time

# Função para calcular o tempo médio de resposta por questão


def calculate_avg_response_time(quiz_id: str, question_index: int):
    response_times = redis_client.keys(
        f"vote_time:{quiz_id}:{question_index}:*")
    if response_times:
        total_time = sum([time.time() - float(redis_client.get(key))
                         for key in response_times])
        return total_time / len(response_times)
    return 0

# Função para atualizar os rankings


def update_rankings(quiz_id: str, user_id: str, question_index: int, alternative: str, correct_answer: str, start_time: float):
    end_time = time.time()
    response_time = end_time - start_time

    # Armazena a resposta e o tempo de resposta
    redis_client.hset(
        f"user_responses:{quiz_id}:{user_id}", question_index, alternative)
    redis_client.hset(
        f"response_time:{quiz_id}:{user_id}", question_index, response_time)

    # Atualiza os rankings de acertos e tempos
    if alternative == correct_answer:
        redis_client.hincrby(f"correct_answers:{quiz_id}", user_id, 1)
    redis_client.zadd(f"response_time_rank:{quiz_id}", {
                      user_id: response_time})

    # Atualiza os contadores de votos da alternativa
    redis_client.hincrby(f"vote:{quiz_id}:{question_index}", alternative, 1)


# Rota para criar os quizzes
@app.post("/quizzes/")
async def create_quiz(quiz_request: dict):
    quiz_ids = []  # Lista para armazenar os quiz_ids gerados
    for quiz in quiz_request['quizzes']:
        quiz_id = f"quiz:{quiz['title'].replace(' ', '_').lower()}"

        # Verifica se o quiz já existe no Redis
        if redis_client.exists(quiz_id):
            raise HTTPException(
                status_code=400, detail=f"Quiz '{quiz['title']}' já existe.")

        # Armazenar o quiz em formato JSON no Redis
        redis_client.set(quiz_id, json.dumps(
            quiz), ex=timedelta(days=30))  # Expira em 30 dias

        # Inicializa os contadores de votos para cada pergunta e alternativa
        for i, question in enumerate(quiz['questions']):
            # Verifica se há exatamente 4 alternativas
            if len(question['alternatives']) != 4:
                raise HTTPException(
                    status_code=400, detail="Cada pergunta deve ter exatamente 4 alternativas.")

            # Verifica se a resposta correta está entre as alternativas
            if question['correct_answer'] not in [alt[0] for alt in question['alternatives']]:
                raise HTTPException(
                    status_code=400, detail="A resposta correta deve ser uma das alternativas.")

            # Inicializa os contadores de votos para as alternativas
            for alternative in question['alternatives']:
                alt, _ = alternative  # Obtém a chave e o valor da alternativa
                # Inicializa o contador de votos para cada alternativa
                redis_client.hset(f"vote:{quiz_id}:{i}", alt, 0)

        quiz_ids.append(quiz_id)

    return {"message": "Quizzes criados com sucesso!", "quiz_ids": quiz_ids}


# Rota para obter todos os quizzes
@app.get("/quizzes/")
async def get_quizzes():
    quiz_keys = redis_client.keys("quiz:*")  # Chaves que começam com "quiz:"

    quizzes = []
    for key in quiz_keys:
        quiz_data = redis_client.get(key)
        quiz = json.loads(quiz_data)
        quiz["quiz_id"] = key
        quizzes.append(quiz)

    return {"quizzes": quizzes}

# Rota para obter um quiz específico


@app.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str):
    quiz_data = redis_client.get(quiz_id)
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz = json.loads(quiz_data)
    return {"quiz": quiz}


# Rota para votar em uma alternativa de um quiz
@app.post("/quizzes/{quiz_id}/votar/")
async def votar(quiz_id: str, question_index: int, alternative: str, user_id: str):
    if not redis_client.exists(quiz_id):
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz_data = json.loads(redis_client.get(quiz_id))
    if question_index < 0 or question_index >= len(quiz_data['questions']):
        raise HTTPException(status_code=400, detail="Pergunta inválida.")

    question = quiz_data['questions'][question_index]
    if alternative not in [alt[0] for alt in question['alternatives']]:
        raise HTTPException(status_code=400, detail="Alternativa inválida.")

    correct_answer = question['correct_answer']

    # Controla o tempo de resposta
    start_time = get_vote_time(quiz_id, question_index, user_id)

    # Atualiza o ranking e o contador de votos
    update_rankings(quiz_id, user_id, question_index,
                    alternative, correct_answer, start_time)

    return {"message": "Voto registrado com sucesso!"}

# Rota para visualizar os contadores de votos em tempo real


@app.get("/quizzes/{quiz_id}/resultados/")
async def visualizar_resultados(quiz_id: str):
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz = json.loads(quiz_data)

    resultados = []
    for i, pergunta in enumerate(quiz['questions']):
        alternativas = pergunta['alternatives']
        votos = {}

        for alternativa in alternativas:
            votos[alternativa] = int(redis_client.hget(
                f"vote:{quiz_id}:{i}", alternativa) or 0)

        resultados.append({"pergunta": pergunta['question'], "votos": votos})

    return {"resultados": resultados}

# Rota para ranking de alternativas mais votadas


@app.get("/quizzes/{quiz_id}/ranking/alternativas/")
async def ranking_alternativas(quiz_id: str):
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz = json.loads(quiz_data)

    rankings = []
    for i, pergunta in enumerate(quiz['questions']):
        alternativas = pergunta['alternatives']
        votos = {}
        for alternativa in alternativas:
            votos[alternativa] = int(redis_client.hget(
                f"vote:{quiz_id}:{i}", alternativa) or 0)

        max_votes = max(votos.values())
        for alternativa, count in votos.items():
            if count == max_votes:
                rankings.append(
                    {"question": pergunta['question'], "alternative": alternativa, "votes": count})

    return {"ranking": rankings}

# Rota para ranking de questões mais acertadas


@app.get("/quizzes/{quiz_id}/ranking/questoes/")
async def ranking_questoes(quiz_id: str):
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz = json.loads(quiz_data)

    question_ranking = []
    for i, pergunta in enumerate(quiz['questions']):
        correct_count = redis_client.hgetall(f"user_responses:{quiz_id}:*:{i}")
        question_ranking.append(
            {"question": pergunta['question'], "correct_answers": len(correct_count)})

    return {"question_ranking": question_ranking}

# Rota para ranking de questões com mais abstenções


@app.get("/quizzes/{quiz_id}/ranking/abstencao/")
async def ranking_abstencao(quiz_id: str):
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz = json.loads(quiz_data)

    abstencao_ranking = []
    for i, pergunta in enumerate(quiz['questions']):
        abstencao_count = len(redis_client.keys(
            f"vote_time:{quiz_id}:{i}:*")) - redis_client.hlen(f"vote:{quiz_id}:{i}")
        abstencao_ranking.append(
            {"question": pergunta['question'], "abstencao": abstencao_count})

    return {"abstencao_ranking": abstencao_ranking}

# Rota para ranking de tempo médio de resposta por questão


@app.get("/quizzes/{quiz_id}/ranking/tempo_medio/")
async def ranking_tempo_medio(quiz_id: str):
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz = json.loads(quiz_data)

    tempo_medio_ranking = []
    for i, pergunta in enumerate(quiz['questions']):
        avg_time = calculate_avg_response_time(quiz_id, i)
        tempo_medio_ranking.append(
            {"question": pergunta['question'], "avg_time": avg_time})

    return {"tempo_medio_ranking": tempo_medio_ranking}

# Rota para excluir todos os quizzes


@app.delete("/quizzes/")
async def delete_all_quizzes():
    # Recupera todas as chaves de quizzes armazenados no Redis
    quiz_keys = redis_client.keys("quiz:*")

    for key in quiz_keys:
        redis_client.delete(key)  # Apaga o quiz

    return {"message": "Todos os quizzes foram apagados."}

# Rota para excluir todos os votos e respostas de usuários


@app.delete("/quizzes/votos-e-respostas/")
async def delete_all_votes_and_user_responses():
    # Recupera todas as chaves de votos e respostas armazenadas no Redis
    vote_keys = redis_client.keys("vote:*")
    user_response_keys = redis_client.keys("user_responses:*")

    for key in vote_keys:
        redis_client.delete(key)  # Apaga o voto

    for key in user_response_keys:
        redis_client.delete(key)  # Apaga a resposta do usuário

    return {"message": "Todos os votos e respostas de usuários foram apagados."}
