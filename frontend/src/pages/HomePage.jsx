import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Eye, Activity, Brain, ChevronRight, Sparkles } from 'lucide-react'
import { useEffect } from 'react'
import { isAuthenticated } from '../services/auth'
import './HomePage.css'

function HomePage() {
  const navigate = useNavigate()

  // Redirect logged-in users to dashboard
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/dashboard', { replace: true })
    }
  }, [navigate])

  return (
    <div className="homepage">
      {/* Hero Section with Atmospheric Background */}
      <section className="hero">
        <div className="hero-background">
          <div className="medical-scan-lines"></div>
          <div className="floating-particles"></div>
        </div>

        <div className="container hero-content">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
            className="hero-text"
          >
            <div className="hero-badge">
              <Sparkles size={16} />
              <span>AI-Powered Early Detection</span>
            </div>

            <h1 className="hero-title">
              Detect Diabetes
              <span className="gradient-text"> Before It Starts</span>
            </h1>

            <p className="hero-subtitle">
              Multimodal AI framework combining retinal imaging, lifestyle analysis,
              and intelligent simulations for personalized prevention strategies.
            </p>

            <div className="hero-stats">
              <div className="stat">
                <span className="stat-value">&gt;90%</span>
                <span className="stat-label">Detection Accuracy</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat">
                <span className="stat-value">0.85+</span>
                <span className="stat-label">AUC Score</span>
              </div>
              <div className="stat-divider"></div>
              <div className="stat">
                <span className="stat-value">&lt;2s</span>
                <span className="stat-label">Processing Time</span>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="cta-button"
              onClick={() => navigate('/analyze')}
            >
              Begin Analysis
              <ChevronRight size={20} />
            </motion.button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2, ease: [0.4, 0, 0.2, 1] }}
            className="hero-visual"
          >
            <div className="visual-container">
              <div className="retinal-scan-mockup">
                <div className="scan-overlay"></div>
                <div className="scan-grid"></div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <motion.h2
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="section-title"
          >
            Multimodal Detection Framework
          </motion.h2>

          <div className="features-grid">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="feature-card"
            >
              <div className="feature-icon" style={{ background: 'linear-gradient(135deg, #1B6B93 0%, #4A9FBD 100%)' }}>
                <Eye size={28} />
              </div>
              <h3>Retinal Imaging</h3>
              <p>
                Advanced CNN analysis of smartphone retinal images detecting
                diabetic retinopathy with 92-99% sensitivity.
              </p>
              <div className="feature-tech">
                <span className="tech-tag">ResNet CNN</span>
                <span className="tech-tag">Transfer Learning</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="feature-card"
            >
              <div className="feature-icon" style={{ background: 'linear-gradient(135deg, #E85D75 0%, #FF6B6B 100%)' }}>
                <Activity size={28} />
              </div>
              <h3>Lifestyle Analysis</h3>
              <p>
                Gradient Boost model predicting diabetes risk from demographic and
                behavioral data with AUC &gt;0.85.
              </p>
              <div className="feature-tech">
                <span className="tech-tag">Gradient Boost ML</span>
                <span className="tech-tag">NHANES Data</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="feature-card"
            >
              <div className="feature-icon" style={{ background: 'linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)' }}>
                <Brain size={28} />
              </div>
              <h3>AI Simulations</h3>
              <p>
                LLM-powered what-if scenarios demonstrating personalized
                prevention strategies and risk reduction pathways.
              </p>
              <div className="feature-tech">
                <span className="tech-tag">Open AI</span>
                <span className="tech-tag">GPT-OSS-120B</span>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="cta-content glass"
          >
            <h2>Ready to Assess Your Risk?</h2>
            <p>
              Upload a retinal image and complete your lifestyle profile
              for a comprehensive diabetes risk assessment in under 2 seconds.
            </p>
            <button
              className="cta-button secondary"
              onClick={() => navigate('/analyze')}
            >
              Start Free Assessment
              <ChevronRight size={20} />
            </button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p className="text-mono">
            Research Project by L.M. Radith Dinusitha • Informatics Institute of Technology
          </p>
          <p className="footer-note">
            This is an educational risk assessment tool, not a medical diagnostic device.
            Consult healthcare professionals for medical advice.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
