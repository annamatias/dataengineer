import time
import json
import redis
from fastapi import FastAPI, HTTPException
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

# Função auxiliar para calcular o tempo médio de resposta


def calculate_avg_response_time(quiz_id, question_index):
    # Obtem todas as chaves de resposta para o quiz específico
    user_keys = redis_client.keys(f"response_time:quiz:{quiz_id}:*")
    total_time = 0.0
    response_count = 0

    for key in user_keys:
        # Obtem o tempo de resposta para a questão específica
        user_response_time = redis_client.hget(key, str(question_index))
        if user_response_time is not None:
            # Converte o tempo para float para cálculo preciso
            total_time += float(user_response_time)
            response_count += 1

    # Retorna None se não houver respostas, senão calcula o tempo médio
    if response_count == 0:
        return None
    return total_time / response_count


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

    # Verifica se o usuário já votou nessa pergunta
    existing_vote = redis_client.hget(
        f"user_responses:{quiz_id}:{user_id}", question_index)
    if existing_vote:
        raise HTTPException(
            status_code=400, detail="Você já votou nesta pergunta.")

    correct_answer = question['correct_answer']

    # Controla o tempo de resposta
    start_time = get_vote_time(quiz_id, question_index, user_id)

    # Atualiza o ranking e o contador de votos
    update_rankings(quiz_id, user_id, question_index,
                    alternative, correct_answer, start_time)

    return {"message": "Voto registrado com sucesso!"}

# Rota para visualizar os resultados de cada pergunta


@app.get("/quizzes/{quiz_id}/resultados/")
async def visualizar_resultados(quiz_id: str):
    resultados = []

    question_index = 0
    while True:
        # Corrige o formato da chave para incluir o prefixo correto
        vote_key = f"vote:quiz:{quiz_id}:{question_index}"

        # Verifica se a chave de votos existe no Redis
        votos = redis_client.hgetall(vote_key)

        # Log de depuração para confirmar os dados
        # print(f"Chave consultada: {vote_key}, Dados retornados: {votos}")

        if not votos:  # Sai do loop se não houver mais perguntas
            break

        # Converte votos para um dicionário legível
        votos_formatados = {
            k.decode() if isinstance(k, bytes) else k: int(v.decode()) if isinstance(v, bytes) else int(v)
            for k, v in votos.items()
        }

        # Adiciona os votos ao resultado
        resultados.append({
            "pergunta": f"Pergunta {question_index + 1}",
            "votos": votos_formatados
        })

        question_index += 1

    if not resultados:
        raise HTTPException(
            status_code=404, detail="Nenhum resultado encontrado para este quiz.")

    return {"resultados": resultados}


# Rota para ranking de alternativas mais votadas

@app.get("/quizzes/{quiz_id}/ranking/alternativas/")
async def ranking_alternativas(quiz_id: str):
    rankings = []

    question_index = 0
    while True:
        # Define a chave correta para buscar os votos
        vote_key = f"vote:quiz:{quiz_id}:{question_index}"

        # Obtém os votos da pergunta atual
        votos = redis_client.hgetall(vote_key)

        # Log para verificar as chaves e dados retornados
        # print(f"Chave consultada: {vote_key}, Dados retornados: {votos}")

        if not votos:  # Interrompe se não houver mais perguntas
            break

        # Converte votos para um formato utilizável
        votos_formatados = {
            k.decode() if isinstance(k, bytes) else k: int(v.decode()) if isinstance(v, bytes) else int(v)
            for k, v in votos.items()
        }

        # Identifica a alternativa mais votada (ou alternativas em caso de empate)
        max_votes = max(votos_formatados.values())
        alternativas_max = [
            alternativa for alternativa, count in votos_formatados.items() if count == max_votes
        ]

        # Adiciona o ranking para a pergunta atual
        rankings.append({
            "pergunta": f"Pergunta {question_index + 1}",
            "alternativas_mais_votadas": alternativas_max,
            "votos": max_votes
        })

        question_index += 1

    if not rankings:
        raise HTTPException(
            status_code=404, detail="Nenhum ranking encontrado para este quiz.")

    return {"ranking": rankings}


@app.get("/quizzes/{quiz_id}/ranking/questoes/")
async def ranking_questoes(quiz_id: str):
    # Obter os dados do quiz do Redis
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz = json.loads(quiz_data)
    question_ranking = []

    # Itera sobre cada pergunta no quiz
    for i, pergunta in enumerate(quiz['questions']):
        # Recupera o contador de respostas corretas para a resposta correta da questão
        correct_answer = pergunta.get('correct_answer')
        if correct_answer is None:
            continue  # Pula perguntas sem uma resposta correta especificada

        # Busca o total de votos para a resposta correta desta pergunta
        correct_count = int(redis_client.hget(
            f"vote:quiz:{quiz_id}:{i}", correct_answer) or 0)

        # Adiciona ao ranking
        question_ranking.append({
            "question": pergunta['question'],
            "correct_answers": correct_count
        })

    # Verifica se todos os votos estão em zero e retorna uma mensagem apropriada
    if all(item["correct_answers"] == 0 for item in question_ranking):
        return {"message": "Todas as questões têm contagem de respostas corretas igual a zero."}

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

