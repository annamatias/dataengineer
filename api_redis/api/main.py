import os
import json
import time
from datetime import timedelta
from typing import List, Dict
from fastapi import FastAPI, HTTPException
import redis
from redis import Redis
from dotenv import load_dotenv

load_dotenv()
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")


class RedisClient:
    def __init__(self, host: str, port: int, password: str):
        self.client = redis.Redis(host=host, port=port, password=password)

    def get_client(self) -> Redis:
        return self.client

    def check_connection(self) -> bool:
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False


redis_client = RedisClient(
    host=redis_host, port=int(redis_port), password=redis_password
).get_client()


class RedisQuizService:
    def __init__(self, client_redis: Redis):
        self.redis_client = client_redis

    def get_quiz_data(self, quiz_id: str) -> Dict:
        quiz_data = self.redis_client.get(f"quiz:{quiz_id}")
        if quiz_data is None:
            raise ValueError(f"Quiz '{quiz_id}' não encontrado.")
        return json.loads(quiz_data)

    def get_votes_for_question(self, quiz_id: str, question_index: int) -> Dict:
        vote_key = f"vote:quiz:{quiz_id}:{question_index}"
        return {
            k.decode(): int(v.decode())
            for k, v in self.redis_client.hgetall(vote_key).items()
        }

    def get_correct_answers(self, quiz_id: str) -> Dict:
        return {
            user_id.decode(): int(acertos.decode())
            for user_id, acertos in self.redis_client.hgetall(
                f"correct_answers:quiz:{quiz_id}"
            ).items()
        }

    def get_abstention_count(self, quiz_id: str, question_index: int) -> int:
        return len(
            self.redis_client.keys(f"vote_time:{quiz_id}:{question_index}:*")
        ) - self.redis_client.hlen(f"vote:{quiz_id}:{question_index}")

    def get_response_time(self, quiz_id: str) -> List[Dict]:
        response_times = self.redis_client.zrangebyscore(
            f"response_time_rank:quiz:{quiz_id}", "-inf", "+inf", withscores=True
        )
        return [
            {"user_id": user_id.decode(), "response_time": time}
            for user_id, time in response_times
        ]


class QuizService:
    @staticmethod
    def get_vote_time(quiz_id: str, question_index: int, user_id: str):
        start_time = time.time()
        redis_client.setex(
            f"vote_time:{quiz_id}:{question_index}:{user_id}",
            timedelta(seconds=20),
            start_time,
        )
        return start_time

    @staticmethod
    def calculate_avg_response_time(quiz_id: str, question_index: int):
        user_keys = redis_client.keys(f"response_time:quiz:{quiz_id}:*")
        total_time = 0.0
        response_count = 0

        for key in user_keys:
            user_response_time = redis_client.hget(key, str(question_index))
            if user_response_time is not None:
                total_time += float(user_response_time)
                response_count += 1

        return None if response_count == 0 else total_time / response_count

    @staticmethod
    def update_rankings(quiz_id, user_id, question_index, alternative, correct_answer, start_time):
        end_time = time.time()
        response_time = end_time - start_time

        redis_client.hset(
            f"user_responses:{quiz_id}:{user_id}", question_index, alternative
        )
        redis_client.hset(
            f"response_time:{quiz_id}:{user_id}", question_index, response_time
        )

        if alternative == correct_answer:
            redis_client.hincrby(f"correct_answers:{quiz_id}", user_id, 1)
        redis_client.zadd(f"response_time_rank:{quiz_id}", {
                          user_id: response_time})
        redis_client.hincrby(
            f"vote:{quiz_id}:{question_index}", alternative, 1)


