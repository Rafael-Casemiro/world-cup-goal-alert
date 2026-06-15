import os
import httpx
from loguru import logger
from app.models import Match, Statistic
from dotenv import load_dotenv

load_dotenv()

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    async def send_alert(self, match: Match, stats: Statistic, rules_fired: list, score: float):
        if not self.webhook_url:
            logger.warning("DISCORD_WEBHOOK_URL não configurada no .env. Alerta ignorado.")
            return
        
        title = f"🔥 ALERTA DE JOGO QUENTE: {match.home_team.name} vs {match.away_team.name}"

        regras_formatadas = "\n".join([f"✅ {r}" for r in rules_fired])

        embed = {
            "title": title,
            "color": 16711680,
            "fields": [
                {"name": "⏰ Minuto", "value": f"{match.minute}", "inline": True},
                {"name": "⚽ Placar", "value": f"{match.home_score} - {match.away_score}", "inline": True},
                {"name": "📊 Fator de Pressão", "value": f"chutes a Gol: {stats.shots_on_target}\nEscanteios: {stats.corners}\nAtaques Perigosos: {stats.dangerous_attacks}\nxG (Gols Esperados): {stats.expected_goals}", "inline": False},
                {"name": "⚡ Regras Ativadas", "value": regras_formatadas, "inline": False},
                {"name": "🏆 Score do Sistema", "value": f"{score:.2f} pontos", "inline": False}
            ],
            "footer": {"text": "World Cup Goal Alert System - Sprint 03"}
        }

        payload = {"embeds": [embed]}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                logger.info(f"Alerta do jogo {match.id} enviado com sucesso para o Discord!")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta para o Discord: {e}")