from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from models import FootballResult, Team, TeamScore, Test
from schemas import FootballResultSchema, TeamSchema, TeamScoreSchema, TestSchema

engine = create_engine('postgresql://odoo16:odoo16@localhost:5432/db_dashbaord_score')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

STATIC_TOKEN = "prioratus"

class ConnectionManager:
    """
    Manages WebSocket connections and provides methods for connecting, disconnecting, and broadcasting messages.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Connects a WebSocket client and adds it to the list of active connections.

        Args:
            websocket (WebSocket): The WebSocket client to connect.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Disconnects a WebSocket client and removes it from the list of active connections.

        Args:
            websocket (WebSocket): The WebSocket client to disconnect.
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """
        Broadcasts a message to all connected WebSocket clients.

        Args:
            message (dict): The message to broadcast.
        """
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Función auxiliar para obtener una sesión de base de datos
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# async def get_results(db: SessionLocal):
#     return [{r.team: r.score} for r in db.query(FootballResult).all()]

@app.get('/results')
def get_results(db: SessionLocal = Depends(get_db_session)):
    # Obtener todos los registros de la base de datos PostgreSQL
    results = db.query(FootballResult).all()
    return [{'id':r.id, 'team': r.team, 'score': r.score} for r in results]


@app.post('/results')
async def create_results(result: FootballResultSchema, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    # Verificar el token de autorización
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    
    # Crear o actualizar el registro en la base de datos PostgreSQL
    db_result = FootballResult(team=result.team, score=result.score)
    db.add(db_result)
    db.commit()
    await manager.broadcast(get_results(db))
    
    return {'status': 'success'}

@app.put('/results')
async def update_results(result: FootballResultSchema, db: SessionLocal = Depends(get_db_session)):
    # Actualizar el registro en la base de datos PostgreSQL
    db_result = db.query(FootballResult).filter(FootballResult.team == result.team).first()
    if db_result:
        db_result.score = result.score
        db.commit()
        await manager.broadcast(get_results(db))
        return {'status': 'success'}
    return {'status': 'failure', 'message': 'Team not found'}

@app.delete('/results')
async def delete_results(team: str, db: SessionLocal = Depends(get_db_session)):
    # Eliminar el registro de la base de datos PostgreSQL
    db_result = db.query(FootballResult).filter(FootballResult.team == team).first()
    if db_result:
        db.delete(db_result)
        db.commit()
        await manager.broadcast(get_results(db))
        return {'status': 'success'}
    return {'status': 'failure', 'message': 'Team not found'}

@app.websocket('/ws/results')
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles the WebSocket connection for the endpoint.

    Args:
        websocket (WebSocket): The WebSocket connection object.

    Returns:
        None
    """
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# -------------------------------------------------------------
# Team
# -------------------------------------------------------------
@app.get('/teams', summary='Get all teams',tags=['Teams'])
def get_teams(db: SessionLocal = Depends(get_db_session)):
    result = db.query(Team).all()
    return [{'id': r.id, 'name': r.name} for r in result]

@app.post('/teams', summary='Create a new team', tags=['Teams'])
async def create_team(team: TeamSchema, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    db_team = Team(name=team.name)
    db.add(db_team)
    db.commit()
    return {'status': 'success'}

@app.put('/teams/{id}', summary='Update a team', tags=['Teams'])
async def update_team(id:int, team: TeamSchema, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    db_team = db.query(Team).filter(Team.id == id).first()
    if db_team:
        db_team.name = team.name
        db.commit()
        return {'status': 'success'}
    return {'status': 'failure', 'message': 'Team not found'}

@app.delete('/teams/{id}', summary='Delete a team', tags=['Teams'])
async def delete_team(id:int, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    db_team = db.query(Team).filter(Team.id == id).first()
    print(db_team)
    if db_team:
        db.delete(db_team)
        db.commit()
        return {'status': 'success'}
    return {'status': 'failure', 'message': 'Team not found'}

# -------------------------------------------------------------
# Test
# -------------------------------------------------------------
@app.get('/tests', summary='Get all tests', tags=['Tests'])
def get_tests(db: SessionLocal = Depends(get_db_session)):
    result = db.query(Test).all()
    return [{'id': r.id, 'name': r.name} for r in result]

@app.post('/tests', summary='Create a new test', tags=['Tests'])
async def create_test(test: TestSchema, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    db_test = Test(name=test.name)
    db.add(db_test)
    db.commit()
    return {'status': 'success'}

@app.delete('/tests/{id}', summary='Delete a test', tags=['Tests'])
async def delete_test(id:int, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    db_test = db.query(Test).filter(Test.id == id).first()
    if db_test:
        db.delete(db_test)
        db.commit()
        return {'status': 'success'}
    return {'status': 'failure', 'message': 'Test not found'}

# -------------------------------------------------------------
# TeamScore
# -------------------------------------------------------------
@app.get('/team_scores', summary='Get all team scores', tags=['Team Scores'])
def get_team_scores(db: SessionLocal = Depends(get_db_session)):
    result = db.query(TeamScore).all()
    return [{'id': r.id, 'team_id': r.team_id, 'test_id': r.test_id, 'score': r.score} for r in result]

@app.get('/team_scores_by_team', summary='Get all scores by team', tags=['Team Scores'])   
def get_team_scores_grouped(db: SessionLocal = Depends(get_db_session)):
    team_scors = db.query(TeamScore).all()
    teams= db.query(Team).all()
    teams_name = {t.id: t.name for t in teams}
    total_scores = {}
    for r in team_scors:
        if r.team_id not in total_scores:
            total_scores[r.team_id] = 0
        total_scores[r.team_id] += r.score
    result = [{'team_id': t, 'score': s, 'name':teams_name[t]} for t,s in total_scores.items()]
    print(result)
    return result
        

@app.post('/team_scores', summary='Create a new team score', tags=['Team Scores'])
# async def create_team_score(team_score: TeamScoreSchema, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
async def create_team_score(
    team_id:int=Form(...),
    test_id:int=Form(...),
    score:int=Form(...),
    db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    db_team_score = TeamScore(team_id=team_id, test_id=test_id, score=score)
    db.add(db_team_score)
    db.commit()
    await manager.broadcast(get_team_scores_grouped(db))
    return {'status': 'success'}

@app.delete('/team_scores/{id}', summary='Delete a team score', tags=['Team Scores'])
async def delete_team_score(id:int, db: SessionLocal = Depends(get_db_session), token: str = Header(default=None)):
    if token != STATIC_TOKEN:
        return {'status': 'failure', 'message': 'Unauthorized'}
    db_team_score = db.query(TeamScore).filter(TeamScore.id == id).first()
    if db_team_score:
        db.delete(db_team_score)
        db.commit()
        await manager.broadcast(get_team_scores_grouped(db))
        return {'status': 'success'}
    return {'status': 'failure', 'message': 'Team score not found'}

