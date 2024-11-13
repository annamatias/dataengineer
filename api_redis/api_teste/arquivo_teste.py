from fastapi import FastAPI, HTTPException
import redis
import json
import time
from uuid import uuid4

# Configuração do cliente Redis
redis_client = redis.Redis(
  host='redis-17224.c93.us-east-1-3.ec2.redns.redis-cloud.com',
  port=17224,
  password='UtRsPtFRSlKJWTCc21uWvkiO4jyGgfA3')

# Inicializa o FastAPI
app = FastAPI()

# Rota para criar os quizzes
@app.post("/quizzes/")
async def create_quiz(quiz_request: dict):
    quiz_ids = []  # Lista para armazenar os quiz_ids gerados
    # Iterar sobre a lista de quizzes recebida no corpo da requisição
    for quiz in quiz_request['quizzes']:
        # Gerar um ID único para o quiz
        quiz_id = f"quiz:{quiz['title'].replace(' ', '_').lower()}"
        
        # Verifica se o quiz já existe no Redis
        if redis_client.exists(quiz_id):
            raise HTTPException(status_code=400, detail=f"Quiz '{quiz['title']}' já existe.")
        
        # Armazenar o quiz em formato JSON no Redis
        redis_client.set(quiz_id, json.dumps(quiz))
        
        # Inicializa os contadores de votos para cada pergunta e alternativa
        for i, question in enumerate(quiz['questions']):
            for alternative in question['alternatives']:
                redis_client.set(f"vote:{quiz_id}:{i}:{alternative}", 0)  # Inicializa o contador de votos para a alternativa
        
        # Adiciona o quiz_id à lista para retornar depois
        quiz_ids.append(quiz_id)

    # Retornar os quiz_ids criados
    return {"message": "Quizzes criados com sucesso!", "quiz_ids": quiz_ids}

# Rota para obter todos os quizzes
@app.get("/quizzes/")
async def get_quizzes():
    # Recupera todas as chaves de quizzes armazenados no Redis
    quiz_keys = redis_client.keys("quiz:*")  # Chaves que começam com "quiz:"
    
    quizzes = []
    for key in quiz_keys:
        # Para cada chave, pega o quiz armazenado e o decodifica
        quiz_data = redis_client.get(key)
        quiz = json.loads(quiz_data)  # Converte o JSON armazenado em um dicionário
        
        # Adiciona o quiz_id no início de cada quiz
        quiz["quiz_id"] = key
        
        # Adiciona o quiz completo (com o quiz_id) à lista
        quizzes.append(quiz)
        
    return {"quizzes": quizzes}

# Rota para votar em uma alternativa de um quiz
@app.post("/quizzes/{quiz_id}/votar/")
async def votar(quiz_id: str, question_index: int, alternative: str):
    # Verifica se o quiz existe
    if not redis_client.exists(quiz_id):
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")
    
    # Verifica se a pergunta e alternativa são válidas
    quiz_data = json.loads(redis_client.get(quiz_id))
    if question_index < 0 or question_index >= len(quiz_data['questions']):
        raise HTTPException(status_code=400, detail="Pergunta inválida.")
    
    question = quiz_data['questions'][question_index]
    if alternative not in [alt[0] for alt in question['alternatives']]:
        raise HTTPException(status_code=400, detail="Alternativa inválida.")
    
    # Atualiza o contador de votos
    redis_client.incr(f"vote:{quiz_id}:{question_index}:{alternative}")

    return {"message": "Voto registrado com sucesso!"}

# Rota para obter um quiz específico
@app.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: str):
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")
    
    return json.loads(quiz_data)

# Rota para visualizar os contadores de votos em tempo real
@app.get("/quizzes/{quiz_id}/resultados/")
async def visualizar_resultados(quiz_id: str):
    # Verifica se o quiz existe
    quiz_data = redis_client.get(f"quiz:{quiz_id}")
    if quiz_data is None:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")
    
    # Converte o JSON do quiz para um objeto Python
    quiz = json.loads(quiz_data)
    
    resultados = []
    for i, pergunta in enumerate(quiz['questions']):
        alternativas = pergunta['alternatives']
        votos = {}
        
        for alternativa in alternativas:
            # Ajuste na consulta para garantir que o formato da chave seja correto
            votos[alternativa] = int(redis_client.get(f"vote:{quiz_id}:{i}:{alternativa}") or 0)
        
        resultados.append({"pergunta": pergunta['question'], "votos": votos})
    
    return {"resultados": resultados}

# Rota para excluir todos os quizzes
@app.delete("/quizzes/")
async def delete_all_quizzes():
    # Recupera todas as chaves de quizzes armazenados no Redis
    quiz_keys = redis_client.keys("quiz:*")
    
    for key in quiz_keys:
        redis_client.delete(key)  # Apaga o quiz
    
    return {"message": "Todos os quizzes foram apagados."}