# Rota para obter ranking de tempo médio de resposta


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


# Ranking de alunos com maior acerto
@app.get("/quizzes/{quiz_id}/ranking/acerto/")
async def ranking_acerto(quiz_id: str):
    # Verifica se o quiz existe
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    print(f"Quiz data: {quiz_data}")  # Adicionado para debug
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    # Recupera os dados de acertos do Redis para o quiz
    correct_answers = redis_client.hgetall(f"correct_answers:quiz:{quiz_id}")
    print(f"Dados de acertos: {correct_answers}")  # Adicionado para debug

    # Se não houver acertos, retornamos uma mensagem
    if not correct_answers:
        raise HTTPException(
            status_code=404, detail="Nenhum acerto encontrado para este quiz.")

    # Converte os dados de bytes para string e int
    acertos_ranking = [
        {"user_id": user_id.decode(), "acertos": int(acertos.decode())}
        for user_id, acertos in correct_answers.items()
    ]

    # Ordena o ranking baseado nos acertos de forma decrescente
    acertos_ranking = sorted(
        acertos_ranking, key=lambda x: x["acertos"], reverse=True)

    return {"ranking_acerto": acertos_ranking}


# Ranking de rapidez
@app.get("/quizzes/{quiz_id}/ranking/rapidez/")
async def ranking_rapidez(quiz_id: str):
    rapidez_ranking = []

    # Recupera os tempos de resposta diretamente do Redis (os resultados já estão ordenados)
    response_times = redis_client.zrangebyscore(
        f"response_time_rank:quiz:{quiz_id}", '-inf', '+inf', withscores=True)

    # Preenche o ranking com os dados recuperados
    for user_id, time in response_times:
        rapidez_ranking.append(
            {"user_id": user_id.decode(), "response_time": time})

    return {"rapidez_ranking": rapidez_ranking}


# Rota para excluir todos os quizzes
@app.delete("/quizzes/")
async def delete_all_quizzes():
    # Recupera todas as chaves de quizzes armazenados no Redis
    quiz_keys = redis_client.keys("quiz:*")

    for key in quiz_keys:
        redis_client.delete(key)  # Apaga o quiz

    return {"message": "Todos os quizzes foram apagados."}

# Apaga um quiz específico


@app.delete("/quizzes/{quiz_id}")
async def delete_quiz(quiz_id: str):
    # Verifica se o quiz existe no Redis
    if not redis_client.exists(quiz_id):
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    # Apaga o quiz específico
    redis_client.delete(quiz_id)

    # Apaga também as chaves associadas aos contadores de votos das perguntas desse quiz
    quiz_data = json.loads(redis_client.get(quiz_id))
    for i, question in enumerate(quiz_data['questions']):
        # Apaga os contadores de votos
        redis_client.delete(f"vote:{quiz_id}:{i}")

    return {"message": f"Quiz '{quiz_id}' foi apagado com sucesso."}


# Rota com alunos com maior acerto(independente do tempo) e alunos mais rápidos(independente do acerto)
@app.get("/quizzes/{quiz_id}/ranking/geral/")
async def ranking_geral(quiz_id: str):
    # Ranking de maior acerto
    acerto_data = await ranking_acerto(quiz_id)

    # Ranking de mais rápidos
    rapidez_data = await ranking_rapidez(quiz_id)

    # Combina os dados de ambos os rankings
    combined_ranking = []
    for acerto in acerto_data['ranking_acertos']:
        user_id = acerto['user_id']
        acerto_points = acerto['acertos']
        rapidez_points = next(
            (r['response_time'] for r in rapidez_data['ranking_rapidez'] if r['user_id'] == user_id), None)

        combined_ranking.append({
            "user_id": user_id,
            "acertos": acerto_points,
            "response_time": rapidez_points
        })

    # Ordena o ranking final primeiro por acertos, depois por tempo de resposta (mais rápido primeiro)
    combined_ranking = sorted(
        combined_ranking, key=lambda x: (-x['acertos'], x['response_time']))

    return {"ranking_geral": combined_ranking}


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

# Rota para excluir todos as respostas corretas e tempo de resposta


@app.delete("/quizzes/responses-time-and-aswers/")
async def delete_all_responses_time_and_aswers():
    # Recupera todas as chaves de votos e respostas armazenadas no Redis
    correct_aswers_keys = redis_client.keys("correct_answers:*")
    response_time_keys = redis_client.keys("response_time:*")
    response_time_rank_keys = redis_client.keys("response_time_rank:*")

    for key in correct_aswers_keys:
        redis_client.delete(key)

    for key in response_time_keys:
        redis_client.delete(key)

    for key in response_time_rank_keys:
        redis_client.delete(key)

    return {"message": "Todos as respostas de tempo e perguntas corretas foram apagados."}
