from app.models import Match, Statistic

class RulesEngine:
    def __init__(self):
        # Aqui registramos todas as regras que queremos avaliar
        self.rules = [
            self.rule_late_game_pressure,
            self.rule_high_xg,
            self.rule_momentum,
            self.rule_first_half_pressure
        ]

    def evaluate(self, match: Match, stats: Statistic) -> dict:
        """
        Avalia as estatísticas da partida e decide se deve alertar.
        Retorna: {'trigger': bool, 'score': float, 'rules_fired': list}
        """
        if not stats or not match:
            return {"trigger": False, "score": 0.0, "rules_fired": []}

        # Evita mandar alertas nos primeiros 15 minutos do jogo, pois as estatísticas ainda estão muito "frias"
        # if match.minute < 15:
        #     return {"trigger": False, "score": 0.0, "rules_fired": []}

        total_score = 0.0
        rules_fired = []

        # Passa por todas as regras e soma a pontuação
        for rule in self.rules:
            passed, score, rule_name = rule(match, stats)
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

    def rule_late_game_pressure(self, match: Match, stats: Statistic):
        """Regra 1: Minuto >= 70, Chutes a gol >= 8, Escanteios >= 7"""
        if match.minute >= 70 and stats.shots_on_target >= 8 and stats.corners >= 7:
            return True, 1.5, "Pressão no Fim do Jogo"
        return False, 0.0, ""

    def rule_high_xg(self, match: Match, stats: Statistic):
        """Regra 2: Expected Goals (xG) >= 1.5"""
        if stats.expected_goals >= 1.5:
            return True, 1.0, "xG Alto"
        return False, 0.0, ""

    def rule_momentum(self, match: Match, stats: Statistic):
        """Regra 3: (MODIFICADA PARA TESTE DO DISCORD)"""
        return True, 5.0, "🔧 TESTE DE CONEXÃO DISCORD"

    def rule_first_half_pressure(self, match: Match, stats: Statistic):
        """Regra 4: Pressão no 1º Tempo (Min >= 35) com muitos chutes e escanteios"""
        if 35 <= match.minute <= 45 and stats.shots_on_target >= 5 and stats.corners >= 4:
            return True, 1.5, "Pressão no Fim do 1º Tempo"
        return False, 0.0, ""
