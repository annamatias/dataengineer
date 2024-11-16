import os
import json
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from api.main import app, RedisClient


load_dotenv()
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')


redis_client = RedisClient(
    host=redis_host,
    port=int(redis_port),
    password=redis_password
).get_client()


print(redis_client.ping())

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_redis():
    # Cria uma chave para armazenar dados durante os testes
    redis_client.set('test:quiz:key', json.dumps({'test': 'data'}))
    yield
    # Limpa as chaves após os testes
    redis_client.delete('test:quiz:key')


def test_create_quiz(setup_redis):
    quiz_data = {
        "quizzes": [
            {
                "title": "Quiz de Geografia",
                "questions": [
                    {
                        "question": "Qual é a capital da França?",
                        "alternatives": [
                            ["A", "Paris"],
                            ["B", "Londres"],
                            ["C", "Roma"],
                            ["D", "Berlim"]
                        ],
                        "correct_answer": "A"
                    }
                ]
            }
        ]
    }

    try:
        response = client.post("/quizzes/", json=quiz_data)

        if response.status_code == 200:
            print(response.json())
            assert "quiz_ids" in response.json()
        else:
            if response.status_code == 400:
                print(
                    f"Erro 400: Quiz '{quiz_data['quizzes'][0]['title']}' já existe.")
                assert response.status_code == 400
            else:
                print(f"Erro inesperado: {response.status_code}")
                assert False, f"Esperado 200 ou 400, mas recebeu {response.status_code}"

    except Exception as e:
        print(f"Erro ao criar quiz: {str(e)}")
        assert False, f"Erro durante o teste: {str(e)}"
