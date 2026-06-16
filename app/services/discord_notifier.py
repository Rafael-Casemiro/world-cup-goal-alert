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
        
        # Cor dinâmica baseada no score da partida
        color = 0xFF4500 # Laranja-avermelhado padrão
        if score >= 5.0:
            color = 0xFF0000 # Vermelho puro (Pegando fogo)
        elif score < 3.0:
            color = 0xFFA500 # Laranja mais suave

        # Monta a URL de busca no Google para o jogo
        search_query = f"{match.home_team.name}+vs+{match.away_team.name}".replace(" ", "+")

        total_gols = match.home_score + match.away_score
        linha_gol = total_gols + 0.5
        
        sugestao_aposta = f"**+ {linha_gol} Gols na Partida**"
        if match.minute <= 45:
            sugestao_aposta = f"**+ {linha_gol} Gols no 1º Tempo (HT)**"

        embed = {
            "title": f"⚽ {match.home_team.name} vs {match.away_team.name}",
            "url": f"https://www.google.com/search?q={search_query}",
            "color": color,
            "author": {
                "name": "🔥 ALERTA DE JOGO QUENTE!",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/1165/1165187.png"
            },
            "fields": [
                {"name": "⏰ Minuto", "value": f"**{match.minute}'**", "inline": True},
                {"name": "🏆 Placar", "value": f"**{match.home_score} - {match.away_score}**", "inline": True},
                {"name": "📈 Score do Sistema", "value": f"**{score:.2f} pts**", "inline": True},
                
                {"name": "───────────────", "value": "**📊 FATOR DE PRESSÃO**", "inline": False},
                
                {"name": "🎯 Chutes no Alvo", "value": f"` {stats.shots_on_target} `", "inline": True},
                {"name": "🚩 Escanteios", "value": f"` {stats.corners} `", "inline": True},
                {"name": "⚔️ Atq. Perigosos", "value": f"` {stats.dangerous_attacks} `", "inline": True},
                {"name": "⚽ xG (Gols Esp.)", "value": f"` {stats.expected_goals:.2f} `", "inline": True},
                
                {"name": "───────────────", "value": "💡 **SUGESTÃO DE ENTRADA**", "inline": False},
                {"name": "Mercado de Gols", "value": f"👉 Entrar em {sugestao_aposta}", "inline": True}
            ]
        }

        payload = {"embeds": [embed]}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                logger.info(f"Alerta do jogo {match.id} enviado com sucesso para o Discord!")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta para o Discord: {e}")