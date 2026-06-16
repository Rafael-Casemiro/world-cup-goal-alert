from asyncio import sleep
from typing import cast
from loguru import logger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Alert
from app.services.football_api import FootballApiService

class AlertValidator:
     def __init__(self):
          self.api = FootballApiService()
     
     async def run_validation(self):
          logger.info("🔎 Iniciando varredura de validação de Alertas Pendentes...")
          db: Session = SessionLocal()
          try:
               alertas_pendentes = db.query(Alert).filter(Alert.success == 0).all()

               if not alertas_pendentes:
                    logger.info("✅ Nenhum alerta pendente no momento.")
                    return
               for alert in alertas_pendentes:
                    if alert.match_id is None:
                         continue
                    match_id = cast(int, alert.match_id)

                    await sleep(1)

                    detalhes = await self.api.get_match_details(match_id)
                    if not detalhes:
                         continue

                    status = detalhes.get("fixture", {}).get("status", {}).get("short", "")

                    if status not in ["FT", "AET", "PEN"]:
                         continue

                    eventos = detalhes.get("events", [])
                    deu_green = False
                    minuto_do_gol = None

                    for evento in eventos:
                         if evento.get("type") == "Goal":
                              minuto = evento.get("time", {}).get("elapsed", 0)

                              if minuto > alert.alert_minute:
                                   deu_green = True
                                   minuto_do_gol = minuto
                                   break
                    if deu_green:
                         logger.success(f"🤑 GREEN! O Alerta do Jogo {match_id} resultou em GOL no minuto {minuto_do_gol}!")
                         alert.success = 1
                         alert.goal_minute = minuto_do_gol
                    else:
                         logger.warning(f"❌ RED! O Alerta do Jogo {match_id} bateu na trave e terminou sem gols depois.")
                         alert.success = -1
                    
                    db.commit()
          except Exception as e:
               logger.error(f"Erro na rotina de validação: {e}")
               db.rollback()
          finally:
               db.close()
               await self.api.client.aclose()