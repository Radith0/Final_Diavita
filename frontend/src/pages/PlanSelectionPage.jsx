import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Target, TrendingDown, Activity, Apple, Heart, ArrowRight, CheckCircle, Moon, Brain, Sparkles, Clock, Shield, AlertTriangle, TrendingUp } from 'lucide-react'
import Navigation from '../components/Navigation'
import { createPlan, getMyPlans } from '../services/plans'
import { getLatestResult } from '../services/results'
import './PlanSelectionPage.css'

function PlanSelectionPage() {
  const [plans, setPlans] = useState([])
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [generatingPlans, setGeneratingPlans] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()

  // Get analysis results passed from results page
  const analysisResults = location.state?.analysisResults
  const riskData = location.state?.riskData
  const justCompleted = location.state?.justCompleted

  // Safe string conversion helper - moved outside for broader access
  const safeString = (val) => String(val || '')

  useEffect(() => {
    generatePersonalizedPlans()
  }, [])

  const generatePersonalizedPlans = () => {
    setGeneratingPlans(true)

    // Extract key risk factors and recommendations from analysis
    const recommendations = riskData?.recommendations || []
    const keyFactors = analysisResults?.risk_assessment?.lifestyle_analysis?.key_factors || []
    const retinalFindings = analysisResults?.risk_assessment?.retinal_analysis?.findings || {}
    const riskLevel = riskData?.risk_category || 'moderate'
    const combinedRisk = riskData?.combined_risk || 50
    const retinalRisk = riskData?.retinal_risk || 50
    const lifestyleRisk = riskData?.lifestyle_risk || 50

    // Generate personalized plans based on user's specific situation
    const personalizedPlans = []

    // Analyze key risk factors to determine which plans to recommend

    const hasWeightIssue = keyFactors.some(f => safeString(f).toLowerCase().includes('weight') || safeString(f).toLowerCase().includes('bmi'))
    const hasExerciseIssue = keyFactors.some(f => safeString(f).toLowerCase().includes('physical') || safeString(f).toLowerCase().includes('exercise'))
    const hasDietIssue = keyFactors.some(f => safeString(f).toLowerCase().includes('diet') || safeString(f).toLowerCase().includes('nutrition'))
    const hasSleepIssue = keyFactors.some(f => safeString(f).toLowerCase().includes('sleep'))
    const hasStressIssue = keyFactors.some(f => safeString(f).toLowerCase().includes('stress'))
    const hasSmokingIssue = keyFactors.some(f => safeString(f).toLowerCase().includes('smoking'))
    const hasAlcoholIssue = keyFactors.some(f => safeString(f).toLowerCase().includes('alcohol'))
    const hasRetinalIssue = retinalRisk > 70 || retinalFindings.dr_detected

    // Plan 1: Most Critical Issue Plan
    if (hasRetinalIssue) {
      personalizedPlans.push({
        id: 'eye_health_protocol',
        name: 'Eye Health Protection Plan',
        icon: Target,
        color: '#E91E63',
        priority: 'Critical',
        description: 'Specialized plan to protect your vision and prevent retinal damage progression',
        duration: '6-12 months',
        difficulty: 'Comprehensive',
        targetMetric: 'Halt retinal progression',
        personalizedGoals: [
          'Regular eye monitoring every 3 months',
          'Strict blood sugar control (HbA1c < 7%)',
          'Vascular health improvement',
          'Prevent vision complications'
        ],
        whatIfScenarios: [
          { timeline: '3 months', newRisk: Math.max(30, combinedRisk - 15), change: -15, description: 'Initial improvements in blood sugar control' },
          { timeline: '6 months', newRisk: Math.max(25, combinedRisk - 25), change: -25, description: 'Significant retinal health stabilization' },
          { timeline: '12 months', newRisk: Math.max(20, combinedRisk - 35), change: -35, description: 'Major risk reduction with vision protected' }
        ],
        milestones: [
          { name: 'Initial eye exam & baseline', target: 20 },
          { name: 'Blood sugar stabilized', target: 40 },
          { name: 'Follow-up shows improvement', target: 70 },
          { name: 'Vision protected, risk reduced', target: 100 }
        ],
        expectedOutcome: `Prevent vision loss, ${Math.min(35, combinedRisk * 0.4).toFixed(2)}% risk reduction`,
        llmRecommendations: recommendations.filter(r =>
          safeString(r).toLowerCase().includes('eye') ||
          safeString(r).toLowerCase().includes('vision') ||
          safeString(r).toLowerCase().includes('retinal') ||
          safeString(r).toLowerCase().includes('glucose')
        ).slice(0, 3)
      })
    }

    // Plan 2: Lifestyle Modification Plan (always include)
    if (hasExerciseIssue || hasWeightIssue || lifestyleRisk > 60) {
      personalizedPlans.push({
        id: 'active_lifestyle',
        name: 'Active Lifestyle Transformation',
        icon: Activity,
        color: '#2196F3',
        priority: lifestyleRisk > 70 ? 'High' : 'Medium',
        description: 'Progressive exercise and activity plan customized to your fitness level',
        duration: '3-4 months',
        difficulty: 'Progressive',
        targetMetric: '150+ min/week activity + weight loss',
        personalizedGoals: [
          'Build sustainable exercise habits',
          'Lose 5-10% body weight',
          'Improve cardiovascular fitness',
          'Enhance insulin sensitivity'
        ],
        whatIfScenarios: [
          { timeline: '1 month', newRisk: Math.max(30, combinedRisk - 8), change: -8, description: 'Early metabolic improvements' },
          { timeline: '3 months', newRisk: Math.max(25, combinedRisk - 20), change: -20, description: 'Notable fitness gains and weight loss' },
          { timeline: '6 months', newRisk: Math.max(20, combinedRisk - 30), change: -30, description: 'Transformed fitness level' }
        ],
        milestones: [
          { name: 'First week of activity', target: 15 },
          { name: '30 min daily routine', target: 35 },
          { name: 'Target weight loss achieved', target: 70 },
          { name: 'Lifestyle fully transformed', target: 100 }
        ],
        expectedOutcome: `${Math.min(30, combinedRisk * 0.35).toFixed(2)}% risk reduction`,
        llmRecommendations: recommendations.filter(r =>
          safeString(r).toLowerCase().includes('exercise') ||
          safeString(r).toLowerCase().includes('physical') ||
          safeString(r).toLowerCase().includes('weight') ||
          safeString(r).toLowerCase().includes('activity')
        ).slice(0, 3)
      })
    }

    // Plan 3: Nutrition Optimization (always include)
    personalizedPlans.push({
      id: 'nutrition_therapy',
      name: 'Medical Nutrition Therapy',
      icon: Apple,
      color: '#4CAF50',
      priority: hasDietIssue || combinedRisk > 70 ? 'High' : 'Medium',
      description: 'Evidence-based dietary intervention targeting blood sugar control',
      duration: '3-6 months',
      difficulty: 'Moderate',
      targetMetric: 'Optimize glucose & reduce HbA1c',
      personalizedGoals: [
        'Stabilize blood glucose levels',
        'Achieve optimal nutrient balance',
        'Reduce processed foods by 80%',
        'Master carbohydrate counting'
      ],
      whatIfScenarios: [
        { timeline: '2 weeks', newRisk: Math.max(35, combinedRisk - 5), change: -5, description: 'Quick wins from diet changes' },
        { timeline: '2 months', newRisk: Math.max(30, combinedRisk - 18), change: -18, description: 'Blood sugar stabilization' },
        { timeline: '6 months', newRisk: Math.max(25, combinedRisk - 28), change: -28, description: 'Sustained metabolic improvement' }
      ],
      milestones: [
        { name: 'Sugar & processed food eliminated', target: 25 },
        { name: 'Meal planning mastered', target: 50 },
        { name: 'Blood markers improved', target: 75 },
        { name: 'Sustainable eating pattern', target: 100 }
      ],
      expectedOutcome: `${Math.min(28, combinedRisk * 0.32).toFixed(2)}% risk reduction`,
      llmRecommendations: recommendations.filter(r =>
        safeString(r).toLowerCase().includes('diet') ||
        safeString(r).toLowerCase().includes('food') ||
        safeString(r).toLowerCase().includes('nutrition') ||
        safeString(r).toLowerCase().includes('sugar') ||
        safeString(r).toLowerCase().includes('carb')
      ).slice(0, 3)
    })

    // Plan 4: Stress & Sleep Management (if relevant or as 4th plan)
    if (hasSleepIssue || hasStressIssue || personalizedPlans.length < 4) {
      personalizedPlans.push({
        id: 'stress_sleep_recovery',
        name: 'Stress & Sleep Recovery Program',
        icon: Moon,
        color: '#9C27B0',
        priority: hasSleepIssue || hasStressIssue ? 'Medium' : 'Low',
        description: 'Optimize sleep quality and stress management for better glucose control',
        duration: '2-3 months',
        difficulty: 'Easy-Moderate',
        targetMetric: '7-9 hours quality sleep + stress reduction',
        personalizedGoals: [
          'Achieve 7-9 hours consistent sleep',
          'Reduce cortisol and stress hormones',
          'Improve glucose overnight control',
          'Build stress resilience techniques'
        ],
        whatIfScenarios: [
          { timeline: '1 week', newRisk: Math.max(40, combinedRisk - 3), change: -3, description: 'Initial sleep improvements' },
          { timeline: '1 month', newRisk: Math.max(35, combinedRisk - 10), change: -10, description: 'Better stress management' },
          { timeline: '3 months', newRisk: Math.max(30, combinedRisk - 18), change: -18, description: 'Optimized recovery patterns' }
        ],
        milestones: [
          { name: 'Sleep schedule established', target: 30 },
          { name: 'Stress techniques practiced daily', target: 60 },
          { name: 'Quality sleep achieved consistently', target: 85 },
          { name: 'Sustainable habits integrated', target: 100 }
        ],
        expectedOutcome: `${Math.min(18, combinedRisk * 0.2).toFixed(2)}% risk reduction`,
        llmRecommendations: recommendations.filter(r =>
          safeString(r).toLowerCase().includes('sleep') ||
          safeString(r).toLowerCase().includes('stress') ||
          safeString(r).toLowerCase().includes('relax') ||
          safeString(r).toLowerCase().includes('rest')
        ).slice(0, 3)
      })
    }

    // Plan 5: Quick Win Plan (for immediate action)
    if (combinedRisk > 60 || personalizedPlans.length < 4) {
      personalizedPlans.push({
        id: 'quick_wins',
        name: '30-Day Quick Start Program',
        icon: Sparkles,
        color: '#FF9800',
        priority: 'Recommended',
        description: 'Fast-track plan with immediate actionable changes for quick results',
        duration: '30 days',
        difficulty: 'Easy',
        targetMetric: 'Quick 5-10% risk reduction',
        personalizedGoals: [
          'Eliminate sugary drinks completely',
          'Walk 10,000 steps daily',
          'Implement intermittent fasting',
          'Start glucose monitoring'
        ],
        whatIfScenarios: [
          { timeline: '1 week', newRisk: Math.max(45, combinedRisk - 3), change: -3, description: 'Immediate dietary impact' },
          { timeline: '2 weeks', newRisk: Math.max(42, combinedRisk - 6), change: -6, description: 'Early metabolic changes' },
          { timeline: '30 days', newRisk: Math.max(40, combinedRisk - 10), change: -10, description: 'Foundation for long-term success' }
        ],
        milestones: [
          { name: 'First week completed', target: 25 },
          { name: 'Habits forming', target: 50 },
          { name: 'Visible improvements', target: 75 },
          { name: '30-day transformation', target: 100 }
        ],
        expectedOutcome: `${Math.min(10, combinedRisk * 0.15).toFixed(2)}% quick risk reduction`,
        llmRecommendations: recommendations.slice(0, 3)
      })
    }

    // Plan 6: Comprehensive Lifestyle Overhaul (always available as ultimate option)
    personalizedPlans.push({
      id: 'comprehensive_transformation',
      name: 'Complete Diabetes Prevention Program',
      icon: Shield,
      color: '#F44336',
      priority: combinedRisk > 75 ? 'Critical' : 'Recommended',
      description: 'Comprehensive evidence-based program addressing all modifiable risk factors',
      duration: '6-12 months',
      difficulty: 'Comprehensive',
      targetMetric: `Reduce risk below 30%`,
      personalizedGoals: [
        'Address ALL modifiable risk factors',
        'Achieve optimal metabolic health',
        'Build permanent lifestyle changes',
        'Prevent diabetes development'
      ],
      whatIfScenarios: [
        { timeline: '3 months', newRisk: Math.max(30, combinedRisk - 20), change: -20, description: 'Multiple risk factors improving' },
        { timeline: '6 months', newRisk: Math.max(25, combinedRisk - 35), change: -35, description: 'Major lifestyle transformation' },
        { timeline: '12 months', newRisk: Math.max(20, combinedRisk - 45), change: -45, description: 'Maximum achievable risk reduction' }
      ],
      milestones: [
        { name: 'Foundation phase complete', target: 20 },
        { name: 'Multiple habits established', target: 40 },
        { name: 'Significant measurable progress', target: 70 },
        { name: 'Complete transformation achieved', target: 100 }
      ],
      expectedOutcome: `${Math.min(45, combinedRisk * 0.5).toFixed(2)}% total risk reduction`,
      llmRecommendations: recommendations.slice(0, 5)
    })

    // Ensure we have at least 4 plans by adding a preventive monitoring plan if needed
    if (personalizedPlans.length < 4) {
      personalizedPlans.push({
        id: 'preventive_monitoring',
        name: 'Preventive Monitoring Plan',
        icon: AlertTriangle,
        color: '#607D8B',
        priority: 'Low',
        description: 'Regular monitoring and early intervention to maintain current health',
        duration: 'Ongoing',
        difficulty: 'Easy',
        targetMetric: 'Maintain current risk level',
        personalizedGoals: [
          'Regular health check-ups',
          'Track key health metrics',
          'Early intervention when needed',
          'Maintain healthy habits'
        ],
        whatIfScenarios: [
          { timeline: '3 months', newRisk: combinedRisk, change: 0, description: 'Risk level maintained' },
          { timeline: '6 months', newRisk: Math.max(30, combinedRisk - 5), change: -5, description: 'Gradual improvement' },
          { timeline: '12 months', newRisk: Math.max(25, combinedRisk - 10), change: -10, description: 'Slow but steady progress' }
        ],
        milestones: [
          { name: 'Monitoring routine established', target: 25 },
          { name: 'First quarter review', target: 50 },
          { name: 'Half-year assessment', target: 75 },
          { name: 'Annual health goals met', target: 100 }
        ],
        expectedOutcome: `Maintain current health, prevent deterioration`,
        llmRecommendations: recommendations.slice(0, 2)
      })
    }

    // Sort plans by priority and limit to top 5-6 most relevant
    const priorityOrder = { 'Critical': 1, 'High': 2, 'Medium': 3, 'Recommended': 4, 'Low': 5 }
    personalizedPlans.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])

    // Ensure we show 4-6 plans
    const finalPlans = personalizedPlans.slice(0, Math.min(6, Math.max(4, personalizedPlans.length)))

    setPlans(finalPlans)
    setGeneratingPlans(false)
  }

  const handleSelectPlan = async (template) => {
    setLoading(true)
    try {
      const response = await createPlan({
        plan_name: template.name,
        plan_type: template.id,
        description: template.description,
        scenario_parameters: {
          duration: template.duration,
          difficulty: template.difficulty,
          targetMetric: template.targetMetric,
          personalizedGoals: template.personalizedGoals,
          whatIfScenarios: template.whatIfScenarios
        },
        expected_outcomes: {
          risk_reduction: template.expectedOutcome,
          scenarios: template.whatIfScenarios
        },
        milestones: template.milestones,
        is_primary: true,
        llm_recommendations: template.llmRecommendations,
        priority: template.priority
      })

      console.log('✅ Personalized plan created successfully!', response)

      // Navigate to dashboard with refresh flag
      navigate('/dashboard', { state: { planJustCreated: true }, replace: true })

      // Force page reload to fetch new plan
      setTimeout(() => window.location.href = '/dashboard', 100)

    } catch (error) {
      console.error('Error creating plan:', error)
      alert(`Failed to create plan: ${error.response?.data?.message || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (generatingPlans) {
    return (
      <>
        <Navigation />
        <div className="plan-selection-page">
          <div className="loading-container">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="generating-plans"
            >
              <Brain size={48} className="loading-icon" />
              <h2>Generating Your Personalized Health Plans</h2>
              <p>Analyzing your risk factors and creating customized recommendations...</p>
            </motion.div>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <Navigation />
      <div className="plan-selection-page">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="plan-selection-content"
        >
          <div className="page-header">
            {justCompleted && (
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="success-banner"
              >
                <CheckCircle size={24} />
                <span>Your Personalized Health Plans Are Ready!</span>
              </motion.div>
            )}
            <h1>Your Personalized Health Plans</h1>
            <p>We've created {plans.length} custom plans based on your specific risk factors and lifestyle</p>
            {riskData && (
              <div className="risk-summary-banner">
                <div className="risk-item">
                  <span className="risk-label">Current Risk:</span>
                  <span className="risk-value" style={{ color: getRiskColor(riskData.combined_risk) }}>
                    {riskData.combined_risk?.toFixed(2)}%
                  </span>
                </div>
                <div className="risk-item">
                  <span className="risk-label">Category:</span>
                  <span className="risk-value">{riskData.risk_category}</span>
                </div>
                <div className="risk-item">
                  <span className="risk-label">Key Concerns:</span>
                  <span className="risk-value">
                    {riskData.retinal_risk > 70 ? 'Retinal' : ''}
                    {riskData.retinal_risk > 70 && riskData.lifestyle_risk > 70 ? ', ' : ''}
                    {riskData.lifestyle_risk > 70 ? 'Lifestyle' : ''}
                    {riskData.retinal_risk <= 70 && riskData.lifestyle_risk <= 70 ? 'Moderate Risk' : ''}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="plans-grid">
            {plans.map((template, idx) => (
              <motion.div
                key={template.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                className={`plan-template-card ${selectedPlan?.id === template.id ? 'selected' : ''} ${template.priority === 'Critical' ? 'critical-priority' : ''}`}
                onClick={() => setSelectedPlan(template)}
              >
                {/* Priority Badge */}
                {template.priority && (
                  <div className={`priority-badge priority-${template.priority.toLowerCase()}`}>
                    {template.priority} Priority
                  </div>
                )}

                <div className="plan-icon-circle" style={{ background: template.color }}>
                  <template.icon size={32} color="white" />
                </div>

                <h3>{template.name}</h3>
                <p className="plan-desc">{template.description}</p>

                {/* What-If Scenarios */}
                {template.whatIfScenarios && (
                  <div className="what-if-scenarios">
                    <strong><TrendingUp size={14} /> What-If Predictions:</strong>
                    <div className="scenarios-timeline">
                      {template.whatIfScenarios.map((scenario, i) => (
                        <div key={i} className="scenario-item">
                          <span className="timeline">{scenario.timeline}:</span>
                          <span className="new-risk" style={{ color: getRiskColor(scenario.newRisk) }}>
                            {scenario.newRisk.toFixed(2)}%
                          </span>
                          <span className={`change ${scenario.change < 0 ? 'negative' : 'neutral'}`}>
                            ({scenario.change > 0 ? '+' : ''}{scenario.change.toFixed(2)}%)
                          </span>
                          <span className="scenario-desc">{scenario.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Personalized Goals */}
                {template.personalizedGoals && (
                  <div className="personalized-goals">
                    <strong>Your Goals:</strong>
                    <ul>
                      {template.personalizedGoals.slice(0, 3).map((goal, i) => (
                        <li key={i}>{goal}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="plan-meta">
                  <div className="meta-item">
                    <span className="meta-label">Duration</span>
                    <span className="meta-value">{template.duration}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Difficulty</span>
                    <span className="meta-value">{template.difficulty}</span>
                  </div>
                </div>

                <div className="expected-outcome">
                  <strong>Expected Impact:</strong> {template.expectedOutcome}
                </div>

                {/* LLM Recommendations */}
                {template.llmRecommendations && template.llmRecommendations.length > 0 && (
                  <div className="llm-recommendations">
                    <strong>AI Recommendations:</strong>
                    {template.llmRecommendations.slice(0, 2).map((rec, i) => (
                      <div key={i} className="rec-item">• {safeString(rec).substring(0, 60)}...</div>
                    ))}
                  </div>
                )}

                {selectedPlan?.id === template.id && (
                  <motion.button
                    initial={{ scale: 0.9 }}
                    animate={{ scale: 1 }}
                    className="select-plan-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSelectPlan(template)
                    }}
                    disabled={loading}
                  >
                    {loading ? 'Creating Plan...' : 'Start This Plan'}
                    <ArrowRight size={18} />
                  </motion.button>
                )}
              </motion.div>
            ))}
          </div>

          <div className="plan-note">
            <p>💡 Each plan includes personalized What-If scenarios showing your predicted risk reduction over time. Choose the plan that best fits your lifestyle and commitment level.</p>
          </div>
        </motion.div>
      </div>
    </>
  )

  function getRiskColor(risk) {
    if (risk < 25) return '#4CAF50'
    if (risk < 50) return '#FF9800'
    if (risk < 75) return '#FF5722'
    return '#F44336'
  }
}

export default PlanSelectionPage