from dataclasses import dataclass
from typing import Optional
from app.models import Match, Statistic


@dataclass
class PreviousStats:
    """Snapshot das estatísticas do ciclo de coleta anterior, usado para calcular variação (momentum)."""
    shots_on_target: int
    corners: int
    dangerous_attacks: int
    expected_goals: float


class RulesEngine:
    def __init__(self):
        # Aqui registramos todas as regras que queremos avaliar
        self.rules = [
            self.rule_late_game_pressure,
            self.rule_high_xg,
            self.rule_momentum,
            self.rule_first_half_pressure,
            self.rule_momentum_acceleration,
            self.rule_trailing_team_pressure,
            self.rule_scoreless_late_pressure,
            self.rule_total_dominance,
        ]

    def evaluate(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None) -> dict:
        """
        Avalia as estatísticas da partida e decide se deve alertar.
        Retorna: {'trigger': bool, 'score': float, 'rules_fired': list}
        """
        if not stats or not match:
            return {"trigger": False, "score": 0.0, "rules_fired": []}

        # Evita mandar alertas nos primeiros 15 minutos do jogo, pois as estatísticas ainda estão muito "frias"
        if match.minute < 15:
            return {"trigger": False, "score": 0.0, "rules_fired": []}

        total_score = 0.0
        rules_fired = []

        # Passa por todas as regras e soma a pontuação
        for rule in self.rules:
            passed, score, rule_name = rule(match, stats, previous_stats)
            if passed:
                total_score += score
                rules_fired.append(rule_name)

        # Critério de disparo: Score ponderado >= 2.0
        should_trigger = total_score >= 2.0

        return {
            "trigger": should_trigger,
            "score": total_score,
            "rules_fired": rules_fired
        }

    # ================= REGRAS =================

    def rule_late_game_pressure(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 1: Minuto >= 70, Chutes a gol >= 8, Escanteios >= 7"""
        if match.minute >= 70 and stats.shots_on_target >= 8 and stats.corners >= 7:
            return True, 1.5, "Pressão no Fim do Jogo"
        return False, 0.0, ""

    def rule_high_xg(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 2: Expected Goals (xG) >= 1.5"""
        if stats.expected_goals >= 1.5:
            return True, 1.0, "xG Alto"
        return False, 0.0, ""

    def rule_momentum(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 3: Ataques Perigosos >= 75"""
        if stats.dangerous_attacks >= 75:
            return True, 1.0, "Alto Momentum / Pressão"
        return False, 0.0, ""

    def rule_first_half_pressure(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 4: Pressão no 1º Tempo (Min >= 35) com muitos chutes e escanteios"""
        if 35 <= match.minute <= 45 and stats.shots_on_target >= 5 and stats.corners >= 4:
            return True, 1.5, "Pressão no Fim do 1º Tempo"
        return False, 0.0, ""

    def rule_momentum_acceleration(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 5: Aceleração de pressão desde o último ciclo de coleta (delta de estatísticas)"""
        if previous_stats is None:
            return False, 0.0, ""

        delta_shots = stats.shots_on_target - previous_stats.shots_on_target
        delta_corners = stats.corners - previous_stats.corners
        delta_dangerous_attacks = stats.dangerous_attacks - previous_stats.dangerous_attacks

        if delta_shots >= 3 or delta_corners >= 3 or delta_dangerous_attacks >= 15:
            return True, 1.5, "Aceleração de Pressão"
        return False, 0.0, ""

    def rule_trailing_team_pressure(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 6: Time perdendo no placar pressionando a partir do minuto 60"""
        is_home_team = stats.team_id == match.home_team_id
        team_score = match.home_score if is_home_team else match.away_score
        opponent_score = match.away_score if is_home_team else match.home_score
        is_trailing = team_score < opponent_score

        if is_trailing and match.minute >= 60 and (stats.shots_on_target >= 5 or stats.corners >= 5):
            return True, 1.0, "Pressão de Time Buscando Empate/Virada"
        return False, 0.0, ""

    def rule_scoreless_late_pressure(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 7: Jogo 0x0 com pressão a partir do minuto 70"""
        if match.home_score == 0 and match.away_score == 0 and match.minute >= 70 and stats.dangerous_attacks >= 60:
            return True, 1.0, "Jogo Zerado Pressionando"
        return False, 0.0, ""

    def rule_total_dominance(self, match: Match, stats: Statistic, previous_stats: Optional[PreviousStats] = None):
        """Regra 8: Domínio simultâneo em chutes, escanteios e ataques perigosos"""
        if stats.shots_on_target >= 4 and stats.corners >= 4 and stats.dangerous_attacks >= 50:
            return True, 1.0, "Domínio Total do Jogo"
        return False, 0.0, ""