class QuizManager:
    @staticmethod
    def create_quiz(quiz_request: dict):
        quiz_ids = []
        for quiz in quiz_request["quizzes"]:
            quiz_id = f"quiz:{quiz['title'].replace(' ', '_').lower()}"
            if redis_client.exists(quiz_id):
                raise HTTPException(
                    status_code=400, detail=f"Quiz '{quiz['title']}' já existe."
                )
            redis_client.set(quiz_id, json.dumps(quiz), ex=timedelta(days=30))

            for i, question in enumerate(quiz["questions"]):
                if len(question["alternatives"]) != 4:
                    raise HTTPException(
                        status_code=400,
                        detail="Cada pergunta deve ter exatamente 4 alternativas.",
                    )
                if question["correct_answer"] not in [
                    alt[0] for alt in question["alternatives"]
                ]:
                    raise HTTPException(
                        status_code=400,
                        detail="A resposta correta deve ser uma das alternativas.",
                    )

                for alternative in question["alternatives"]:
                    alt, _ = alternative
                    redis_client.hset(f"vote:{quiz_id}:{i}", alt, 0)

            quiz_ids.append(quiz_id)
        return {"message": "Quizzes criados com sucesso!", "quiz_ids": quiz_ids}

    @staticmethod
    def get_quizzes():
        quiz_keys = redis_client.keys("quiz:*")
        quizzes = []
        for key in quiz_keys:
            quiz_data = redis_client.get(key)
            quiz = json.loads(quiz_data)
            quiz["quiz_id"] = key
            quizzes.append(quiz)
        return {"quizzes": quizzes}

    @staticmethod
    def get_quiz(quiz_id: str):
        quiz_data = redis_client.get(quiz_id)
        if quiz_data is None:
            raise HTTPException(status_code=404, detail="Quiz não encontrado.")
        return {"quiz": json.loads(quiz_data)}


class DeleteQuiz:
    def __init__(self, client_redis):
        self.redis_client = client_redis

    def delete_all_votes_and_user_responses(self):
        vote_keys = self.redis_client.keys("vote:*")
        user_response_keys = self.redis_client.keys("user_responses:*")

        for key in vote_keys:
            self.redis_client.delete(key)

        for key in user_response_keys:
            self.redis_client.delete(key)

        return {"message": "Todos os votos e respostas de usuários foram apagados."}

    def delete_all_responses_time_and_answers(self):
        correct_answers_keys = self.redis_client.keys("correct_answers:*")
        response_time_keys = self.redis_client.keys("response_time:*")
        response_time_rank_keys = self.redis_client.keys(
            "response_time_rank:*")

        for key in correct_answers_keys:
            self.redis_client.delete(key)

        for key in response_time_keys:
            self.redis_client.delete(key)

        for key in response_time_rank_keys:
            self.redis_client.delete(key)

        return {
            "message": "Todos as respostas de tempo e perguntas corretas foram apagados."
        }

    def delete_all_quizzes(self):
        quiz_keys = self.redis_client.keys("quiz:*")

        for key in quiz_keys:
            self.redis_client.delete(key)

        return {"message": "Todos os quizzes foram apagados."}

    def delete_quiz(self, quiz_id: str):
        if not self.redis_client.exists(quiz_id):
            raise HTTPException(status_code=404, detail="Quiz não encontrado.")

        self.redis_client.delete(quiz_id)
        quiz_data = json.loads(self.redis_client.get(quiz_id))
        for i in enumerate(quiz_data["questions"]):
            self.redis_client.delete(f"vote:{quiz_id}:{i}")

        return {"message": f"Quiz '{quiz_id}' foi apagado com sucesso."}


