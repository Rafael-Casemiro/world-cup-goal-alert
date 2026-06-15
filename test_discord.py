import asyncio
from unittest.mock import MagicMock
from dotenv import load_dotenv

load_dotenv()

from app.services.discord_notifier import DiscordNotifier

def make_mock_match():
    home = MagicMock()
    home.name = "Brasil"
    away = MagicMock()
    away.name = "Argentina"

    match = MagicMock()
    match.id = 9999
    match.minute = 72
    match.home_score = 1
    match.away_score = 1
    match.home_team = home
    match.away_team = away
    return match

def make_mock_stats():
    stats = MagicMock()
    stats.shots_on_target = 8
    stats.corners = 6
    stats.dangerous_attacks = 42
    stats.expected_goals = 2.3
    return stats

async def main():
    notifier = DiscordNotifier()
    match = make_mock_match()
    stats = make_mock_stats()
    rules_fired = ["Chutes a Gol >= 5", "Escanteios >= 4", "xG >= 1.5"]
    score = 7.8

    print("Enviando alerta de teste para o Discord...")
    await notifier.send_alert(match, stats, rules_fired, score)
    print("Concluído.")

asyncio.run(main())
