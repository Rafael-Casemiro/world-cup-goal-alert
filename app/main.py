import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Match
from app.services.collector import DataCollectorService

collector = DataCollectorService()

@asynccontextmanager
async def lifespan(app: FastAPI):
     task = asyncio.create_task(collector.start_polling(interval_seconds=60))
     yield

     await collector.stop()
     task.cancel()

app = FastAPI(title="World Cup Goal Alert API", lifespan=lifespan)

@app.get("/health")
def health_check():
     return {"status": "ok"}

@app.get("/matches/live")
def get_live_matches_endpoint(db: Session = Depends(get_db)):
     matches = db.query(Match).filter(Match.status.notin_(["FT", "NS", "AET", "PEN"])).all()


     results = []
     for m in matches:
          results.append({
               "id": m.id,
               "home_team": m.home_team.name if m.home_team else "Desconhecido",
               "away_team": m.away_team.name if m.away_team else "Desconhecido",
               "score": f"{m.home_score} - {m.away_score}",
               "minute": m.minute,
               "status": m.status
          })
     
     return {"live_matches": results, "count": len(results)}