class RankingService:
    def __init__(self, service_redis: RedisQuizService):
        self.redis_service = service_redis

    def get_question_results(self, quiz_id: str) -> List[Dict]:
        resultados = []
        question_index = 0
        while True:
            try:
                votos = self.redis_service.get_votes_for_question(
                    quiz_id, question_index
                )
                if not votos:
                    break
                resultados.append(
                    {"pergunta": f"Pergunta {question_index + 1}", "votos": votos}
                )
            except ValueError:
                break
            question_index += 1
        if not resultados:
            raise ValueError("Nenhum resultado encontrado para este quiz.")
        return resultados

    def get_alternatives_ranking(self, quiz_id: str) -> List[Dict]:
        rankings = []
        question_index = 0
        while True:
            try:
                votos = self.redis_service.get_votes_for_question(
                    quiz_id, question_index)
                if not votos:
                    break

                # Transformar os votos em uma lista ordenada de dicionários
                alternativas_ranking = sorted(
                    [{"alternative": alt, "votes": count}
                        for alt, count in votos.items()],
                    key=lambda x: x["votes"],
                    reverse=True
                )

                rankings.append(
                    {
                        "pergunta": f"Pergunta {question_index + 1}",
                        "ranking_alternativas": alternativas_ranking,
                    }
                )
            except ValueError:
                break
            question_index += 1

        if not rankings:
            raise ValueError("Nenhum ranking encontrado para este quiz.")

        return rankings

    def get_question_ranking(self, quiz_id: str) -> List[Dict]:
        quiz_data = self.redis_service.get_quiz_data(quiz_id)
        question_ranking = []
        for i, pergunta in enumerate(quiz_data["questions"]):
            correct_answer = pergunta.get("correct_answer")
            if correct_answer:
                correct_count = int(
                    self.redis_service.get_votes_for_question(quiz_id, i).get(
                        correct_answer, 0
                    )
                )
                question_ranking.append(
                    {"question": pergunta["question"],
                        "correct_answers": correct_count}
                )
        if not question_ranking:
            raise ValueError("Nenhum ranking de questões encontrado.")
        return question_ranking

    def get_student_ranking(self, quiz_id: str) -> List[Dict]:
        # correct_answers:quiz:quiz_de_geografia
        correct_answers_key = f"correct_answers:quiz:{quiz_id}"
        correct_answers_data = self.redis_service.redis_client.hgetall(
            correct_answers_key)

        if not correct_answers_data:
            raise ValueError(
                f"Nenhum dado de respostas corretas encontrado para o quiz:{quiz_id}")

        ranking = [
            {"student": k.decode("utf-8"),
             "correct_answers": int(v.decode("utf-8"))}
            for k, v in correct_answers_data.items()
        ]

        ranking.sort(key=lambda x: x["correct_answers"], reverse=True)

        return ranking

    def get_abstention_ranking(self, quiz_id: str) -> List[Dict]:
        quiz_data = self.redis_service.get_quiz_data(quiz_id)
        abstencao_ranking = [
            {
                "question": pergunta["question"],
                "abstencao": self.redis_service.get_abstention_count(quiz_id, i),
            }
            for i, pergunta in enumerate(quiz_data["questions"])
        ]
        return abstencao_ranking

    def get_avg_response_time_ranking(self, quiz_id: str) -> List[Dict]:
        quiz_data = self.redis_service.get_quiz_data(quiz_id)
        tempo_medio_ranking = []
        for i, pergunta in enumerate(quiz_data["questions"]):
            avg_time = QuizService.calculate_avg_response_time(quiz_id, i)
            tempo_medio_ranking.append(
                {"question": pergunta["question"], "avg_time": avg_time}
            )
        return tempo_medio_ranking

    def get_combined_ranking(self, quiz_id: str) -> List[Dict]:
        acerto_data = self.get_question_ranking(quiz_id)
        rapidez_data = self.redis_service.get_response_time(quiz_id)
        combined_ranking = []
        for acerto in acerto_data:
            user_id = acerto["user_id"]
            acerto_points = acerto["acertos"]
            rapidez_points = next(
                (r["response_time"]
                 for r in rapidez_data if r["user_id"] == user_id),
                None,
            )
            combined_ranking.append(
                {
                    "user_id": user_id,
                    "acertos": acerto_points,
                    "response_time": rapidez_points,
                }
            )
        return sorted(
            combined_ranking, key=lambda x: (-x["acertos"], x["response_time"])
        )


app = FastAPI()
redis_service = RedisQuizService(redis_client)
delete_quiz = DeleteQuiz(redis_client)
ranking_service = RankingService(redis_service)


@app.post("/quizzes/")
async def create_quiz(quiz_request: dict):
    return QuizManager.create_quiz(quiz_request)


@app.get("/quizzes/")
async def get_quizzes():
    return QuizManager.get_quizzes()


@app.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str):
    return QuizManager.get_quiz(quiz_id)


