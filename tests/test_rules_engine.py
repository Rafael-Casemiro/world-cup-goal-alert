import pytest
from app.services.rules_engine import RulesEngine, PreviousStats
from app.models import Match, Statistic


@pytest.fixture
def engine():
    return RulesEngine()


class TestRuleMomentumAcceleration:
    def test_fires_when_shots_on_target_jump_at_least_3(self, engine):
        match = Match(minute=30, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=6, corners=2, dangerous_attacks=20, expected_goals=0.5)
        previous = PreviousStats(shots_on_target=2, corners=2, dangerous_attacks=20, expected_goals=0.5)

        passed, score, name = engine.rule_momentum_acceleration(match, stats, previous)

        assert passed is True
        assert score == 1.5
        assert name == "Aceleração de Pressão"

    def test_fires_when_corners_jump_at_least_3(self, engine):
        match = Match(minute=30, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=2, corners=5, dangerous_attacks=20, expected_goals=0.5)
        previous = PreviousStats(shots_on_target=2, corners=2, dangerous_attacks=20, expected_goals=0.5)

        passed, score, name = engine.rule_momentum_acceleration(match, stats, previous)

        assert passed is True

    def test_fires_when_dangerous_attacks_jump_at_least_15(self, engine):
        match = Match(minute=30, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=2, corners=2, dangerous_attacks=40, expected_goals=0.5)
        previous = PreviousStats(shots_on_target=2, corners=2, dangerous_attacks=20, expected_goals=0.5)

        passed, score, name = engine.rule_momentum_acceleration(match, stats, previous)

        assert passed is True

    def test_does_not_fire_without_previous_stats(self, engine):
        match = Match(minute=30, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=6, corners=2, dangerous_attacks=20, expected_goals=0.5)

        passed, score, name = engine.rule_momentum_acceleration(match, stats, None)

        assert passed is False

    def test_does_not_fire_when_deltas_below_threshold(self, engine):
        match = Match(minute=30, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=3, corners=2, dangerous_attacks=25, expected_goals=0.5)
        previous = PreviousStats(shots_on_target=2, corners=2, dangerous_attacks=20, expected_goals=0.5)

        passed, score, name = engine.rule_momentum_acceleration(match, stats, previous)

        assert passed is False


class TestRuleTrailingTeamPressure:
    def test_fires_when_home_team_trailing_and_pressing_after_minute_60(self, engine):
        match = Match(minute=65, home_score=0, away_score=1, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=5, corners=1, dangerous_attacks=10, expected_goals=0.5)

        passed, score, name = engine.rule_trailing_team_pressure(match, stats, None)

        assert passed is True
        assert score == 1.0
        assert name == "Pressão de Time Buscando Empate/Virada"

    def test_fires_when_away_team_trailing_and_pressing_after_minute_60(self, engine):
        match = Match(minute=70, home_score=2, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=2, shots_on_target=1, corners=5, dangerous_attacks=10, expected_goals=0.5)

        passed, score, name = engine.rule_trailing_team_pressure(match, stats, None)

        assert passed is True

    def test_does_not_fire_when_team_is_leading(self, engine):
        match = Match(minute=65, home_score=1, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=5, corners=5, dangerous_attacks=10, expected_goals=0.5)

        passed, score, name = engine.rule_trailing_team_pressure(match, stats, None)

        assert passed is False

    def test_does_not_fire_before_minute_60(self, engine):
        match = Match(minute=40, home_score=0, away_score=1, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=5, corners=5, dangerous_attacks=10, expected_goals=0.5)

        passed, score, name = engine.rule_trailing_team_pressure(match, stats, None)

        assert passed is False


class TestRuleScorelessLatePressure:
    def test_fires_when_scoreless_late_with_dangerous_attacks(self, engine):
        match = Match(minute=75, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=1, corners=1, dangerous_attacks=65, expected_goals=0.5)

        passed, score, name = engine.rule_scoreless_late_pressure(match, stats, None)

        assert passed is True
        assert score == 1.0
        assert name == "Jogo Zerado Pressionando"

    def test_does_not_fire_when_there_is_a_goal(self, engine):
        match = Match(minute=75, home_score=1, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=1, corners=1, dangerous_attacks=65, expected_goals=0.5)

        passed, score, name = engine.rule_scoreless_late_pressure(match, stats, None)

        assert passed is False

    def test_does_not_fire_before_minute_70(self, engine):
        match = Match(minute=50, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=1, corners=1, dangerous_attacks=65, expected_goals=0.5)

        passed, score, name = engine.rule_scoreless_late_pressure(match, stats, None)

        assert passed is False

    def test_does_not_fire_when_dangerous_attacks_below_threshold(self, engine):
        match = Match(minute=75, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=1, corners=1, dangerous_attacks=30, expected_goals=0.5)

        passed, score, name = engine.rule_scoreless_late_pressure(match, stats, None)

        assert passed is False


class TestRuleTotalDominance:
    def test_fires_when_all_three_metrics_meet_threshold(self, engine):
        match = Match(minute=40, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=4, corners=4, dangerous_attacks=50, expected_goals=0.5)

        passed, score, name = engine.rule_total_dominance(match, stats, None)

        assert passed is True
        assert score == 1.0
        assert name == "Domínio Total do Jogo"

    def test_does_not_fire_when_shots_below_threshold(self, engine):
        match = Match(minute=40, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=3, corners=4, dangerous_attacks=50, expected_goals=0.5)

        passed, score, name = engine.rule_total_dominance(match, stats, None)

        assert passed is False

    def test_does_not_fire_when_corners_below_threshold(self, engine):
        match = Match(minute=40, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=4, corners=3, dangerous_attacks=50, expected_goals=0.5)

        passed, score, name = engine.rule_total_dominance(match, stats, None)

        assert passed is False

    def test_does_not_fire_when_dangerous_attacks_below_threshold(self, engine):
        match = Match(minute=40, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=4, corners=4, dangerous_attacks=49, expected_goals=0.5)

        passed, score, name = engine.rule_total_dominance(match, stats, None)

        assert passed is False


class TestEvaluateWithPreviousStats:
    def test_new_rule_score_is_included_in_total(self, engine):
        match = Match(minute=30, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=6, corners=2, dangerous_attacks=20, expected_goals=0.5)
        previous = PreviousStats(shots_on_target=2, corners=2, dangerous_attacks=20, expected_goals=0.5)

        result = engine.evaluate(match, stats, previous)

        assert "Aceleração de Pressão" in result["rules_fired"]
        assert result["score"] >= 1.5

    def test_evaluate_still_works_without_previous_stats_argument(self, engine):
        match = Match(minute=75, home_score=0, away_score=0, home_team_id=1, away_team_id=2)
        stats = Statistic(team_id=1, shots_on_target=8, corners=7, dangerous_attacks=10, expected_goals=2.0)

        result = engine.evaluate(match, stats)

        assert result["trigger"] is True
        assert "Pressão no Fim do Jogo" in result["rules_fired"]
