"""Tests for RiskScorer."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.fusion.risk_scorer import RiskScorer


@pytest.fixture
def scorer():
    return RiskScorer()


class TestGetRiskLevel:
    """Tests for _get_risk_level method."""

    def test_low_risk(self, scorer):
        assert scorer._get_risk_level(0.2) == 'low'

    def test_moderate_risk(self, scorer):
        assert scorer._get_risk_level(0.4) == 'moderate'

    def test_high_risk(self, scorer):
        assert scorer._get_risk_level(0.6) == 'high'

    def test_very_high_risk(self, scorer):
        assert scorer._get_risk_level(0.8) == 'very_high'


class TestCalculateConfidence:
    """Tests for _calculate_confidence method."""

    def test_base_confidence(self, scorer):
        """Base confidence with no retinal and no lifestyle factors."""
        conf = scorer._calculate_confidence(0.4, {}, [])
        assert conf == 0.75

    def test_retinal_data_increases_confidence(self, scorer):
        """Retinal data should increase confidence."""
        conf = scorer._calculate_confidence(0.4, {'some': 'data'}, [])
        assert conf > 0.75

    def test_many_lifestyle_factors_increase_confidence(self, scorer):
        """3+ lifestyle factors should increase confidence."""
        factors = [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
        conf = scorer._calculate_confidence(0.4, {}, factors)
        assert conf > 0.75

    def test_borderline_score_decreases_confidence(self, scorer):
        """Score near threshold (0.3, 0.5, 0.7) should decrease confidence."""
        conf = scorer._calculate_confidence(0.31, {}, [])
        assert conf < 0.75

    def test_confidence_capped_at_095(self, scorer):
        """Confidence should not exceed 0.95."""
        factors = [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
        conf = scorer._calculate_confidence(0.5, {'data': True}, factors)
        assert conf <= 0.95

    def test_confidence_floor_at_050(self, scorer):
        """Confidence should not go below 0.50."""
        # borderline score with no data
        conf = scorer._calculate_confidence(0.30, {}, [])
        assert conf >= 0.50


class TestAssess:
    """Tests for assess method."""

    def test_assess_returns_expected_keys(self, scorer):
        """Assessment should contain all expected keys."""
        result = scorer.assess(0.4, {}, [])
        assert 'risk_level' in result
        assert 'confidence' in result
        assert 'interpretation' in result
        assert 'priority' in result
        assert 'recommended_action' in result

    def test_assess_low_risk(self, scorer):
        """Low score should produce low risk assessment."""
        result = scorer.assess(0.1, {}, [])
        assert result['risk_level'] == 'low'
        assert result['priority'] == 'routine'

    def test_assess_very_high_risk(self, scorer):
        """High score should produce very_high risk assessment."""
        result = scorer.assess(0.9, {}, [])
        assert result['risk_level'] == 'very_high'
        assert result['priority'] == 'critical'
