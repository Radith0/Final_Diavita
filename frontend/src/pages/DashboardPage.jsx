import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp, TrendingDown, Activity, Target, ArrowRight, AlertCircle,
  Heart, Droplets, Brain, Eye, Zap, Moon, Scale, Clock,
  ChevronRight, Sparkles, Shield, BarChart3, User, Download, FileText
} from 'lucide-react'
import jsPDF from 'jspdf'
import Navigation from '../components/Navigation'
import { getStoredUser } from '../services/auth'
import { getLatestResult, getResultsSummary } from '../services/results'
import { getPrimaryPlan } from '../services/plans'
import './DashboardPage.css'

function DashboardPage() {
  const [user, setUser] = useState(null)
  const [latestResult, setLatestResult] = useState(null)
  const [summary, setSummary] = useState(null)
  const [primaryPlan, setPrimaryPlan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeMetric, setActiveMetric] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const storedUser = getStoredUser()
        if (!storedUser) {
          navigate('/login')
          return
        }
        setUser(storedUser)

        // Load latest result, summary, and primary plan
        const [resultData, summaryData, planData] = await Promise.allSettled([
          getLatestResult(),
          getResultsSummary(),
          getPrimaryPlan()
        ])

        if (resultData.status === 'fulfilled') {
          setLatestResult(resultData.value.result)
        }

        if (summaryData.status === 'fulfilled') {
          setSummary(summaryData.value)
        }

        if (planData.status === 'fulfilled') {
          setPrimaryPlan(planData.value.plan)
        }

      } catch (error) {
        console.error('Error loading dashboard:', error)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [navigate])

  const getRiskGradient = (risk) => {
    if (risk < 25) return 'linear-gradient(135deg, #00F5A0 0%, #00D9FF 100%)'
    if (risk < 50) return 'linear-gradient(135deg, #FFD200 0%, #F7971E 100%)'
    if (risk < 75) return 'linear-gradient(135deg, #FF6B9D 0%, #FEC064 100%)'
    return 'linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%)'
  }

  const getRiskLabel = (category) => {
    const labels = {
      low: 'Optimal Health',
      moderate: 'Moderate Caution',
      high: 'Elevated Risk',
      very_high: 'Critical Alert'
    }
    return labels[category] || 'Analyzing...'
  }

  // Generate comprehensive report content using analysis data
  const generateReportContent = () => {
    const riskScore = latestResult.combined_risk || 0
    const riskCategory = latestResult.risk_category || 'moderate'

    // Generate personalized insights based on risk level
    const getPersonalizedInsights = () => {
      const insights = []

      if (riskScore < 25) {
        insights.push("Your current health metrics indicate a low risk for diabetes. This is excellent news!")
        insights.push("Continue maintaining your healthy lifestyle habits to keep your risk low.")
        insights.push("Regular monitoring and preventive care will help you stay on track.")
      } else if (riskScore < 50) {
        insights.push("Your assessment shows moderate risk factors for diabetes that warrant attention.")
        insights.push("Early intervention at this stage can significantly reduce your risk progression.")
        insights.push("Focus on lifestyle modifications and regular monitoring of key health metrics.")
      } else if (riskScore < 75) {
        insights.push("Your risk assessment indicates elevated concern for diabetes development.")
        insights.push("Immediate lifestyle changes and medical consultation are strongly recommended.")
        insights.push("With proper intervention, you can still prevent or delay diabetes onset.")
      } else {
        insights.push("Your assessment shows critical risk factors requiring immediate medical attention.")
        insights.push("Consult with a healthcare provider as soon as possible for comprehensive evaluation.")
        insights.push("Aggressive intervention strategies may be necessary to manage your risk.")
      }

      // Add specific insights based on retinal vs lifestyle risk
      if (latestResult.retinal_risk > latestResult.lifestyle_risk) {
        insights.push("Retinal analysis shows concerning patterns. Regular eye examinations are crucial.")
      } else if (latestResult.lifestyle_risk > latestResult.retinal_risk) {
        insights.push("Lifestyle factors are your primary risk drivers. Focus on diet, exercise, and weight management.")
      }

      return insights
    }

    // Generate actionable recommendations
    const getDetailedRecommendations = () => {
      const recs = []

      // Diet recommendations
      recs.push({
        category: "Dietary Changes",
        items: [
          "Reduce sugar and refined carbohydrate intake",
          "Increase fiber consumption through whole grains and vegetables",
          "Control portion sizes and meal timing",
          "Stay hydrated with water instead of sugary drinks"
        ]
      })

      // Exercise recommendations
      if (healthMetrics?.lifestyle?.find(m => m.label === "Activity")?.value < 150) {
        recs.push({
          category: "Physical Activity",
          items: [
            "Aim for at least 150 minutes of moderate exercise per week",
            "Include both aerobic and resistance training",
            "Start with 10-minute walks after meals",
            "Gradually increase intensity and duration"
          ]
        })
      }

      // Medical follow-up
      recs.push({
        category: "Medical Follow-up",
        items: [
          riskScore > 50 ? "Schedule immediate consultation with healthcare provider" : "Annual diabetes screening recommended",
          "Monitor blood pressure and cholesterol regularly",
          "Consider HbA1c testing every 3-6 months",
          "Maintain regular eye examinations"
        ]
      })

      return recs
    }

    return {
      insights: getPersonalizedInsights(),
      recommendations: getDetailedRecommendations(),
      riskInterpretation: getRiskInterpretation(riskScore),
      nextSteps: getNextSteps(riskCategory)
    }
  }

  // Get risk interpretation text
  const getRiskInterpretation = (score) => {
    if (score < 25) return "Your risk level is optimal. You're doing great!"
    if (score < 50) return "Moderate risk detected. Preventive action recommended."
    if (score < 75) return "Elevated risk identified. Immediate lifestyle changes needed."
    return "Critical risk level. Urgent medical consultation required."
  }

  // Get next steps based on risk category
  const getNextSteps = (category) => {
    const steps = {
      low: [
        "Continue current healthy lifestyle",
        "Annual health check-ups",
        "Maintain awareness of risk factors"
      ],
      moderate: [
        "Implement lifestyle modifications",
        "Schedule doctor consultation within 3 months",
        "Begin regular glucose monitoring"
      ],
      high: [
        "Urgent medical consultation needed",
        "Start intensive lifestyle intervention",
        "Consider medication if recommended by doctor"
      ],
      very_high: [
        "Immediate medical attention required",
        "Comprehensive diabetes evaluation",
        "Begin treatment protocol as advised"
      ]
    }
    return steps[category] || steps.moderate
  }

  // Generate PDF report using backend LLM
  const downloadPDF = async () => {
    if (!latestResult) {
      alert('No analysis results available')
      return
    }

    try {
      // Get the latest result ID
      const resultId = latestResult.id

      if (!resultId) {
        alert('Unable to identify result ID')
        return
      }

      // Call backend to generate LLM-powered PDF
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:5001/api/reports/generate-pdf/${resultId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to generate PDF report')
      }

      // Download the PDF
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `DIAVITA-Health-Report-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

    } catch (error) {
      console.error('PDF generation failed:', error)
      alert('Failed to generate PDF report. Please try again.')
    }
  }

  // Keep old client-side PDF as fallback (commented out)
  const downloadPDFClientSide = async () => {
    if (!latestResult) return

    const reportContent = generateReportContent()
    const riskScore = latestResult.combined_risk || 0

    // Create a new jsPDF instance
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const margin = 20
    const contentWidth = pageWidth - 2 * margin
    let yPos = margin

    // Helper function to add text with wrapping
    const addText = (text, fontSize, isBold = false, color = [0, 0, 0]) => {
      pdf.setFontSize(fontSize)
      pdf.setFont('helvetica', isBold ? 'bold' : 'normal')
      pdf.setTextColor(...color)
      const lines = pdf.splitTextToSize(text, contentWidth)

      lines.forEach(line => {
        if (yPos > pageHeight - margin - 10) {
          pdf.addPage()
          yPos = margin
        }
        pdf.text(line, margin, yPos)
        yPos += fontSize * 0.5
      })
      yPos += 3
    }

    // Helper to add a section divider
    const addDivider = () => {
      pdf.setDrawColor(200, 200, 200)
      pdf.line(margin, yPos, pageWidth - margin, yPos)
      yPos += 8
    }

    // Header
    pdf.setFillColor(102, 126, 234)
    pdf.rect(0, 0, pageWidth, 40, 'F')
    pdf.setTextColor(255, 255, 255)
    pdf.setFontSize(24)
    pdf.setFont('helvetica', 'bold')
    pdf.text('DIAVITA', pageWidth / 2, 20, { align: 'center' })
    pdf.setFontSize(12)
    pdf.text('Diabetes Risk Assessment Report', pageWidth / 2, 30, { align: 'center' })

    yPos = 50

    // Patient Info
    pdf.setTextColor(0, 0, 0)
    addText(`Patient: ${user?.username || 'Anonymous'}`, 10, false, [100, 100, 100])
    addText(`Generated on: ${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`, 10, false, [100, 100, 100])
    addText(`Report ID: ${Date.now()}`, 10, false, [100, 100, 100])
    yPos += 5
    addDivider()

    // Executive Summary
    addText('EXECUTIVE SUMMARY', 16, true, [102, 126, 234])

    // Risk Score Box
    const riskColor = riskScore < 50 ? [0, 217, 255] : riskScore < 75 ? [247, 151, 30] : [255, 65, 108]
    pdf.setFillColor(...riskColor)
    pdf.roundedRect(margin, yPos, contentWidth, 30, 3, 3, 'F')
    pdf.setTextColor(255, 255, 255)
    pdf.setFontSize(32)
    pdf.setFont('helvetica', 'bold')
    pdf.text(`${riskScore.toFixed(0)}%`, pageWidth / 2, yPos + 15, { align: 'center' })
    pdf.setFontSize(12)
    pdf.text(getRiskLabel(latestResult.risk_category), pageWidth / 2, yPos + 25, { align: 'center' })
    yPos += 35

    pdf.setTextColor(0, 0, 0)
    addText(reportContent.riskInterpretation, 11, true)
    yPos += 5
    addDivider()

    // Risk Assessment Breakdown
    addText('RISK ASSESSMENT BREAKDOWN', 14, true, [102, 126, 234])
    addText(`Overall Diabetes Risk: ${riskScore.toFixed(1)}%`, 11, true)
    addText(`Retinal Analysis Risk: ${(latestResult.retinal_risk || 0).toFixed(1)}%`, 10)
    addText(`Lifestyle Factors Risk: ${(latestResult.lifestyle_risk || 0).toFixed(1)}%`, 10)
    addText(`Confidence Score: ${((latestResult.confidence_score || 0.85) * 100).toFixed(0)}%`, 10)
    yPos += 3
    addDivider()

    // Health Metrics
    if (healthMetrics) {
      addText('HEALTH METRICS ANALYSIS', 14, true, [102, 126, 234])
      addText('Vital Signs:', 12, true)
      healthMetrics.vitals.forEach(metric => {
        addText(`${metric.label}: ${metric.value} ${metric.unit || ''}`, 10)
      })

      if (healthMetrics.lifestyle) {
        yPos += 3
        addText('Lifestyle Factors:', 12, true)
        healthMetrics.lifestyle.forEach(metric => {
          addText(`${metric.label}: ${metric.value} ${metric.unit || ''}`, 10)
        })
      }
      yPos += 3
      addDivider()
    }

    // Personalized Insights
    if (yPos > pageHeight - margin - 50) {
      pdf.addPage()
      yPos = margin
    }
    addText('PERSONALIZED HEALTH INSIGHTS', 14, true, [102, 126, 234])
    reportContent.insights.forEach(insight => {
      pdf.setFillColor(240, 244, 255)
      const textLines = pdf.splitTextToSize(insight, contentWidth - 10)
      const boxHeight = textLines.length * 5 + 6

      if (yPos + boxHeight > pageHeight - margin - 10) {
        pdf.addPage()
        yPos = margin
      }

      pdf.roundedRect(margin, yPos, contentWidth, boxHeight, 2, 2, 'F')
      pdf.setDrawColor(102, 126, 234)
      pdf.setLineWidth(1)
      pdf.line(margin, yPos, margin, yPos + boxHeight)

      yPos += 5
      textLines.forEach(line => {
        pdf.setTextColor(0, 0, 0)
        pdf.setFontSize(10)
        pdf.text(line, margin + 5, yPos)
        yPos += 5
      })
      yPos += 3
    })
    addDivider()

    // Detailed Recommendations
    if (yPos > pageHeight - margin - 50) {
      pdf.addPage()
      yPos = margin
    }
    addText('DETAILED RECOMMENDATIONS', 14, true, [102, 126, 234])
    reportContent.recommendations.forEach(rec => {
      if (yPos > pageHeight - margin - 40) {
        pdf.addPage()
        yPos = margin
      }
      addText(rec.category, 12, true)
      rec.items.forEach(item => {
        addText(`• ${item}`, 10)
      })
      yPos += 3
    })
    addDivider()

    // Next Steps
    if (yPos > pageHeight - margin - 50) {
      pdf.addPage()
      yPos = margin
    }
    addText('IMMEDIATE NEXT STEPS', 14, true, [102, 126, 234])
    pdf.setFillColor(255, 248, 225)
    const nextStepsHeight = reportContent.nextSteps.length * 8 + 10

    if (yPos + nextStepsHeight > pageHeight - margin - 10) {
      pdf.addPage()
      yPos = margin
    }

    pdf.roundedRect(margin, yPos, contentWidth, nextStepsHeight, 2, 2, 'F')
    yPos += 5
    reportContent.nextSteps.forEach(step => {
      addText(`✓ ${step}`, 10, true)
    })
    yPos += 5
    addDivider()

    // Risk Factor Analysis
    if (yPos > pageHeight - margin - 60) {
      pdf.addPage()
      yPos = margin
    }
    addText('RISK FACTOR ANALYSIS', 14, true, [102, 126, 234])

    const riskFactors = []
    if (healthMetrics) {
      healthMetrics.vitals.forEach(metric => {
        if (metric.label === 'Blood Pressure' && metric.value !== '120/80') {
          riskFactors.push(`Blood Pressure: ${metric.value} - Monitor closely`)
        }
        if (metric.label === 'Glucose' && parseFloat(metric.value) > 100) {
          riskFactors.push(`Blood Glucose: ${metric.value} ${metric.unit} - Above normal range`)
        }
        if (metric.label === 'BMI' && parseFloat(metric.value) >= 25) {
          riskFactors.push(`BMI: ${metric.value} - Weight management recommended`)
        }
        if (metric.label === 'HbA1c' && parseFloat(metric.value) >= 5.7) {
          riskFactors.push(`HbA1c: ${metric.value}% - Pre-diabetic range detected`)
        }
      })

      if (healthMetrics.lifestyle) {
        healthMetrics.lifestyle.forEach(metric => {
          if (metric.label === 'Exercise' && parseFloat(metric.value) < 150) {
            riskFactors.push(`Physical Activity: ${metric.value} ${metric.unit} - Below recommended 150 min/week`)
          }
          if (metric.label === 'Sleep' && (parseFloat(metric.value) < 7 || parseFloat(metric.value) > 9)) {
            riskFactors.push(`Sleep: ${metric.value} ${metric.unit} - Suboptimal sleep duration`)
          }
          if (metric.label === 'Retinal' && metric.value === 'Alert') {
            riskFactors.push(`Retinal Health: Alert - Eye examination recommended`)
          }
        })
      }
    }

    if (riskFactors.length > 0) {
      riskFactors.forEach(factor => {
        addText(`• ${factor}`, 10)
      })
    } else {
      addText('No significant risk factors identified. Maintain current health practices.', 10)
    }
    yPos += 3
    addDivider()

    // Timeline & Prognosis
    if (yPos > pageHeight - margin - 60) {
      pdf.addPage()
      yPos = margin
    }
    addText('RISK PROGRESSION TIMELINE', 14, true, [102, 126, 234])
    addText('Projected risk if no intervention:', 11, true)
    addText(`• 6 months: ${Math.min(100, riskScore + 5).toFixed(1)}% (↑ +5%)`, 10, false, [255, 87, 34])
    addText(`• 12 months: ${Math.min(100, riskScore + 12).toFixed(1)}% (↑ +12%)`, 10, false, [255, 87, 34])
    addText(`• 24 months: ${Math.min(100, riskScore + 20).toFixed(1)}% (↑ +20%)`, 10, false, [255, 87, 34])

    yPos += 5
    addText('Projected risk with lifestyle intervention:', 11, true)
    addText(`• 3 months: ${Math.max(0, riskScore - 8).toFixed(1)}% (↓ -8%)`, 10, false, [76, 175, 80])
    addText(`• 6 months: ${Math.max(0, riskScore - 18).toFixed(1)}% (↓ -18%)`, 10, false, [76, 175, 80])
    addText(`• 12 months: ${Math.max(0, riskScore - 30).toFixed(1)}% (↓ -30%)`, 10, false, [76, 175, 80])
    yPos += 5
    addDivider()

    // Understanding Your Results
    if (yPos > pageHeight - margin - 60) {
      pdf.addPage()
      yPos = margin
    }
    addText('UNDERSTANDING YOUR RESULTS', 14, true, [102, 126, 234])
    addText('This assessment combines:', 11, true)
    addText('• Retinal image analysis using AI-powered deep learning models', 10)
    addText('• Lifestyle and metabolic risk factor evaluation', 10)
    addText('• Clinical data integration for comprehensive risk scoring', 10)
    yPos += 3

    addText('What your score means:', 11, true)
    addText(`Your ${riskScore.toFixed(1)}% risk score represents the probability of developing diabetes-related complications within the next 5-10 years if current health patterns continue unchanged.`, 10)
    yPos += 5
    addDivider()

    // Key Resources & Support
    if (yPos > pageHeight - margin - 60) {
      pdf.addPage()
      yPos = margin
    }
    addText('RESOURCES & SUPPORT', 14, true, [102, 126, 234])
    addText('Recommended Actions:', 11, true)
    addText('1. Share this report with your primary care physician', 10)
    addText('2. Consider diabetes prevention programs in your area', 10)
    addText('3. Join support groups or online communities for motivation', 10)
    addText('4. Track your progress using health monitoring apps', 10)
    addText('5. Schedule regular follow-up assessments every 3-6 months', 10)
    yPos += 5
    addDivider()

    // Final Page - Disclaimer and Footer
    if (yPos > pageHeight - 40) {
      pdf.addPage()
      yPos = margin
    } else {
      yPos = pageHeight - 40
    }

    pdf.setFontSize(8)
    pdf.setTextColor(100, 100, 100)
    pdf.setFont('helvetica', 'normal')
    const disclaimer = 'DISCLAIMER: This report is generated by an AI-powered system for informational and educational purposes only. It does not constitute medical advice, diagnosis, or treatment. The risk assessments are statistical predictions based on available data and should not replace professional medical consultation. Always consult with qualified healthcare professionals for personalized medical advice, diagnosis, and treatment. Individual results may vary.'
    const disclaimerLines = pdf.splitTextToSize(disclaimer, contentWidth)
    disclaimerLines.forEach(line => {
      pdf.text(line, margin, yPos)
      yPos += 3.5
    })

    yPos += 2
    pdf.setFontSize(9)
    pdf.setFont('helvetica', 'bold')
    pdf.text(`Powered by DIAVITA - AI-Driven Diabetes Prevention | ${new Date().getFullYear()}`, pageWidth / 2, yPos, { align: 'center' })
    pdf.setFont('helvetica', 'normal')
    pdf.text('See Clearly & Live Freely', pageWidth / 2, yPos + 4, { align: 'center' })

    // Save the PDF
    pdf.save(`DIAVITA-Health-Report-${new Date().toISOString().split('T')[0]}.pdf`)
  }


  // Extract user's health metrics from latest analysis
  const getUserHealthMetrics = () => {
    if (!latestResult) return null

    const metrics = latestResult.lifestyle_data || {}
    const retinalData = latestResult.retinal_data || {}

    return {
      vitals: [
        { icon: Heart, label: 'Blood Pressure', value: metrics.blood_pressure || '120/80', unit: 'mmHg', color: '#FF6B9D' },
        { icon: Droplets, label: 'Glucose', value: metrics.blood_glucose || '95', unit: 'mg/dL', color: '#4ECDC4' },
        { icon: Scale, label: 'BMI', value: metrics.bmi || '24.5', unit: 'kg/m²', color: '#FFD93D' },
        { icon: Brain, label: 'HbA1c', value: metrics.hba1c || '5.4', unit: '%', color: '#95E1D3' }
      ],
      lifestyle: [
        { icon: Activity, label: 'Exercise', value: metrics.physical_activity || '30', unit: 'min/day', color: '#F38181' },
        { icon: Moon, label: 'Sleep', value: metrics.sleep_hours || '7', unit: 'hours', color: '#AA96DA' },
        { icon: Zap, label: 'Stress', value: metrics.stress_level || 'Low', unit: '', color: '#FCBAD3' },
        { icon: Eye, label: 'Retinal', value: retinalData.dr_detected ? 'Alert' : 'Clear', unit: '', color: '#A8E6CF' }
      ]
    }
  }

  const healthMetrics = getUserHealthMetrics()

  if (loading) {
    return (
      <>
        <Navigation />
        <div className="dashboard-page">
          <motion.div className="loading-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <motion.div className="pulse-loader"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <Heart size={48} />
            </motion.div>
            <p>Analyzing your health data...</p>
          </motion.div>
        </div>
      </>
    )
  }

  // First-time user - no analysis yet
  if (!latestResult) {
    return (
      <>
        <Navigation />
        <div className="dashboard-page">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="welcome-section"
          >
            <motion.div className="welcome-hero"
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <motion.div className="welcome-avatar"
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", delay: 0.3 }}
              >
                <User size={48} />
              </motion.div>
              <h1 className="welcome-title">
                Welcome back,
                <span className="welcome-user-name"> {user?.username}</span>
              </h1>
              <p className="welcome-subtitle">
                Let's begin your diabetes risk assessment with our AI-powered health analysis
              </p>

              <div className="onboarding-cards">
                {[
                  { icon: Eye, title: 'Retinal Scan', desc: 'AI-powered eye analysis for early detection', delay: 0.5 },
                  { icon: BarChart3, title: 'Risk Assessment', desc: 'Comprehensive health risk evaluation', delay: 0.6 },
                  { icon: Shield, title: 'Prevention Plan', desc: 'Personalized action steps for better health', delay: 0.7 }
                ].map((step, idx) => (
                  <motion.div key={idx} className="onboarding-card"
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: step.delay }}
                  >
                    <div className="card-icon-wrapper">
                      <step.icon size={32} />
                    </div>
                    <h4>{step.title}</h4>
                    <p>{step.desc}</p>
                  </motion.div>
                ))}
              </div>

              <button
                className="start-assessment-btn"
                onClick={() => navigate('/analyze')}
              >
                <Sparkles size={20} />
                Begin Health Assessment
                <ArrowRight size={20} />
              </button>
            </motion.div>
          </motion.div>
        </div>
      </>
    )
  }

  // User with analysis results
  const riskScore = latestResult.combined_risk || 0
  const riskGradient = getRiskGradient(riskScore)

  return (
    <>
      <Navigation />
      <div className="dashboard-page">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="dashboard-content"
        >
          {/* Header Section */}
          <motion.div className="dashboard-header"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
          >
            <div className="user-greeting">
              <h1 className="greeting-title">
                Health Dashboard
              </h1>
              <p className="greeting-subtitle">
                Welcome back, {user?.username} • {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
              </p>
            </div>
          </motion.div>

          {/* Risk Score Hero */}
          <motion.div className="risk-hero-section"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            <div className="risk-hero-card">
              <div className="risk-visualization">
                <motion.div className="risk-circle-wrapper"
                  initial={{ scale: 0.9 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.5 }}
                >
                  <svg className="progress-ring" width="280" height="280" viewBox="0 0 280 280">
                    <circle
                      cx="140"
                      cy="140"
                      r="110"
                      fill="none"
                      stroke="#f0f0f0"
                      strokeWidth="18"
                    />
                    <motion.circle
                      cx="140"
                      cy="140"
                      r="110"
                      fill="none"
                      stroke={riskScore < 50 ? '#4CAF50' : riskScore < 75 ? '#FF9800' : '#FF5722'}
                      strokeWidth="18"
                      strokeDasharray={`${2 * Math.PI * 110}`}
                      initial={{ strokeDashoffset: 2 * Math.PI * 110 }}
                      animate={{ strokeDashoffset: 2 * Math.PI * 110 * (1 - riskScore / 100) }}
                      transform="rotate(-90 140 140)"
                      transition={{ duration: 2, ease: "easeInOut" }}
                    />
                    <text x="140" y="150" textAnchor="middle" fontSize="48" fontWeight="700" fill={riskScore < 50 ? '#4CAF50' : riskScore < 75 ? '#FF9800' : '#FF5722'}>
                      {riskScore.toFixed(0)}%
                    </text>
                    <text x="140" y="175" textAnchor="middle" fontSize="16" fill="#999">
                      Risk Score
                    </text>
                  </svg>
                </motion.div>

                <div className="risk-info">
                  <div className="risk-label-badge" style={{ background: riskGradient }}>
                    {getRiskLabel(latestResult.risk_category)}
                  </div>

                  {summary?.risk_trend && (
                    <motion.div className="trend-indicator"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.5 }}
                    >
                      {summary.risk_trend === 'improving' ? (
                        <div className="trend-badge improving">
                          <TrendingDown size={18} />
                          <span>Improving</span>
                        </div>
                      ) : (
                        <div className="trend-badge worsening">
                          <TrendingUp size={18} />
                          <span>Needs Focus</span>
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>
              </div>

              <div className="risk-breakdown" style={{ marginTop: '2rem' }}>
                <h3 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Risk Components</h3>
                <div style={{ display: 'flex', justifyContent: 'center', paddingLeft: '5rem' }}>
                  <div className="breakdown-items" style={{
                    display: 'inline-flex',
                    gap: '0',
                    alignItems: 'center'
                  }}>
                    <div className="breakdown-item" style={{ textAlign: 'center', padding: '0 3rem' }}>
                      <span className="breakdown-label" style={{ display: 'block', fontSize: '0.9rem', color: '#9ca3af', marginBottom: '0.5rem' }}>Retinal Analysis</span>
                      <span className="breakdown-value" style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#6366f1' }}>
                        {(latestResult.retinal_risk || 0).toFixed(2)}%
                      </span>
                    </div>

                    <div style={{ width: '2px', height: '60px', background: 'rgba(156, 163, 175, 0.3)' }}></div>

                    <div className="breakdown-item" style={{ textAlign: 'center', padding: '0 3rem' }}>
                      <span className="breakdown-label" style={{ display: 'block', fontSize: '0.9rem', color: '#9ca3af', marginBottom: '0.5rem' }}>Lifestyle Factors</span>
                      <span className="breakdown-value" style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#10b981' }}>
                        {(latestResult.lifestyle_risk || 0).toFixed(2)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Download Report Section */}
              <div className="download-section" style={{
                marginTop: '2rem',
                paddingTop: '1.5rem',
                borderTop: '1px solid rgba(255,255,255,0.1)',
                display: 'flex',
                gap: '1rem',
                justifyContent: 'center'
              }}>
                <button
                  className="download-btn pdf-btn"
                  onClick={downloadPDF}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.75rem 1.5rem',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    transition: 'transform 0.2s'
                  }}
                  onMouseEnter={e => e.target.style.transform = 'translateY(-2px)'}
                  onMouseLeave={e => e.target.style.transform = 'translateY(0)'}
                >
                  <FileText size={18} />
                  Download PDF Report
                </button>

              </div>
            </div>
          </motion.div>

          {/* Health Metrics Summary */}
          {healthMetrics && (
            <motion.div className="health-metrics-section"
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="section-title">Your Health Snapshot</h2>

              <div className="metrics-grid">
                <div className="metrics-group">
                  <h3>Vital Signs</h3>
                  <div className="metrics-cards">
                    {healthMetrics.vitals.map((metric, idx) => (
                      <motion.div key={idx}
                        className="metric-card"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.4 + idx * 0.1 }}
                        whileHover={{ y: -5, scale: 1.05 }}
                        onClick={() => setActiveMetric(activeMetric === idx ? null : idx)}
                      >
                        <div className="metric-icon" style={{ background: metric.color }}>
                          <metric.icon size={24} />
                        </div>
                        <div className="metric-info">
                          <span className="metric-label">{metric.label}</span>
                          <div className="metric-value-wrapper">
                            <span className="metric-value">{metric.value}</span>
                            {metric.unit && <span className="metric-unit">{metric.unit}</span>}
                          </div>
                        </div>
                        <AnimatePresence>
                          {activeMetric === idx && (
                            <motion.div className="metric-tooltip"
                              initial={{ opacity: 0, y: -10 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -10 }}
                            >
                              Latest reading from your health assessment
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.div>
                    ))}
                  </div>
                </div>

                <div className="metrics-group">
                  <h3>Lifestyle Factors</h3>
                  <div className="metrics-cards">
                    {healthMetrics.lifestyle.map((metric, idx) => (
                      <motion.div key={idx}
                        className="metric-card lifestyle"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.6 + idx * 0.1 }}
                        whileHover={{ y: -5, scale: 1.05 }}
                      >
                        <div className="metric-icon" style={{ background: metric.color }}>
                          <metric.icon size={24} />
                        </div>
                        <div className="metric-info">
                          <span className="metric-label">{metric.label}</span>
                          <div className="metric-value-wrapper">
                            <span className="metric-value">{metric.value}</span>
                            {metric.unit && <span className="metric-unit">{metric.unit}</span>}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Action Cards */}
          <motion.div className="action-section"
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <div className="action-cards-grid">
              {/* Health Plan Card */}
              <motion.div className="action-card plan-card"
                whileHover={{ scale: 1.02 }}
              >
                <div className="card-glow"></div>
                {primaryPlan ? (
                  <>
                    <div className="card-header">
                      <Shield size={28} />
                      <h3>Active Health Plan</h3>
                    </div>
                    <div className="plan-content">
                      <h4>{primaryPlan.plan_name}</h4>
                      <p className="plan-desc">{primaryPlan.description}</p>

                      <div className="progress-indicator" style={{ textAlign: 'center', marginTop: '1rem' }}>
                        <div className="progress-header" style={{ marginBottom: '0.5rem' }}>
                          <span style={{ fontSize: '0.9rem', color: '#6b7280' }}>Progress</span>
                        </div>
                        <div className="progress-display" style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
                          {Number(primaryPlan.current_progress).toFixed(2)}%
                        </div>
                      </div>

                      <button className="action-btn primary" onClick={() => navigate('/progress')}>
                        Continue Plan
                        <ChevronRight size={18} />
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="empty-plan-state">
                    <div className="empty-icon">
                      <Target size={48} />
                    </div>
                    <h3>Start Your Health Journey</h3>
                    <p>Select a personalized plan to begin improving your health</p>
                    <button className="action-btn highlight" onClick={() => navigate('/plans')}>
                      <Sparkles size={18} />
                      Choose Plan
                    </button>
                  </div>
                )}
              </motion.div>

              {/* Quick Actions Card */}
              <motion.div className="action-card quick-actions"
                whileHover={{ scale: 1.02 }}
              >
                <div className="card-header">
                  <Zap size={28} />
                  <h3>Quick Actions</h3>
                </div>

                <div className="quick-action-list">
                  <button className="quick-action-item"
                    onClick={() => navigate('/analyze')}
                  >
                    <Eye size={20} />
                    <span>New Analysis</span>
                    <ChevronRight size={16} />
                  </button>

                  <button className="quick-action-item"
                    onClick={() => navigate('/results')}
                  >
                    <BarChart3 size={20} />
                    <span>View Results</span>
                    <ChevronRight size={16} />
                  </button>

                  <button className="quick-action-item"
                    onClick={() => navigate('/plans')}
                  >
                    <Target size={20} />
                    <span>Health Plans</span>
                    <ChevronRight size={16} />
                  </button>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Insights Section */}
          {latestResult?.recommendations && (
            <motion.div className="insights-section"
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              <h2 className="section-title">AI Health Insights</h2>
              <div className="insights-grid">
                {latestResult.recommendations.slice(0, 3).map((rec, idx) => (
                  <motion.div key={idx} className="insight-card"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.9 + idx * 0.1 }}
                    whileHover={{ scale: 1.02 }}
                  >
                    <div className="insight-icon">
                      <Brain size={20} />
                    </div>
                    <p>{rec}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>
    </>
  )
}

export default DashboardPage