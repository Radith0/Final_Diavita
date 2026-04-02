import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate, useLocation } from 'react-router-dom'
import { Eye, TrendingUp, Calendar, Target, AlertCircle, Activity, ArrowRight, CheckCircle, Sparkles, TrendingDown } from 'lucide-react'
import Navigation from '../components/Navigation'
import { getMyResults, getResultsSummary } from '../services/results'
import { getPrimaryPlan } from '../services/plans'
import './ResultsPage.css'

function ResultsPage() {
  const [results, setResults] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedResult, setSelectedResult] = useState(null)
  const [currentResult, setCurrentResult] = useState(null)
  const [hasPlan, setHasPlan] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  // Check if coming from fresh analysis
  const justCompleted = location.state?.justCompleted
  const passedResults = location.state?.results

  useEffect(() => {
    loadResults()
  }, [])

  const loadResults = async () => {
    try {
      // If coming from analysis with fresh results, use those
      if (passedResults) {
        setCurrentResult(passedResults)
      }

      // Also load historical results from database
      const [resultsData, summaryData, planCheck] = await Promise.allSettled([
        getMyResults(1, 20),
        getResultsSummary(),
        getPrimaryPlan()
      ])

      if (resultsData.status === 'fulfilled') {
        setResults(resultsData.value.results || [])
        // If no current result, use latest from database
        if (!passedResults && resultsData.value.results?.length > 0) {
          setSelectedResult(resultsData.value.results[0])
        }
      }

      if (summaryData.status === 'fulfilled') {
        setSummary(summaryData.value)
      }

      if (planCheck.status === 'fulfilled') {
        setHasPlan(true)
      }

    } catch (error) {
      console.error('Error loading results:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (risk) => {
    if (risk < 25) return '#4CAF50'
    if (risk < 50) return '#FF9800'
    if (risk < 75) return '#FF5722'
    return '#F44336'
  }

  const getRiskLabel = (category) => {
    const labels = {
      low: 'Low Risk',
      moderate: 'Moderate Risk',
      high: 'High Risk',
      very_high: 'Very High Risk'
    }
    return labels[category] || 'Unknown'
  }

  if (loading) {
    return (
      <>
        <Navigation />
        <div className="results-page">
          <div className="loading">
            <TrendingUp className="loading-icon" />
            <p>Loading your results...</p>
          </div>
        </div>
      </>
    )
  }

  // Use fresh results if available, otherwise use database results
  const displayResult = currentResult || selectedResult

  if (!displayResult && results.length === 0 && !loading) {
    return (
      <>
        <Navigation />
        <div className="results-page">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="no-results-state"
          >
            <AlertCircle size={64} color="#999" />
            <h2>No Analysis Results Yet</h2>
            <p>Complete your first health assessment to see results here</p>
            <button className="cta-button" onClick={() => navigate('/analyze')}>
              Start Analysis
            </button>
          </motion.div>
        </div>
      </>
    )
  }

  // Extract data from either fresh or saved results
  const getRiskData = () => {
    // Helper to convert to percentage if needed (handles both 0-1 and 0-100 scales)
    const toPercentage = (value) => {
      if (!value && value !== 0) return 0
      return value <= 1 ? value * 100 : value
    }

    if (currentResult) {
      // Fresh from analysis - extract from nested structure
      const riskAssessment = currentResult.risk_assessment || {}
      const overallRisk = riskAssessment.overall_risk_score || currentResult.final_risk || currentResult.risk_score || 0
      const retinalRisk = riskAssessment.retinal_analysis?.risk_score || 0
      const lifestyleRisk = riskAssessment.lifestyle_analysis?.risk_score || 0

      return {
        combined_risk: toPercentage(overallRisk),
        retinal_risk: toPercentage(retinalRisk),
        lifestyle_risk: toPercentage(lifestyleRisk),
        recommendations: currentResult.personalized_advice?.recommendations || currentResult.recommendations || [],
        risk_assessment: riskAssessment,
        risk_category: riskAssessment.risk_level || 'unknown'
      }
    } else if (displayResult) {
      // From database - values are already in percentage format
      return {
        combined_risk: displayResult.combined_risk || 0,
        retinal_risk: displayResult.retinal_risk || 0,
        lifestyle_risk: displayResult.lifestyle_risk || 0,
        recommendations: displayResult.recommendations || [],
        risk_category: displayResult.risk_category
      }
    }
    return {}
  }

  const riskData = getRiskData()

  return (
    <>
      <Navigation />
      <div className="results-page">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="results-content"
        >
          {/* Success Banner for Fresh Analysis */}
          {justCompleted && (
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="completion-banner"
            >
              <CheckCircle size={32} />
              <div>
                <h3>Analysis Complete!</h3>
                <p>Your results have been saved and analyzed</p>
              </div>
            </motion.div>
          )}

          {/* Header with Summary */}
          <div className="results-header">
            <div className="header-text">
              <h1>{justCompleted ? 'Your Results' : 'Analysis History'}</h1>
              <p>{justCompleted ? 'Review your diabetes risk assessment' : `${results.length} total ${results.length === 1 ? 'analysis' : 'analyses'} completed`}</p>
            </div>

            {summary?.risk_trend && !justCompleted && (
              <div className="trend-badge" style={{
                backgroundColor: summary.risk_trend === 'improving' ? '#e8f5e9' : summary.risk_trend === 'worsening' ? '#ffebee' : '#f5f5f5',
                color: summary.risk_trend === 'improving' ? '#2e7d32' : summary.risk_trend === 'worsening' ? '#c62828' : '#666'
              }}>
                {summary.risk_trend === 'improving' ? '📈 Risk Improving' :
                 summary.risk_trend === 'worsening' ? '📉 Risk Increasing' :
                 '➡️ Risk Stable'}
              </div>
            )}
          </div>

          <div className="results-layout">
            {/* Results List */}
            <div className="results-list">
              <h3>Analysis History</h3>
              {results.map((result, idx) => (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`result-item ${selectedResult?.id === result.id ? 'selected' : ''}`}
                  onClick={() => setSelectedResult(result)}
                >
                  <div className="result-date">
                    <Calendar size={16} />
                    {new Date(result.analysis_date).toLocaleDateString()}
                  </div>
                  <div className="result-score" style={{ color: getRiskColor(result.combined_risk) }}>
                    {result.combined_risk?.toFixed(1)}%
                  </div>
                  <div className="result-category" style={{
                    backgroundColor: `${getRiskColor(result.combined_risk)}20`,
                    color: getRiskColor(result.combined_risk)
                  }}>
                    {getRiskLabel(result.risk_category)}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Main Result Display */}
            {displayResult && (
              <div className="result-detail">
                {/* Risk Score Display */}
                <div className="risk-visualization">
                  <svg className="progress-ring" width="280" height="280" viewBox="0 0 280 280">
                    <circle
                      cx="140"
                      cy="140"
                      r="110"
                      fill="none"
                      stroke="#f0f0f0"
                      strokeWidth="18"
                    />
                    <circle
                      cx="140"
                      cy="140"
                      r="110"
                      fill="none"
                      stroke={getRiskColor(riskData.combined_risk)}
                      strokeWidth="18"
                      strokeDasharray={`${2 * Math.PI * 110}`}
                      strokeDashoffset={`${2 * Math.PI * 110 * (1 - riskData.combined_risk / 100)}`}
                      transform="rotate(-90 140 140)"
                      style={{ transition: 'stroke-dashoffset 0.8s ease' }}
                    />
                    <text x="140" y="150" textAnchor="middle" fontSize="48" fontWeight="700" fill={getRiskColor(riskData.combined_risk)}>
                      {riskData.combined_risk?.toFixed(0)}%
                    </text>
                    <text x="140" y="175" textAnchor="middle" fontSize="16" fill="#999">
                      Risk Score
                    </text>
                  </svg>

                  <div className="risk-breakdown">
                    <div className="risk-component">
                      <Eye size={20} />
                      <div>
                        <span className="component-label">Retinal Analysis</span>
                        <span className="component-value">{riskData.retinal_risk?.toFixed(1)}%</span>
                      </div>
                    </div>
                    <div className="risk-component">
                      <Activity size={20} />
                      <div>
                        <span className="component-label">Lifestyle Assessment</span>
                        <span className="component-value">{riskData.lifestyle_risk?.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recommendations */}
                {riskData.recommendations && riskData.recommendations.length > 0 && (
                  <div className="recommendations-section">
                    <h4>Personalized Recommendations</h4>
                    <div className="recommendations-list">
                      {riskData.recommendations.slice(0, 5).map((rec, idx) => (
                        <div key={idx} className="recommendation-item">
                          <span className="rec-bullet">•</span>
                          <p>{rec}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Next Steps - Prominent CTA */}
                <div className="next-steps-section">
                  <h3>What's Next?</h3>
                  <p>Now that you have your results, it's time to take action</p>

                  {!hasPlan && justCompleted ? (
                    <button className="continue-btn primary-cta" onClick={() => navigate('/plans', {
                      state: {
                        analysisResults: currentResult,
                        riskData: riskData,
                        justCompleted: true
                      }
                    })}>
                      Choose Your Health Plan
                      <ArrowRight size={20} />
                    </button>
                  ) : (
                    <div className="action-buttons">
                      <button className="action-btn primary" onClick={() => navigate('/plans')}>
                        <Target size={18} />
                        View Health Plans
                      </button>
                      <button className="action-btn" onClick={() => navigate('/simulations')}>
                        <Sparkles size={18} />
                        What-If Scenarios
                      </button>
                      <button className="action-btn" onClick={() => navigate('/dashboard')}>
                        <Activity size={18} />
                        Go to Dashboard
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </>
  )
}

export default ResultsPage
