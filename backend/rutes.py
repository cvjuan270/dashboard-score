from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# ----------------------------------
# websocket
# ----------------------------------

# ----------------------------------
# Teams
# ----------------------------------
@router.get("/teams", response_model=)
async def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return teams
