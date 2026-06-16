import os
import httpx
from loguru import logger

class FootballApiService:
     def __init__(self):
          self.api_key = os.getenv("API_SPORTS_KEY", "")
          self.host = os.getenv("API_SPORTS_HOST", "v3.football.api-sports.io")
          self.base_url = f"https://{self.host}"

          self.headers = {
               "x-rapidapi-key": self.api_key,
               "x-rapidapi-host": self.host
          }

          self.client = httpx.AsyncClient(headers=self.headers, base_url=self.base_url, timeout=10.0)

     async def __aenter__(self):
          return self

     async def __aexit__(self, *args):
          await self.client.aclose()

     async def get_live_matches(self):
          try:
               league_id = os.getenv("LEAGUE_ID", "1")
               response = await self.client.get(f"/fixtures?live=all&league={league_id}")
               response.raise_for_status()
               data = response.json()
               logger.info(f"Busca de partidas ao vivo concluídas: {data.get('results', 0)} partidas encontradas.")
               return data.get("response", [])
          except httpx.HTTPStatusError as e:
               logger.error(f"Erro HTTP {e.response.status_code} ao buscar partidas ao vivo: {e}")
               return []
          except httpx.RequestError as e:
               logger.error(f"Erro de conexão ao buscar partidas ao vivo: {e}")
               return []

     async def get_match_statistics(self, fixture_id: int):
          try:
               response = await self.client.get(f"/fixtures/statistics?fixture={fixture_id}")
               response.raise_for_status()
               data = response.json()
               logger.info(f"Estatísticas coletadas para a partida {fixture_id}")
               return data.get("response", [])
          except httpx.HTTPStatusError as e:
               logger.error(f"Erro HTTP {e.response.status_code} ao buscar estatísticas da partida {fixture_id}: {e}")
               return []
          except httpx.RequestError as e:
               logger.error(f"Erro de conexão ao buscar estatísticas da partida {fixture_id}: {e}")
               return []
     
     async def get_match_details(self, fixture_id: int):
          try:
               response = await self.client.get(f"/fixtures?id={fixture_id}")
               response.raise_for_status()
               data = response.json()
               responses = data.get("response", [])
               return responses[0] if responses else {}
          except Exception as e:
               logger.error(f"Erro ao buscar detalhes da partida {fixture_id}: {e}")
               return {}

