import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Target, CheckCircle, Circle, Calendar, TrendingUp } from 'lucide-react'
import Navigation from '../components/Navigation'
import { getPrimaryPlan, updateProgress, addCheckpoint } from '../services/plans'
import './ProgressPage.css'

function ProgressPage() {
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [newProgress, setNewProgress] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadPlan()
  }, [])

  const loadPlan = async () => {
    try {
      const response = await getPrimaryPlan()
      setPlan(response.plan)
      setNewProgress(response.plan.current_progress || 0)
    } catch (error) {
      console.error('No primary plan found')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateProgress = async () => {
    if (!plan) return

    setUpdating(true)
    try {
      const response = await updateProgress(plan.id, parseFloat(newProgress))
      setPlan(response.plan)

      // Add checkpoint
      await addCheckpoint(plan.id, {
        progress: newProgress,
        note: 'Progress updated'
      })

      alert('Progress updated successfully!')
    } catch (error) {
      console.error('Error updating progress:', error)
      alert('Failed to update progress')
    } finally {
      setUpdating(false)
    }
  }

  if (loading) {
    return (
      <>
        <Navigation />
        <div className="progress-page">
          <div className="loading">Loading plan...</div>
        </div>
      </>
    )
  }

  if (!plan) {
    return (
      <>
        <Navigation />
        <div className="progress-page">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="no-plan-message"
          >
            <Target size={64} color="#ccc" />
            <h2>No Active Plan</h2>
            <p>Start by selecting a health plan from your dashboard</p>
            <button className="cta-button" onClick={() => navigate('/plans')}>
              Choose a Plan
            </button>
          </motion.div>
        </div>
      </>
    )
  }

  const milestones = plan.milestones || []
  const completedMilestones = milestones.filter(m => plan.current_progress >= m.target)

  return (
    <>
      <Navigation />
      <div className="progress-page">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="progress-content"
        >
          {/* Plan Header */}
          <div className="plan-header-card">
            <div className="plan-title-section">
              <h1>{plan.plan_name}</h1>
              <p>{plan.description}</p>
            </div>

            <div className="progress-circle">
              <svg width="160" height="160">
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  fill="none"
                  stroke="#f0f0f0"
                  strokeWidth="12"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  fill="none"
                  stroke="#667eea"
                  strokeWidth="12"
                  strokeDasharray={`${2 * Math.PI * 70}`}
                  strokeDashoffset={`${2 * Math.PI * 70 * (1 - plan.current_progress / 100)}`}
                  transform="rotate(-90 80 80)"
                  style={{ transition: 'stroke-dashoffset 0.6s ease' }}
                />
                <text
                  x="80"
                  y="75"
                  textAnchor="middle"
                  fontSize="32"
                  fontWeight="700"
                  fill="#667eea"
                >
                  {plan.current_progress}%
                </text>
                <text
                  x="80"
                  y="95"
                  textAnchor="middle"
                  fontSize="14"
                  fill="#999"
                >
                  Complete
                </text>
              </svg>
            </div>
          </div>

          <div className="progress-grid">
            {/* Milestones Card */}
            <div className="milestones-card">
              <h2>Milestones</h2>
              <div className="milestones-list">
                {milestones.map((milestone, idx) => {
                  const isCompleted = plan.current_progress >= milestone.target
                  return (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className={`milestone-item ${isCompleted ? 'completed' : ''}`}
                    >
                      {isCompleted ? (
                        <CheckCircle size={24} color="#4CAF50" />
                      ) : (
                        <Circle size={24} color="#ccc" />
                      )}
                      <div className="milestone-content">
                        <h4>{milestone.name}</h4>
                        <span>{milestone.target}% progress needed</span>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>

            {/* Update Progress Card */}
            <div className="update-progress-card">
              <h2>Update Your Progress</h2>
              <p>How far along are you with your plan?</p>

              <div className="progress-input-group">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={newProgress}
                  onChange={(e) => setNewProgress(e.target.value)}
                  placeholder="Enter progress %"
                />
                <button
                  className="update-btn"
                  onClick={handleUpdateProgress}
                  disabled={updating}
                >
                  {updating ? 'Updating...' : 'Update Progress'}
                </button>
              </div>

              <div className="stats-row">
                <div className="stat">
                  <Calendar size={20} />
                  <span>Started: {new Date(plan.start_date).toLocaleDateString()}</span>
                </div>
                <div className="stat">
                  <TrendingUp size={20} />
                  <span>{completedMilestones.length}/{milestones.length} milestones</span>
                </div>
              </div>
            </div>
          </div>

          {/* Expected Outcomes */}
          {plan.expected_outcomes && (
            <div className="outcomes-card">
              <h2>Expected Outcomes</h2>
              <div className="outcome-content">
                <p>{plan.expected_outcomes.risk_reduction}</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </>
  )
}

export default ProgressPage