@app.post("/quizzes/{quiz_id}/votar/")
async def votar(quiz_id: str, question_index: int, alternative: str, user_id: str):
    if not redis_client.exists(quiz_id):
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")

    quiz_data = json.loads(redis_client.get(quiz_id))
    redis_client.set(quiz_id, json.dumps(quiz_data), ex=timedelta(days=30))

    if question_index < 0 or question_index >= len(quiz_data["questions"]):
        raise HTTPException(status_code=400, detail="Pergunta inválida.")
    question = quiz_data["questions"][question_index]
    if alternative not in [alt[0] for alt in question["alternatives"]]:
        raise HTTPException(status_code=400, detail="Alternativa inválida.")

    existing_vote = redis_client.hget(
        f"user_responses:{quiz_id}:{user_id}", question_index
    )
    if existing_vote:
        raise HTTPException(
            status_code=400, detail="Você já votou nesta pergunta.")

    correct_answer = question["correct_answer"]
    start_time = QuizService.get_vote_time(quiz_id, question_index, user_id)
    QuizService.update_rankings(
        quiz_id, user_id, question_index, alternative, correct_answer, start_time
    )

    return {"message": "Voto registrado com sucesso!"}


@app.get("/quizzes/{quiz_id}/resultados/")
async def visualizar_resultados(quiz_id: str):
    try:
        resultados = ranking_service.get_question_results(quiz_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"resultados": resultados}


@app.get("/quizzes/{quiz_id}/ranking/alternativas/")
async def ranking_alternativas(quiz_id: str):
    try:
        rankings = ranking_service.get_alternatives_ranking(quiz_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"ranking": rankings}


@app.get("/quizzes/{quiz_id}/ranking/questoes/")
async def ranking_questoes(quiz_id: str):
    try:
        question_ranking = ranking_service.get_question_ranking(quiz_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"question_ranking": question_ranking}


@app.get("/quizzes/{quiz_id}/ranking/abstencao/")
async def ranking_abstencao(quiz_id: str):
    abstencao_ranking = ranking_service.get_abstention_ranking(quiz_id)
    return {"abstencao_ranking": abstencao_ranking}


@app.get("/quizzes/{quiz_id}/ranking/tempo_medio/")
async def ranking_tempo_medio(quiz_id: str):
    tempo_medio_ranking = ranking_service.get_avg_response_time_ranking(
        quiz_id)
    return {"tempo_medio_ranking": tempo_medio_ranking}


@app.get("/quizzes/{quiz_id}/ranking/rapidez/")
async def ranking_rapidez(quiz_id: str):
    rapidez_ranking = []
    response_times = redis_client.zrangebyscore(
        f"response_time_rank:quiz:{quiz_id}", "-inf", "+inf", withscores=True
    )
    for user_id, tempo in response_times:
        rapidez_ranking.append(
            {"user_id": user_id.decode(), "response_time": tempo})

    return {"rapidez_ranking": rapidez_ranking}


@app.get("/quizzes/{quiz_id}/ranking/acerto/")
async def ranking_acerto(quiz_id: str):
    try:
        acerto_ranking = ranking_service.get_student_ranking(quiz_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"ranking_acerto": acerto_ranking}


@app.get("/quizzes/{quiz_id}/ranking/geral/")
async def ranking_geral(quiz_id: str):
    combined_ranking = ranking_service.get_combined_ranking(quiz_id)
    return {"ranking_geral": combined_ranking}


@app.delete("/quizzes/votos-e-respostas/")
async def delete_all_votes_and_user_responses():
    return delete_quiz.delete_all_votes_and_user_responses()


@app.delete("/quizzes/responses-time-and-aswers/")
async def delete_all_responses_time_and_aswers():
    return delete_quiz.delete_all_responses_time_and_answers()


@app.delete("/quizzes/")
async def delete_all_quizzes():
    return delete_quiz.delete_all_quizzes()


@app.delete("/quizzes/{quiz_id}")
async def delete_quizzes(quiz_id: str):
    return delete_quiz.delete_quiz(quiz_id)
