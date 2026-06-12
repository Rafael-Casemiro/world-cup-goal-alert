import asyncio
from loguru import logger
from app.services.football_api import FootballApiService
from app.database import SessionLocal
from app.models import Match, Team, Statistic
from datetime import datetime, timezone

class DataCollectorService:
    def __init__(self):
        self.api = FootballApiService()
        self.running = False

    def _save_match_and_stats(self, db, match_data, stats_data):
        fixture = match_data.get("fixture", {})
        teams = match_data.get("teams", {})
        goals = match_data.get("goals", {})
        fixture_status = fixture.get("status", {}).get("short", "NS")
        elapsed_time = fixture.get("status", {}).get("elapsed", 0)

        # 1. Salvar ou atualizar os Times
        home_team_data = teams.get("home", {})
        away_team_data = teams.get("away", {})

        home_team = db.query(Team).filter(Team.id == home_team_data.get("id")).first()
        if not home_team:
            home_team = Team(id=home_team_data.get("id"), name=home_team_data.get("name"), logo_url=home_team_data.get("logo"))
            db.add(home_team)

        away_team = db.query(Team).filter(Team.id == away_team_data.get("id")).first()
        if not away_team:
            away_team = Team(id=away_team_data.get("id"), name=away_team_data.get("name"), logo_url=away_team_data.get("logo"))
            db.add(away_team)
            
        db.commit()

        # 2. Salvar ou atualizar a Partida (Match)
        match = db.query(Match).filter(Match.id == fixture.get("id")).first()
        if not match:
            # Pega o timestamp e converte pra datetime UTC
            start_dt = datetime.fromtimestamp(fixture.get("timestamp", 0), tz=timezone.utc)
            match = Match(
                id=fixture.get("id"),
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                started_at=start_dt
            )
            db.add(match)
        
        match.status = fixture_status
        match.minute = elapsed_time
        match.home_score = goals.get("home", 0) or 0
        match.away_score = goals.get("away", 0) or 0
        
        db.commit()

        # 3. Mapear e salvar Estatísticas da partida
        if not stats_data:
            return

        for team_stats in stats_data:
            team_id = team_stats.get("team", {}).get("id")
            stats_list = team_stats.get("statistics", [])
            
            # Função para buscar estatísticas na lista da API
            def get_stat(type_name):
                item = next((s for s in stats_list if s.get("type") == type_name), None)
                if item and item.get("value") is not None:
                    try:
                        # Se for porcentagem ("50%"), removemos o '%'
                        val = str(item.get("value")).replace("%", "")
                        return float(val)
                    except ValueError:
                        return 0.0
                return 0.0

            stat_record = db.query(Statistic).filter(
                Statistic.match_id == match.id,
                Statistic.team_id == team_id
            ).first()

            if not stat_record:
                stat_record = Statistic(match_id=match.id, team_id=team_id)
                db.add(stat_record)

            stat_record.shots_on_target = int(get_stat("Shots on Goal"))
            stat_record.corners = int(get_stat("Corner Kicks"))
            stat_record.dangerous_attacks = int(get_stat("Dangerous attacks"))
            stat_record.expected_goals = get_stat("expected_goals")
        
        db.commit()
        logger.info(f"Dados da partida {match.id} salvos no banco!")

    async def collect_data(self):
        logger.info("Iniciando ciclo de coleta de dados...")
        db = SessionLocal()
        try:
            live_matches = await self.api.get_live_matches()
            
            for match_data in live_matches:
                fixture_id = match_data.get("fixture", {}).get("id")
                if not fixture_id:
                    continue
                
                # Aguarda 1 segundo entre buscas de estatísticas para não tomar block da API gratuita (Rate Limit)
                await asyncio.sleep(1)
                
                stats_data = await self.api.get_match_statistics(fixture_id)
                self._save_match_and_stats(db, match_data, stats_data)
                
        except Exception as e:
            logger.error(f"Erro no ciclo de coleta: {e}")
            db.rollback()
        finally:
            db.close()

    async def start_polling(self, interval_seconds=60):
        self.running = True
        while self.running:
            await self.collect_data()
            logger.info(f"Aguardando {interval_seconds} segundos para a próxima coleta...")
            await asyncio.sleep(interval_seconds)

    async def stop(self):
        self.running = False
        await self.api.close()
