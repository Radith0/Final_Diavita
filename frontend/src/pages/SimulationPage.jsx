import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { TrendingDown, Target, AlertCircle, Activity, Sparkles } from 'lucide-react'
import Navigation from '../components/Navigation'
import { getPrimaryPlan } from '../services/plans'
import { getLatestResult } from '../services/results'
import { createSimulations } from '../services/api'
import './SimulationPage.css'

function SimulationPage() {
  const [plan, setPlan] = useState(null)
  const [latestResult, setLatestResult] = useState(null)
  const [simulations, setSimulations] = useState([])
  const [loading, setLoading] = useState(true)
  const [runningSimulation, setRunningSimulation] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [planResponse, resultResponse] = await Promise.allSettled([
        getPrimaryPlan(),
        getLatestResult()
      ])

      if (planResponse.status === 'fulfilled') {
        setPlan(planResponse.value.plan)
        // Generate simulations based on the plan
        await generatePlanSimulations(planResponse.value.plan)
      }

      if (resultResponse.status === 'fulfilled') {
        setLatestResult(resultResponse.value.result)
      }

    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const generatePlanSimulations = async (userPlan) => {
    setRunningSimulation(true)
    try {
      // Generate what-if scenarios based on the user's plan type
      const scenarioData = {
        baseline_data: latestResult?.lifestyle_data || {},
        plan_type: userPlan.plan_type,
        scenarios: getPlanScenarios(userPlan.plan_type)
      }

      // Call backend simulation API
      const result = await createSimulations(scenarioData)
      setSimulations(result.what_if_simulations || [])

    } catch (error) {
      console.error('Error generating simulations:', error)
      // Use mock data for now
      setSimulations(getMockSimulations(userPlan.plan_type))
    } finally {
      setRunningSimulation(false)
    }
  }

  const getPlanScenarios = (planType) => {
    const scenarios = {
      weight_loss: [
        { name: 'Lose 5 lbs in 6 weeks', changes: { weight: -5 } },
        { name: 'Lose 10 lbs in 3 months', changes: { weight: -10 } },
        { name: 'Lose 20 lbs in 6 months', changes: { weight: -20 } }
      ],
      exercise: [
        { name: '15 min daily walking', changes: { activity: 105 } },
        { name: '30 min daily exercise', changes: { activity: 210 } },
        { name: '60 min 5x per week', changes: { activity: 300 } }
      ],
      diet: [
        { name: 'Reduce sugar intake', changes: { diet: 'good' } },
        { name: 'Mediterranean diet', changes: { diet: 'excellent' } },
        { name: 'Plant-based diet', changes: { diet: 'excellent' } }
      ],
      lifestyle: [
        { name: 'Light lifestyle improvement', changes: { weight: -5, activity: 105 } },
        { name: 'Moderate lifestyle change', changes: { weight: -10, activity: 210, diet: 'good' } },
        { name: 'Complete transformation', changes: { weight: -20, activity: 300, diet: 'excellent' } }
      ]
    }

    return scenarios[planType] || scenarios.lifestyle
  }

  const getMockSimulations = (planType) => {
    const baseRisk = latestResult?.combined_risk || 45

    return getPlanScenarios(planType).map((scenario, idx) => ({
      scenario: scenario.name,
      difficulty: idx === 0 ? 'easy' : idx === 1 ? 'moderate' : 'challenging',
      predicted_risk_reduction: `${10 + (idx * 10)}-${20 + (idx * 15)}%`,
      new_risk_score: baseRisk * (1 - (0.15 + idx * 0.15)),
      impact_level: idx === 0 ? 'moderate' : idx === 1 ? 'high' : 'very high',
      timeline: idx === 0 ? '6-8 weeks' : idx === 1 ? '3 months' : '6 months',
      description: scenario.name
    }))
  }

  if (loading) {
    return (
      <>
        <Navigation />
        <div className="simulation-page">
          <div className="loading">
            <Activity className="loading-icon" />
            <p>Loading simulations...</p>
          </div>
        </div>
      </>
    )
  }

  if (!plan) {
    return (
      <>
        <Navigation />
        <div className="simulation-page">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="no-plan-state"
          >
            <AlertCircle size={64} color="#FF9800" />
            <h2>Choose a Plan First</h2>
            <p>What-if simulations are personalized based on your active health plan</p>
            <button className="cta-button" onClick={() => navigate('/plans')}>
              Select Your Plan
            </button>
          </motion.div>
        </div>
      </>
    )
  }

  const getDifficultyColor = (difficulty) => {
    const colors = {
      'easy': '#4CAF50',
      'moderate': '#FF9800',
      'challenging': '#F44336'
    }
    return colors[difficulty] || '#999'
  }

  const getImpactColor = (impact) => {
    const colors = {
      'moderate': '#3498DB',
      'high': '#2ECC71',
      'very high': '#27AE60'
    }
    return colors[impact] || '#999'
  }

  return (
    <>
      <Navigation />
      <div className="simulation-page">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="simulation-content"
        >
          {/* Plan Context Banner */}
          <div className="plan-context-banner">
            <Target size={24} />
            <div>
              <h3>Simulations for: {plan.plan_name}</h3>
              <p>Explore different scenarios to achieve your health goals</p>
            </div>
          </div>

          {/* Header */}
          <div className="simulation-header">
            <h1>
              <Sparkles size={32} />
              What-If Scenarios
            </h1>
            <p>Explore how different approaches can help you achieve your plan goals and reduce diabetes risk</p>

            {latestResult && (
              <div className="current-risk-display">
                <span>Current Risk:</span>
                <strong>{latestResult.combined_risk?.toFixed(1)}%</strong>
              </div>
            )}
          </div>

          {/* Simulations Grid */}
          {runningSimulation ? (
            <div className="generating-simulations">
              <Activity className="spin-icon" />
              <p>Generating personalized simulations...</p>
            </div>
          ) : (
            <div className="simulations-grid">
              {simulations.map((sim, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="simulation-card"
                >
                  <div className="sim-header">
                    <h3>{sim.scenario || sim.description}</h3>
                    <div className="sim-badges">
                      <span
                        className="badge difficulty"
                        style={{ backgroundColor: `${getDifficultyColor(sim.difficulty)}20`, color: getDifficultyColor(sim.difficulty) }}
                      >
                        {sim.difficulty}
                      </span>
                      <span
                        className="badge impact"
                        style={{ backgroundColor: `${getImpactColor(sim.impact_level)}20`, color: getImpactColor(sim.impact_level) }}
                      >
                        {sim.impact_level} impact
                      </span>
                    </div>
                  </div>

                  <div className="sim-metrics">
                    <div className="metric">
                      <span className="metric-label">Risk Reduction</span>
                      <span className="metric-value">{sim.predicted_risk_reduction}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">New Risk Score</span>
                      <span className="metric-value success">{sim.new_risk_score?.toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Timeline</span>
                      <span className="metric-value">{sim.timeline}</span>
                    </div>
                  </div>

                  <p className="sim-description">{sim.description}</p>

                  <div className="sim-note">
                    💡 This scenario aligns with your {plan.plan_name}
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          <div className="simulation-footer">
            <p>These simulations are generated based on your active health plan: <strong>{plan.plan_name}</strong></p>
            <p>Want to see different scenarios? <button className="link-button" onClick={() => navigate('/plans')}>Change your plan</button></p>
          </div>
        </motion.div>
      </div>
    </>
  )
}

export default SimulationPage
