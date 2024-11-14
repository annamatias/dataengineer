from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import redis
import json

# Configuração do cliente Redis
redis_client = redis.Redis(
    host='redis-17224.c93.us-east-1-3.ec2.redns.redis-cloud.com',
    port=17224,
    password='UtRsPtFRSlKJWTCc21uWvkiO4jyGgfA3')

# Inicializa o FastAPI
app = FastAPI()

# Configuração do Jinja2 para templates
templates = Jinja2Templates(directory="api_redis/app/static/templates")

# Função para obter os quizzes do Redis
def get_quizzes_from_redis():
    quiz_keys = redis_client.keys("quiz:*")
    quizzes = []
    for key in quiz_keys:
        quiz_data = redis_client.get(key)
        quiz = json.loads(quiz_data)
        quiz["quiz_id"] = key.decode('utf-8')
        quizzes.append(quiz)
    return quizzes

# Página inicial para listar os quizzes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    quizzes = get_quizzes_from_redis()
    return templates.TemplateResponse("index.html", {"request": request, "quizzes": quizzes})

# Página de visualização do quiz
@app.get("/quiz/{quiz_id}", response_class=HTMLResponse)
async def view_quiz(request: Request, quiz_id: str):
    quiz_data = redis_client.get(quiz_id)
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")
    
    quiz = json.loads(quiz_data)
    return templates.TemplateResponse("quiz.html", {"request": request, "quiz": quiz, "quiz_id": quiz_id})

# Página de visualização dos rankings
@app.get("/rankings/{quiz_id}", response_class=HTMLResponse)
async def view_rankings(request: Request, quiz_id: str):
    quiz_data = redis_client.get(quiz_id)
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz não encontrado.")
    
    quiz = json.loads(quiz_data)
    
    # Rankings de alternativas mais votadas
    rankings = []
    for i, pergunta in enumerate(quiz['questions']):
        alternativas = pergunta['alternatives']
        votos = {}
        for alternativa in alternativas:
            votos[alternativa] = int(redis_client.hget(f"vote:{quiz_id}:{i}", alternativa) or 0)
        
        max_votes = max(votos.values())
        for alternativa, count in votos.items():
            if count == max_votes:
                rankings.append({"question": pergunta['question'], "alternative": alternativa, "votes": count})

    return templates.TemplateResponse("rankings.html", {"request": request, "rankings": rankings})
