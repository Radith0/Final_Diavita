import { motion } from 'framer-motion'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  Activity, Eye, Brain, TrendingUp, BarChart3,
  ArrowLeft, Code, Layers, Home, Zap, AlertCircle
} from 'lucide-react'
import './AdvancedMetricsPage.css'

function AdvancedMetricsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const results = location.state?.results

  if (!results) {
    return (
      <div className="error-state">
        <h2>No Analysis Data</h2>
        <p>Please complete an analysis first</p>
        <button onClick={() => navigate('/analyze')}>Go to Analysis</button>
      </div>
    )
  }

  const { risk_assessment, metadata } = results
  const retinalAnalysis = risk_assessment.retinal_analysis
  const lifestyleAnalysis = risk_assessment.lifestyle_analysis

  return (
    <div className="advanced-metrics-page">
      <div className="container">
        {/* Page Navigation */}
        <div className="page-nav">
          <button className="nav-back-btn" onClick={() => navigate('/results', { state: { results } })}>
            <ArrowLeft size={18} />
            Back to Results
          </button>
          <button className="nav-home-btn" onClick={() => navigate('/')}>
            <Home size={18} />
            Home
          </button>
        </div>

        {/* Header */}
        <div className="page-header">
          <h1>
            <Code size={32} />
            Advanced ML Metrics
          </h1>
          <p className="page-subtitle">Technical Analysis for Data Scientists & ML Engineers</p>
        </div>

        {/* Model Status Banner */}
        {(retinalAnalysis.dr_detected === null || lifestyleAnalysis.risk_score === 0) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="info-banner"
          >
            <AlertCircle size={20} />
            <div>
              <strong>Models Currently Not Loaded</strong>
              <p>
                The training metrics below are from model development. To get real-time predictions,
                re-export models with current sklearn 1.8.0 version. See backend logs for details.
              </p>
            </div>
          </motion.div>
        )}

        {/* Model Architecture Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="section glass"
        >
          <h2>
            <Layers size={24} />
            Model Architecture
          </h2>

          <div className="architecture-grid">
            {/* Retinal Model */}
            <div className="model-card">
              <h3>Retinal Image Model</h3>
              <div className="model-details">
                <div className="detail-row">
                  <span className="label">Architecture:</span>
                  <code>ResNet50 + Custom Attention</code>
                </div>
                <div className="detail-row">
                  <span className="label">Input Size:</span>
                  <code>[512, 512, 3]</code>
                </div>
                <div className="detail-row">
                  <span className="label">Output Classes:</span>
                  <code>5 (DR severity 0-4)</code>
                </div>
                <div className="detail-row">
                  <span className="label">Framework:</span>
                  <code>TensorFlow/Keras</code>
                </div>
                <div className="detail-row">
                  <span className="label">Model Version:</span>
                  <code>{metadata?.model_versions?.retinal || '1.0.0'}</code>
                </div>
                <div className="detail-row">
                  <span className="label">Status:</span>
                  <code className={retinalAnalysis.dr_detected !== null ? 'status-loaded' : 'status-not-loaded'}>
                    {retinalAnalysis.dr_detected !== null ? '🟢 Loaded' : '🔴 Not Loaded'}
                  </code>
                </div>
              </div>
            </div>

            {/* Lifestyle Model */}
            <div className="model-card">
              <h3>Lifestyle Risk Model</h3>
              <div className="model-details">
                <div className="detail-row">
                  <span className="label">Algorithm:</span>
                  <code>Gradient Boosting Classifier</code>
                </div>
                <div className="detail-row">
                  <span className="label">Features:</span>
                  <code>16 (demographic + clinical)</code>
                </div>
                <div className="detail-row">
                  <span className="label">Output:</span>
                  <code>Binary (diabetes risk)</code>
                </div>
                <div className="detail-row">
                  <span className="label">Framework:</span>
                  <code>scikit-learn 1.8.0</code>
                </div>
                <div className="detail-row">
                  <span className="label">Model Version:</span>
                  <code>{metadata?.model_versions?.lifestyle || '1.0.0'}</code>
                </div>
                <div className="detail-row">
                  <span className="label">Status:</span>
                  <code className={lifestyleAnalysis.risk_score > 0 ? 'status-loaded' : 'status-not-loaded'}>
                    {lifestyleAnalysis.risk_score > 0 ? '🟢 Loaded' : '🔴 Not Loaded'}
                  </code>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Model Performance Metrics - Training Results */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="section glass"
        >
          <h2>
            <BarChart3 size={24} />
            Model Performance (Training Results)
          </h2>

          <div className="metrics-grid">
            {/* Retinal Model Metrics */}
            <div className="metrics-card">
              <h3>Retinal CNN Model</h3>
              <div className="metrics-table">
                <div className="metric-row header">
                  <span>Metric</span>
                  <span>Value</span>
                </div>
                <div className="metric-row">
                  <span>Test Accuracy</span>
                  <code>~78.45%</code>
                </div>
                <div className="metric-row">
                  <span>Dataset</span>
                  <code>EyePACS (~35k images)</code>
                </div>
                <div className="metric-row">
                  <span>Output Classes</span>
                  <code>5 severity levels</code>
                </div>
              </div>
            </div>

            {/* Lifestyle Model Metrics */}
            <div className="metrics-card">
              <h3>Lifestyle Gradient Boosting</h3>
              <div className="metrics-table">
                <div className="metric-row header">
                  <span>Metric</span>
                  <span>Value</span>
                </div>
                <div className="metric-row">
                  <span>Accuracy</span>
                  <code>94.35%</code>
                </div>
                <div className="metric-row">
                  <span>F1-Score</span>
                  <code>0.9045</code>
                </div>
                <div className="metric-row">
                  <span>Precision</span>
                  <code>95.58%</code>
                </div>
                <div className="metric-row">
                  <span>Recall</span>
                  <code>85.84%</code>
                </div>
                <div className="metric-row">
                  <span>Dataset</span>
                  <code>NHANES (~15k samples)</code>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Current Prediction Details - Only show if models are loaded */}
        {(retinalAnalysis.dr_detected !== null || lifestyleAnalysis.risk_score > 0) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="section glass"
          >
            <h2>
              <Brain size={24} />
              Current Prediction Analysis
            </h2>

            <div className="prediction-details-grid">
              {/* Retinal Prediction */}
              {retinalAnalysis.dr_detected !== null && (
                <div className="prediction-card">
                  <h3>
                    <Eye size={20} />
                    Retinal Model Output
                  </h3>
                  <div className="prediction-data">
                    <div className="data-row">
                      <span className="data-label">DR Probability:</span>
                      <code className="data-value">
                        {(retinalAnalysis.confidence * 100).toFixed(2)}%
                      </code>
                    </div>
                    <div className="data-row">
                      <span className="data-label">Predicted Class:</span>
                      <code className="data-value">{retinalAnalysis.severity}</code>
                    </div>
                    <div className="data-row">
                      <span className="data-label">Confidence Score:</span>
                      <code className="data-value">
                        {(retinalAnalysis.confidence * 100).toFixed(2)}%
                      </code>
                    </div>
                    {retinalAnalysis.findings && (
                      <div className="features-detected">
                        <span className="data-label">Detected Features:</span>
                        <div className="features-list">
                          {Object.entries(retinalAnalysis.findings)
                            .filter(([key, value]) => value === true && key !== 'total_features_detected')
                            .map(([key]) => (
                              <span key={key} className="feature-badge">{key}</span>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Lifestyle Prediction */}
              {lifestyleAnalysis.risk_score > 0 && (
                <div className="prediction-card">
                  <h3>
                    <Activity size={20} />
                    Lifestyle Model Output
                  </h3>
                  <div className="prediction-data">
                    <div className="data-row">
                      <span className="data-label">Risk Probability:</span>
                      <code className="data-value">
                        {(lifestyleAnalysis.risk_score * 100).toFixed(2)}%
                      </code>
                    </div>
                    <div className="data-row">
                      <span className="data-label">Confidence:</span>
                      <code className="data-value">
                        {(lifestyleAnalysis.confidence * 100).toFixed(2)}%
                      </code>
                    </div>
                    <div className="data-row">
                      <span className="data-label">Classification:</span>
                      <code className="data-value">
                        {lifestyleAnalysis.risk_score > 0.5 ? 'Positive' : 'Negative'}
                      </code>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}


        {/* Back Button */}
        <div className="actions-footer">
          <button className="btn-primary" onClick={() => navigate('/results', { state: { results } })}>
            <ArrowLeft size={20} />
            Back to Results
          </button>
        </div>
      </div>
    </div>
  )
}

export default AdvancedMetricsPage
