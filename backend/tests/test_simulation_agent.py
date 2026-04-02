"""Tests for SimulationAgent."""
import os
import sys
import pytest
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.simulation_agent import SimulationAgent


@pytest.fixture
def agent():
    return SimulationAgent()


def _run_async(coro):
    """Helper to run async coroutine in sync test."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestSimulateWeightLoss:
    """Tests for _simulate_weight_loss method."""

    def test_returns_correct_structure(self, agent):
        result = agent._simulate_weight_loss(0.6, 30.0)
        assert 'intervention' in result
        assert 'projected_risk' in result
        assert 'current_risk' in result
        assert result['intervention'] == 'Weight Loss'

    def test_projected_risk_is_lower(self, agent):
        result = agent._simulate_weight_loss(0.6, 30.0)
        assert result['projected_risk'] < result['current_risk']

    def test_projected_risk_not_negative(self, agent):
        result = agent._simulate_weight_loss(0.1, 30.0)
        assert result['projected_risk'] >= 0.0


class TestSimulateIncreasedActivity:
    """Tests for _simulate_increased_activity method."""

    def test_returns_correct_structure(self, agent):
        result = agent._simulate_increased_activity(0.5, 60)
        assert 'intervention' in result
        assert result['intervention'] == 'Increased Physical Activity'

    def test_projected_risk_not_negative(self, agent):
        result = agent._simulate_increased_activity(0.05, 30)
        assert result['projected_risk'] >= 0.0


class TestSimulateBetterSleep:
    """Tests for _simulate_better_sleep method."""

    def test_returns_correct_structure(self, agent):
        result = agent._simulate_better_sleep(0.5, 5.0)
        assert 'intervention' in result
        assert result['intervention'] == 'Improved Sleep Quality'


class TestSimulateHealthyDiet:
    """Tests for _simulate_healthy_diet method."""

    def test_returns_correct_structure(self, agent):
        result = agent._simulate_healthy_diet(0.5)
        assert 'intervention' in result
        assert result['intervention'] == 'Healthy Diet Adoption'


class TestExecute:
    """Tests for execute method."""

    def test_execute_high_bmi(self, agent):
        task = {'risk_score': 0.6, 'lifestyle_data': {'bmi': 30, 'physical_activity': 50, 'sleep_hours': 5}, 'risk_factors': []}
        result = _run_async(agent.execute(task))
        assert result['status'] == 'success'
        interventions = [s['intervention'] for s in result['simulations']]
        assert 'Weight Loss' in interventions

    def test_execute_always_includes_diet(self, agent):
        task = {'risk_score': 0.5, 'lifestyle_data': {'bmi': 22, 'physical_activity': 200, 'sleep_hours': 8}, 'risk_factors': []}
        result = _run_async(agent.execute(task))
        interventions = [s['intervention'] for s in result['simulations']]
        assert 'Healthy Diet Adoption' in interventions

    def test_execute_best_scenario(self, agent):
        task = {'risk_score': 0.6, 'lifestyle_data': {'bmi': 30, 'physical_activity': 50, 'sleep_hours': 5}, 'risk_factors': []}
        result = _run_async(agent.execute(task))
        assert 'best_scenario' in result
        assert result['best_scenario']['projected_risk'] <= result['current_risk']

    def test_execute_with_empty_data(self, agent):
        task = {'risk_score': 0.5, 'lifestyle_data': {}, 'risk_factors': []}
        result = _run_async(agent.execute(task))
        assert result['status'] == 'success'

    def test_execute_smoker(self, agent):
        task = {'risk_score': 0.5, 'lifestyle_data': {'bmi': 22, 'physical_activity': 200, 'sleep_hours': 8, 'smoking': True}, 'risk_factors': []}
        result = _run_async(agent.execute(task))
        interventions = [s['intervention'] for s in result['simulations']]
        assert 'Smoking Cessation' in interventions
