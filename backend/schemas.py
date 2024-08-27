from pydantic import BaseModel

class FootballResultSchema(BaseModel):
    team: str
    score: int

class TeamSchema(BaseModel):
    name: str

class TestSchema(BaseModel):
    name: str

class TeamScoreSchema(BaseModel):
    team_id: int
    test_id: int
    score: int