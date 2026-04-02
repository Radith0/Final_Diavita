import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Upload, User, Activity, Heart, ArrowRight, Loader, Ruler, Weight, Info, Moon, Coffee, Dumbbell, Brain, Apple, Cigarette, FlaskConical, ChevronDown, ChevronUp, Eye, AlertTriangle, X } from 'lucide-react'
import { analyzeComplete } from '../services/api'
import { saveAnalysisResult } from '../services/results'
import { getPrimaryPlan } from '../services/plans'
import './AnalysisPage.css'

function AnalysisPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [heightUnit, setHeightUnit] = useState('cm') // 'cm' or 'ft'
  const [weightUnit, setWeightUnit] = useState('kg') // 'kg' or 'lbs'
  const [waistUnit, setWaistUnit] = useState('in') // 'cm' or 'in' - default to inches
  const [lifestyleData, setLifestyleData] = useState({
    // Basic Demographics
    gender: 'male',
    age: '',
    ethnicity: 3,

    // Body Measurements (stored in metric for backend)
    height_cm: '',
    weight_kg: '',
    bmi: '',  // Auto-calculated
    waist_circumference: '',

    // Imperial inputs (temporary, converted to metric)
    height_ft: '',
    height_in: '',
    weight_lbs: '',
    waist_inches: '',

    // Blood Pressure
    systolic_bp: '',
    diastolic_bp: '',

    // Lab Results
    HbA1c: '',
    hdl_cholesterol: '',
    total_cholesterol: '',  // Adding total cholesterol
    blood_glucose: '',  // Adding blood glucose

    // Medical History
    has_hypertension: false,
    takes_cholesterol_med: false,
    family_diabetes_history: false,

    // Lifestyle & Habits (NEW FIELDS)
    smoking: 'no',
    alcohol: 'no',
    physical_activity: '',  // minutes per week
    sleep_hours: '',
    stress_level: 'moderate',
    diet_quality: 'average'
  })
  const [loading, setLoading] = useState(false)
  const [showScenarios, setShowScenarios] = useState(true) // Toggle for showing/hiding scenarios
  const [activeTab, setActiveTab] = useState('basic') // Tab state for lifestyle data
  const [inputErrors, setInputErrors] = useState({}) // Track validation errors for inputs
  const [showRetinalConfirmModal, setShowRetinalConfirmModal] = useState(false)
  const [pendingImageFile, setPendingImageFile] = useState(null)
  const [pendingImagePreview, setPendingImagePreview] = useState(null)

  // Pre-defined scenarios for testing
  const scenarios = {
    healthy: {
      name: 'Healthy Adult',
      description: 'Low risk profile',
      color: '#2ECC71',
      data: {
        gender: 'male',
        age: 32,
        height_cm: '175',
        weight_kg: '70',
        systolic_bp: '118',
        diastolic_bp: '76',
        HbA1c: '5.2',
        blood_glucose: '85',
        hdl_cholesterol: '55',
        total_cholesterol: '180',
        has_hypertension: false,
        takes_cholesterol_med: false,
        family_diabetes_history: false,
        smoking: 'no',
        alcohol: 'no',
        physical_activity: '180',
        sleep_hours: '8',
        stress_level: 'low',
        diet_quality: 'good'
      }
    },
    prediabetic: {
      name: 'Pre-diabetic',
      description: 'Moderate risk profile',
      color: '#F39C12',
      data: {
        gender: 'female',
        age: 42,  // Reduced age to lower risk
        height_cm: '165',
        weight_kg: '73',  // Reduced weight slightly
        systolic_bp: '128',  // Improved BP
        diastolic_bp: '82',
        HbA1c: '5.8',  // Lower HbA1c but still pre-diabetic
        blood_glucose: '105',  // Improved glucose
        hdl_cholesterol: '48',  // Better HDL
        total_cholesterol: '210',  // Better total cholesterol
        has_hypertension: false,
        takes_cholesterol_med: false,
        family_diabetes_history: true,
        smoking: 'no',
        alcohol: 'moderate',
        physical_activity: '120',  // More activity
        sleep_hours: '7',  // Better sleep
        stress_level: 'moderate',
        diet_quality: 'average'
      }
    },
    highRisk: {
      name: 'High Risk',
      description: 'High risk profile',
      color: '#E74C3C',
      data: {
        gender: 'male',
        age: 50,  // Reduced age slightly
        height_cm: '178',
        weight_kg: '88',  // Reduced weight
        systolic_bp: '138',  // Slightly better BP
        diastolic_bp: '88',
        HbA1c: '6.1',  // Lower HbA1c
        blood_glucose: '118',  // Better glucose
        hdl_cholesterol: '40',  // Slightly better HDL
        total_cholesterol: '245',  // Better cholesterol
        has_hypertension: true,
        takes_cholesterol_med: true,
        family_diabetes_history: true,
        smoking: 'no',  // Changed from yes to no
        alcohol: 'moderate',  // Changed from heavy to moderate
        physical_activity: '60',  // More activity
        sleep_hours: '6',  // Better sleep
        stress_level: 'high',
        diet_quality: 'poor'
      }
    },
    diabetic: {
      name: 'Type 2 Diabetic',
      description: 'Very high risk profile',
      color: '#8E44AD',
      data: {
        gender: 'female',
        age: 62,
        height_cm: '160',
        weight_kg: '85',
        systolic_bp: '148',
        diastolic_bp: '95',
        HbA1c: '7.8',
        blood_glucose: '165',
        hdl_cholesterol: '35',
        total_cholesterol: '280',
        has_hypertension: true,
        takes_cholesterol_med: true,
        family_diabetes_history: true,
        smoking: 'former',
        alcohol: 'moderate',
        physical_activity: '20',
        sleep_hours: '5.5',
        stress_level: 'high',
        diet_quality: 'poor'
      }
    }
  }

  // Convert height ft/in to cm
  useEffect(() => {
    if (heightUnit === 'ft') {
      const ft = parseFloat(lifestyleData.height_ft) || 0
      const inches = parseFloat(lifestyleData.height_in) || 0
      const totalInches = (ft * 12) + inches
      const cm = totalInches * 2.54

      if (cm > 0) {
        setLifestyleData(prev => ({ ...prev, height_cm: cm.toFixed(1) }))
      }
    }
  }, [lifestyleData.height_ft, lifestyleData.height_in, heightUnit])

  // Convert weight lbs to kg
  useEffect(() => {
    if (weightUnit === 'lbs') {
      const lbs = parseFloat(lifestyleData.weight_lbs) || 0
      const kg = lbs * 0.453592

      if (kg > 0) {
        setLifestyleData(prev => ({ ...prev, weight_kg: kg.toFixed(1) }))
      }
    }
  }, [lifestyleData.weight_lbs, weightUnit])

  // Convert waist inches to cm
  useEffect(() => {
    if (waistUnit === 'in') {
      const inches = parseFloat(lifestyleData.waist_inches) || 0
      const cm = inches * 2.54

      if (cm > 0) {
        setLifestyleData(prev => ({ ...prev, waist_circumference: cm.toFixed(1) }))
      }
    }
  }, [lifestyleData.waist_inches, waistUnit])

  // Auto-calculate BMI when height or weight changes
  useEffect(() => {
    const height = parseFloat(lifestyleData.height_cm)
    const weight = parseFloat(lifestyleData.weight_kg)

    if (height > 0 && weight > 0) {
      const heightInMeters = height / 100
      const bmi = weight / (heightInMeters * heightInMeters)
      setLifestyleData(prev => ({ ...prev, bmi: bmi.toFixed(1) }))
    }
  }, [lifestyleData.height_cm, lifestyleData.weight_kg])

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Check file size (reject if too small - likely low quality)
      if (file.size < 10000) { // Less than 10KB
        alert('Image quality is too low. Please upload a higher quality retinal image.')
        e.target.value = null // Reset input
        return
      }

      const reader = new FileReader()
      reader.onloadend = () => {
        const img = new Image()
        img.onload = () => {
          // Check image dimensions
          if (img.width < 200 || img.height < 200) {
            alert('Image resolution is too low. Minimum resolution required: 200x200 pixels. Please upload a higher quality retinal image.')
            e.target.value = null // Reset input
            setImage(null)
            setImagePreview(null)
            return
          }

          // Show confirmation modal for retinal image verification
          setPendingImageFile(file)
          setPendingImagePreview(reader.result)
          setShowRetinalConfirmModal(true)
          e.target.value = null // Reset file input
        }

        img.onerror = () => {
          alert('Failed to load image. Please try a different image.')
          e.target.value = null
          setImage(null)
          setImagePreview(null)
        }

        img.src = reader.result
      }
      reader.readAsDataURL(file)
    }
  }

  const confirmRetinalImage = () => {
    setImage(pendingImageFile)
    setImagePreview(pendingImagePreview)
    setShowRetinalConfirmModal(false)
    setPendingImageFile(null)
    setPendingImagePreview(null)
  }

  const cancelRetinalImage = () => {
    setShowRetinalConfirmModal(false)
    setPendingImageFile(null)
    setPendingImagePreview(null)
  }

  const handleInputChange = (field, value) => {
    // Validate the input
    let error = null
    const numValue = parseFloat(value)

    // Check for negative values in numeric fields
    const numericFields = [
      'age', 'height_cm', 'height_ft', 'height_in', 'weight_kg', 'weight_lbs',
      'waist_circumference', 'waist_inches', 'systolic_bp', 'diastolic_bp',
      'HbA1c', 'hdl_cholesterol', 'total_cholesterol', 'blood_glucose',
      'physical_activity', 'sleep_hours'
    ]

    if (numericFields.includes(field) && value !== '' && numValue < 0) {
      error = 'Value cannot be negative'
    }

    // Specific field validations
    if (field === 'sleep_hours' && value !== '') {
      if (numValue > 24) {
        error = 'Sleep hours cannot exceed 24'
      } else if (numValue < 0) {
        error = 'Sleep hours cannot be negative'
      }
    }

    if (field === 'age' && value !== '') {
      if (numValue < 0) {
        error = 'Age cannot be negative'
      } else if (numValue > 150) {
        error = 'Please enter a valid age'
      }
    }

    if (field === 'systolic_bp' && value !== '') {
      if (numValue < 0) {
        error = 'Blood pressure cannot be negative'
      } else if (numValue > 300) {
        error = 'Please enter a valid blood pressure'
      }
    }

    if (field === 'diastolic_bp' && value !== '') {
      if (numValue < 0) {
        error = 'Blood pressure cannot be negative'
      } else if (numValue > 200) {
        error = 'Please enter a valid blood pressure'
      }
    }

    if (field === 'HbA1c' && value !== '') {
      if (numValue < 0) {
        error = 'HbA1c cannot be negative'
      } else if (numValue > 20) {
        error = 'Please enter a valid HbA1c value'
      }
    }

    if (field === 'physical_activity' && value !== '') {
      const maxMinutesPerWeek = 7 * 24 * 60 // 7 days * 24 hours * 60 minutes
      if (numValue < 0) {
        error = 'Activity minutes cannot be negative'
      } else if (numValue > maxMinutesPerWeek) {
        error = 'Activity minutes cannot exceed total minutes in a week'
      }
    }

    // Update error state
    setInputErrors(prev => ({
      ...prev,
      [field]: error
    }))

    // Always update the value (even if invalid) so user can see what they're typing
    setLifestyleData(prev => ({ ...prev, [field]: value }))
  }

  // Function to apply a scenario
  const applyScenario = (scenario) => {
    // Calculate BMI for the scenario
    const height = parseFloat(scenario.data.height_cm)
    const weight = parseFloat(scenario.data.weight_kg)
    const heightInMeters = height / 100
    const bmi = (weight / (heightInMeters * heightInMeters)).toFixed(1)

    setLifestyleData({
      ...scenario.data,
      bmi: bmi,
      ethnicity: 3, // Keep default ethnicity
      // Clear imperial inputs since we're setting metric values
      height_ft: '',
      height_in: '',
      weight_lbs: '',
      waist_inches: '',
      waist_circumference: ''
    })

    // Set units to metric for consistency
    setHeightUnit('cm')
    setWeightUnit('kg')
    setWaistUnit('cm')
  }

  const handleSubmit = async () => {
    if (!image) {
      alert('Please upload a retinal image')
      return
    }

    setLoading(true)

    try {
      // 1. Perform analysis
      const result = await analyzeComplete(image, lifestyleData)

      console.log('📊 Analysis result received:', result)

      // 2. Extract risk scores from result (handle different response structures)
      const overallRisk = result.risk_assessment?.overall_risk_score || result.final_risk || result.risk_score || 0
      const retinalRisk = result.risk_assessment?.retinal_analysis?.risk_score || result.retinal_risk || 0
      const lifestyleRisk = result.risk_assessment?.lifestyle_analysis?.risk_score || result.lifestyle_risk || 0

      // Convert to percentage if needed (0-1 scale to 0-100)
      const toPercentage = (val) => val > 1 ? val : val * 100

      const riskData = {
        analysis_type: 'complete',
        retinal_risk: toPercentage(retinalRisk),
        lifestyle_risk: toPercentage(lifestyleRisk),
        combined_risk: toPercentage(overallRisk),
        confidence_score: result.confidence || result.confidence_score || 0.85,
        lifestyle_data: lifestyleData,
        detailed_results: result,
        recommendations: result.personalized_advice?.recommendations || result.recommendations || []
      }

      console.log('💾 Saving analysis data:', riskData)

      // 3. Auto-save results to database
      const savedResult = await saveAnalysisResult(riskData)

      console.log('✅ Analysis saved!', savedResult)

      // 3. ALWAYS redirect to results page to show the analysis
      navigate('/results', {
        state: {
          results: result,
          savedResult: savedResult,
          justCompleted: true
        }
      })

    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="analysis-page">
      <div className="analysis-background">
        <div className="diagnostic-grid"></div>
      </div>

      <div className="container analysis-container">
        {/* Progress Indicator */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="progress-indicator"
        >
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <div className="step-number">1</div>
            <span>Retinal Image</span>
          </div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <div className="step-number">2</div>
            <span>Lifestyle Data</span>
          </div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
            <div className="step-number">3</div>
            <span>Analysis</span>
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="form-section glass"
            >
              <h2>Upload Retinal Image</h2>
              <p className="section-description">
                Upload a retinal fundus image captured from a smartphone-based retinal camera or standard fundus camera.
              </p>

              <div className="upload-area" onClick={() => document.getElementById('imageInput').click()}>
                {imagePreview ? (
                  <div className="image-preview">
                    <img src={imagePreview} alt="Retinal preview" />
                    <div className="image-overlay">
                      <Upload size={32} />
                      <span>Change Image</span>
                    </div>
                  </div>
                ) : (
                  <div className="upload-placeholder">
                    <Upload size={48} />
                    <h3>Drop retinal image here</h3>
                    <p>or click to browse</p>
                    <span className="file-formats">JPG, PNG (max 10MB)</span>
                  </div>
                )}
                <input
                  id="imageInput"
                  type="file"
                  accept="image/jpeg,image/jpg,image/png"
                  onChange={handleImageUpload}
                  style={{ display: 'none' }}
                />
              </div>

              <button
                className="next-button"
                onClick={() => setStep(2)}
                disabled={!image}
              >
                Next
                <ArrowRight size={20} />
              </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="form-section glass large-form"
            >
              <h2>Health & Lifestyle Profile</h2>
              <p className="section-description">
                Provide your health information for accurate diabetes risk assessment.
              </p>

              {/* Scenario Selection */}
              <div className="scenarios-section" style={{ marginBottom: '20px' }}>
                <button
                  className="toggle-scenarios-btn"
                  onClick={() => setShowScenarios(!showScenarios)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px',
                    background: 'rgba(74, 144, 226, 0.1)',
                    border: '1px solid rgba(74, 144, 226, 0.3)',
                    borderRadius: '8px',
                    color: '#4A90E2',
                    cursor: 'pointer',
                    fontSize: '14px',
                    marginBottom: '12px',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <FlaskConical size={16} />
                  Test Scenarios
                  {showScenarios ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>

                {showScenarios && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="scenarios-grid"
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                      gap: '12px',
                      marginTop: '12px'
                    }}
                  >
                    {Object.entries(scenarios).map(([key, scenario]) => (
                      <button
                        key={key}
                        className="scenario-btn"
                        onClick={() => applyScenario(scenario)}
                        style={{
                          padding: '12px',
                          background: `linear-gradient(135deg, ${scenario.color}15, ${scenario.color}10)`,
                          border: `1px solid ${scenario.color}40`,
                          borderRadius: '8px',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          textAlign: 'left'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.transform = 'translateY(-2px)'
                          e.currentTarget.style.borderColor = `${scenario.color}80`
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.transform = 'translateY(0)'
                          e.currentTarget.style.borderColor = `${scenario.color}40`
                        }}
                      >
                        <div style={{ fontWeight: '600', color: scenario.color, marginBottom: '4px' }}>
                          {scenario.name}
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          {scenario.description}
                        </div>
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>

              {/* Tab Navigation */}
              <div className="tab-navigation" style={{
                display: 'flex',
                gap: '10px',
                marginBottom: '20px',
                borderBottom: '2px solid rgba(255, 255, 255, 0.1)',
                paddingBottom: '10px'
              }}>
                <button
                  className={`tab-btn ${activeTab === 'basic' ? 'active' : ''}`}
                  onClick={() => setActiveTab('basic')}
                  style={{
                    padding: '10px 20px',
                    background: activeTab === 'basic' ? 'rgba(74, 144, 226, 0.2)' : 'transparent',
                    border: activeTab === 'basic' ? '1px solid #4A90E2' : '1px solid transparent',
                    borderRadius: '8px 8px 0 0',
                    color: activeTab === 'basic' ? '#4A90E2' : '#aaa',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <User size={16} />
                  Basic Info
                </button>

                <button
                  className={`tab-btn ${activeTab === 'body' ? 'active' : ''}`}
                  onClick={() => setActiveTab('body')}
                  style={{
                    padding: '10px 20px',
                    background: activeTab === 'body' ? 'rgba(74, 144, 226, 0.2)' : 'transparent',
                    border: activeTab === 'body' ? '1px solid #4A90E2' : '1px solid transparent',
                    borderRadius: '8px 8px 0 0',
                    color: activeTab === 'body' ? '#4A90E2' : '#aaa',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <Ruler size={16} />
                  Body Measurements
                </button>

                <button
                  className={`tab-btn ${activeTab === 'medical' ? 'active' : ''}`}
                  onClick={() => setActiveTab('medical')}
                  style={{
                    padding: '10px 20px',
                    background: activeTab === 'medical' ? 'rgba(74, 144, 226, 0.2)' : 'transparent',
                    border: activeTab === 'medical' ? '1px solid #4A90E2' : '1px solid transparent',
                    borderRadius: '8px 8px 0 0',
                    color: activeTab === 'medical' ? '#4A90E2' : '#aaa',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <Heart size={16} />
                  Medical Data
                </button>

                <button
                  className={`tab-btn ${activeTab === 'lifestyle' ? 'active' : ''}`}
                  onClick={() => setActiveTab('lifestyle')}
                  style={{
                    padding: '10px 20px',
                    background: activeTab === 'lifestyle' ? 'rgba(74, 144, 226, 0.2)' : 'transparent',
                    border: activeTab === 'lifestyle' ? '1px solid #4A90E2' : '1px solid transparent',
                    borderRadius: '8px 8px 0 0',
                    color: activeTab === 'lifestyle' ? '#4A90E2' : '#aaa',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <Coffee size={16} />
                  Lifestyle & Habits
                </button>
              </div>

              {/* Tab Content */}
              <div className="tab-content">
                {/* Basic Info Tab */}
                {activeTab === 'basic' && (
                  <motion.div
                    key="basic"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <div className="form-section-header">
                      <User size={20} />
                      <h3>Basic Information</h3>
                    </div>
                <div className="form-grid">
                <div className="form-group">
                  <label>Gender</label>
                  <select
                    value={lifestyleData.gender}
                    onChange={(e) => handleInputChange('gender', e.target.value)}
                    className="select-input"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Age (years) <span className="required">*</span></label>
                  <input
                    type="number"
                    value={lifestyleData.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                    placeholder="45"
                    required
                    style={{
                      borderColor: inputErrors.age ? '#FF5722' : '',
                      backgroundColor: inputErrors.age ? '#FFF5F5' : ''
                    }}
                  />
                  {inputErrors.age && (
                    <span className="field-error" style={{ color: '#FF5722', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                      {inputErrors.age}
                    </span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    Ethnicity
                    <span className="info-tooltip" title="Used for risk calculation based on population data">
                      <Info size={14} />
                    </span>
                  </label>
                  <select
                    value={lifestyleData.ethnicity}
                    onChange={(e) => handleInputChange('ethnicity', parseInt(e.target.value))}
                    className="select-input"
                  >
                    <option value={1}>Mexican American</option>
                    <option value={2}>Other Hispanic</option>
                    <option value={3}>Non-Hispanic White</option>
                    <option value={4}>Non-Hispanic Black</option>
                    <option value={6}>Non-Hispanic Asian</option>
                    <option value={7}>Other/Multi-Racial</option>
                  </select>
                </div>
              </div>
                  </motion.div>
                )}

                {/* Body Measurements Tab */}
                {activeTab === 'body' && (
                  <motion.div
                    key="body"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
              <div className="form-section-header">
                <Activity size={20} />
                <h3>Body Measurements</h3>
              </div>

              <div className="form-grid">
                {/* Height with individual unit selector */}
                <div className="form-group with-unit-select">
                  <label>
                    <Ruler size={16} />
                    Height <span className="required">*</span>
                  </label>
                  <div className="input-with-unit">
                    {heightUnit === 'cm' ? (
                      <input
                        type="number"
                        step="0.1"
                        value={lifestyleData.height_cm}
                        onChange={(e) => handleInputChange('height_cm', e.target.value)}
                        placeholder="170"
                        required
                        style={{
                          borderColor: inputErrors.height_cm ? '#FF5722' : '',
                          backgroundColor: inputErrors.height_cm ? '#FFF5F5' : ''
                        }}
                      />
                    ) : (
                      <div className="dual-input">
                        <input
                          type="number"
                          value={lifestyleData.height_ft}
                          onChange={(e) => handleInputChange('height_ft', e.target.value)}
                          placeholder="5"
                          className="small-input"
                          required
                          style={{
                            borderColor: inputErrors.height_ft ? '#FF5722' : '',
                            backgroundColor: inputErrors.height_ft ? '#FFF5F5' : ''
                          }}
                        />
                        <span className="input-separator">ft</span>
                        <input
                          type="number"
                          value={lifestyleData.height_in}
                          onChange={(e) => handleInputChange('height_in', e.target.value)}
                          placeholder="10"
                          className="small-input"
                          required
                          style={{
                            borderColor: inputErrors.height_in ? '#FF5722' : '',
                            backgroundColor: inputErrors.height_in ? '#FFF5F5' : ''
                          }}
                        />
                        <span className="input-separator">in</span>
                      </div>
                    )}
                    <select
                      value={heightUnit}
                      onChange={(e) => setHeightUnit(e.target.value)}
                      className="unit-selector"
                    >
                      <option value="cm">cm</option>
                      <option value="ft">ft/in</option>
                    </select>
                  </div>
                </div>

                {/* Weight with individual unit selector */}
                <div className="form-group with-unit-select">
                  <label>
                    <Weight size={16} />
                    Weight <span className="required">*</span>
                  </label>
                  <div className="input-with-unit">
                    {weightUnit === 'kg' ? (
                      <input
                        type="number"
                        step="0.1"
                        value={lifestyleData.weight_kg}
                        onChange={(e) => handleInputChange('weight_kg', e.target.value)}
                        placeholder="75"
                        required
                        style={{
                          borderColor: inputErrors.weight_kg ? '#FF5722' : '',
                          backgroundColor: inputErrors.weight_kg ? '#FFF5F5' : ''
                        }}
                      />
                    ) : (
                      <input
                        type="number"
                        step="0.1"
                        value={lifestyleData.weight_lbs}
                        onChange={(e) => handleInputChange('weight_lbs', e.target.value)}
                        placeholder="165"
                        required
                        style={{
                          borderColor: inputErrors.weight_lbs ? '#FF5722' : '',
                          backgroundColor: inputErrors.weight_lbs ? '#FFF5F5' : ''
                        }}
                      />
                    )}
                    <select
                      value={weightUnit}
                      onChange={(e) => setWeightUnit(e.target.value)}
                      className="unit-selector"
                    >
                      <option value="kg">kg</option>
                      <option value="lbs">lbs</option>
                    </select>
                  </div>
                </div>

                {/* Waist with individual unit selector */}
                <div className="form-group with-unit-select">
                  <label>
                    Waist <span className="optional-badge">optional</span>
                  </label>
                  <div className="input-with-unit">
                    {waistUnit === 'cm' ? (
                      <input
                        type="number"
                        step="0.1"
                        value={lifestyleData.waist_circumference}
                        onChange={(e) => handleInputChange('waist_circumference', e.target.value)}
                        placeholder="90"
                      />
                    ) : (
                      <input
                        type="number"
                        step="0.1"
                        value={lifestyleData.waist_inches}
                        onChange={(e) => handleInputChange('waist_inches', e.target.value)}
                        placeholder="35"
                      />
                    )}
                    <select
                      value={waistUnit}
                      onChange={(e) => setWaistUnit(e.target.value)}
                      className="unit-selector"
                    >
                      <option value="cm">cm</option>
                      <option value="in">in</option>
                    </select>
                  </div>
                  <span className="field-hint">At belly button level</span>
                </div>

                {/* BMI Display */}
                <div className="form-group bmi-display">
                  <label>BMI (calculated)</label>
                  <div className="calculated-value">
                    {lifestyleData.bmi ? (
                      <>
                        <span className="bmi-value">{lifestyleData.bmi}</span>
                        <span className="bmi-category">
                          {lifestyleData.bmi < 18.5 ? 'Underweight' :
                           lifestyleData.bmi < 25 ? 'Normal' :
                           lifestyleData.bmi < 30 ? 'Overweight' :
                           'Obese'}
                        </span>
                      </>
                    ) : (
                      <span className="placeholder-text">Enter height & weight</span>
                    )}
                  </div>
                </div>
              </div>
                  </motion.div>
                )}

                {/* Medical Data Tab */}
                {activeTab === 'medical' && (
                  <motion.div
                    key="medical"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
              <div className="form-section-header">
                <Heart size={20} />
                <h3>Blood Pressure</h3>
              </div>
              <div className="form-grid">
                <div className="form-group">
                  <label>
                    Systolic BP (mmHg)
                    <span className="optional-badge">optional</span>
                  </label>
                  <input
                    type="number"
                    value={lifestyleData.systolic_bp}
                    onChange={(e) => handleInputChange('systolic_bp', e.target.value)}
                    placeholder="120"
                    style={{
                      borderColor: inputErrors.systolic_bp ? '#FF5722' : '',
                      backgroundColor: inputErrors.systolic_bp ? '#FFF5F5' : ''
                    }}
                  />
                  {inputErrors.systolic_bp ? (
                    <span className="field-error" style={{ color: '#FF5722', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                      {inputErrors.systolic_bp}
                    </span>
                  ) : (
                    <span className="field-hint">Top number (normal: 90-120)</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    Diastolic BP (mmHg)
                    <span className="optional-badge">optional</span>
                  </label>
                  <input
                    type="number"
                    value={lifestyleData.diastolic_bp}
                    onChange={(e) => handleInputChange('diastolic_bp', e.target.value)}
                    placeholder="80"
                    style={{
                      borderColor: inputErrors.diastolic_bp ? '#FF5722' : '',
                      backgroundColor: inputErrors.diastolic_bp ? '#FFF5F5' : ''
                    }}
                  />
                  {inputErrors.diastolic_bp ? (
                    <span className="field-error" style={{ color: '#FF5722', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                      {inputErrors.diastolic_bp}
                    </span>
                  ) : (
                    <span className="field-hint">Bottom number (normal: 60-80)</span>
                  )}
                </div>
              </div>

              {/* Lab Results */}
              <div className="form-section-header">
                <Activity size={20} />
                <h3>Lab Results (if available)</h3>
              </div>
              <div className="form-grid">
                <div className="form-group">
                  <label>
                    HbA1c (%)
                    <span className="info-tooltip" title="Glycated hemoglobin - 3 month average blood sugar">
                      <Info size={14} />
                    </span>
                    <span className="optional-badge">optional</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={lifestyleData.HbA1c}
                    onChange={(e) => handleInputChange('HbA1c', e.target.value)}
                    placeholder="5.5"
                    style={{
                      borderColor: inputErrors.HbA1c ? '#FF5722' : '',
                      backgroundColor: inputErrors.HbA1c ? '#FFF5F5' : ''
                    }}
                  />
                  {inputErrors.HbA1c ? (
                    <span className="field-error" style={{ color: '#FF5722', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                      {inputErrors.HbA1c}
                    </span>
                  ) : (
                    <span className="field-hint">Normal: &lt;5.7%, Pre-diabetes: 5.7-6.4%, Diabetes: ≥6.5%</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    Blood Glucose (mg/dL)
                    <span className="info-tooltip" title="Fasting blood sugar level">
                      <Info size={14} />
                    </span>
                    <span className="optional-badge">optional</span>
                  </label>
                  <input
                    type="number"
                    value={lifestyleData.blood_glucose}
                    onChange={(e) => handleInputChange('blood_glucose', e.target.value)}
                    placeholder="95"
                  />
                  <span className="field-hint">Normal: 70-100, Pre-diabetes: 100-125, Diabetes: ≥126</span>
                </div>

                <div className="form-group">
                  <label>
                    HDL Cholesterol (mg/dL)
                    <span className="info-tooltip" title="Good cholesterol">
                      <Info size={14} />
                    </span>
                    <span className="optional-badge">optional</span>
                  </label>
                  <input
                    type="number"
                    value={lifestyleData.hdl_cholesterol}
                    onChange={(e) => handleInputChange('hdl_cholesterol', e.target.value)}
                    placeholder="50"
                  />
                  <span className="field-hint">Higher is better (normal: 40-60)</span>
                </div>

                <div className="form-group">
                  <label>
                    Total Cholesterol (mg/dL)
                    <span className="info-tooltip" title="Total cholesterol level">
                      <Info size={14} />
                    </span>
                    <span className="optional-badge">optional</span>
                  </label>
                  <input
                    type="number"
                    value={lifestyleData.total_cholesterol}
                    onChange={(e) => handleInputChange('total_cholesterol', e.target.value)}
                    placeholder="200"
                  />
                  <span className="field-hint">Desirable: &lt;200, Borderline: 200-239, High: ≥240</span>
                </div>
              </div>

              {/* Medical History */}
              <div className="form-section-header">
                <Heart size={20} />
                <h3>Medical History</h3>
              </div>
              <div className="checkbox-group modern">
                <label className="checkbox-card">
                  <input
                    type="checkbox"
                    checked={lifestyleData.has_hypertension}
                    onChange={(e) => handleInputChange('has_hypertension', e.target.checked)}
                  />
                  <div className="checkbox-content">
                    <span className="checkbox-title">High Blood Pressure</span>
                    <span className="checkbox-subtitle">Diagnosed hypertension</span>
                  </div>
                </label>

                <label className="checkbox-card">
                  <input
                    type="checkbox"
                    checked={lifestyleData.takes_cholesterol_med}
                    onChange={(e) => handleInputChange('takes_cholesterol_med', e.target.checked)}
                  />
                  <div className="checkbox-content">
                    <span className="checkbox-title">Cholesterol Medication</span>
                    <span className="checkbox-subtitle">Taking statins or similar</span>
                  </div>
                </label>

                <label className="checkbox-card">
                  <input
                    type="checkbox"
                    checked={lifestyleData.family_diabetes_history}
                    onChange={(e) => handleInputChange('family_diabetes_history', e.target.checked)}
                  />
                  <div className="checkbox-content">
                    <span className="checkbox-title">Family History</span>
                    <span className="checkbox-subtitle">Diabetes in immediate family</span>
                  </div>
                </label>
              </div>
                  </motion.div>
                )}

                {/* Lifestyle & Habits Tab */}
                {activeTab === 'lifestyle' && (
                  <motion.div
                    key="lifestyle"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
              <div className="form-section-header">
                <Coffee size={20} />
                <h3>Lifestyle & Habits</h3>
              </div>
              <div className="form-grid">
                <div className="form-group">
                  <label>
                    <Cigarette size={16} />
                    Smoking Status
                  </label>
                  <select
                    value={lifestyleData.smoking}
                    onChange={(e) => handleInputChange('smoking', e.target.value)}
                    className="select-input"
                  >
                    <option value="no">Non-smoker</option>
                    <option value="yes">Current smoker</option>
                    <option value="former">Former smoker</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>
                    <Coffee size={16} />
                    Alcohol Consumption
                  </label>
                  <select
                    value={lifestyleData.alcohol}
                    onChange={(e) => handleInputChange('alcohol', e.target.value)}
                    className="select-input"
                  >
                    <option value="no">None</option>
                    <option value="moderate">Moderate (1-2 drinks/day)</option>
                    <option value="heavy">Heavy (3+ drinks/day)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>
                    <Dumbbell size={16} />
                    Physical Activity (min/week) <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    value={lifestyleData.physical_activity}
                    onChange={(e) => handleInputChange('physical_activity', e.target.value)}
                    placeholder="150"
                    required
                    style={{
                      borderColor: inputErrors.physical_activity ? '#FF5722' : '',
                      backgroundColor: inputErrors.physical_activity ? '#FFF5F5' : ''
                    }}
                  />
                  {inputErrors.physical_activity ? (
                    <span className="field-error" style={{ color: '#FF5722', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                      {inputErrors.physical_activity}
                    </span>
                  ) : (
                    <span className="field-hint">WHO recommends 150+ min/week</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <Moon size={16} />
                    Sleep Hours (per night) <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={lifestyleData.sleep_hours}
                    onChange={(e) => handleInputChange('sleep_hours', e.target.value)}
                    placeholder="7"
                    required
                    style={{
                      borderColor: inputErrors.sleep_hours ? '#FF5722' : '',
                      backgroundColor: inputErrors.sleep_hours ? '#FFF5F5' : ''
                    }}
                  />
                  {inputErrors.sleep_hours ? (
                    <span className="field-error" style={{ color: '#FF5722', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                      {inputErrors.sleep_hours}
                    </span>
                  ) : (
                    <span className="field-hint">Adults need 7-9 hours</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <Brain size={16} />
                    Stress Level
                  </label>
                  <select
                    value={lifestyleData.stress_level}
                    onChange={(e) => handleInputChange('stress_level', e.target.value)}
                    className="select-input"
                  >
                    <option value="low">Low</option>
                    <option value="moderate">Moderate</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>
                    <Apple size={16} />
                    Diet Quality
                  </label>
                  <select
                    value={lifestyleData.diet_quality}
                    onChange={(e) => handleInputChange('diet_quality', e.target.value)}
                    className="select-input"
                  >
                    <option value="poor">Poor (fast food, processed)</option>
                    <option value="average">Average (mixed)</option>
                    <option value="good">Good (balanced, healthy)</option>
                  </select>
                </div>
              </div>
                  </motion.div>
                )}
              </div>

              <div className="form-note">
                <Info size={16} />
                <span>Fields marked with * are required. Optional fields help improve accuracy.</span>
              </div>

              <div className="button-group">
                <button className="back-button" onClick={() => setStep(1)}>
                  Back
                </button>
                <button
                  className="next-button"
                  onClick={() => setStep(3)}
                  disabled={!lifestyleData.age || !lifestyleData.height_cm || !lifestyleData.weight_kg || !lifestyleData.physical_activity || !lifestyleData.sleep_hours}
                >
                  Next
                  <ArrowRight size={20} />
                </button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="form-section glass"
            >
              <h2>Review Your Information</h2>
              <p className="section-description">
                Verify your details before running the multimodal AI analysis.
              </p>

              <div className="review-grid-full">
                <div className="review-card">
                  <h3>Retinal Image</h3>
                  {imagePreview && (
                    <div className="review-image">
                      <img src={imagePreview} alt="Retinal" />
                    </div>
                  )}
                </div>

                <div className="review-card">
                  <h3>Demographics</h3>
                  <div className="review-data">
                    <div className="review-item">
                      <span>Gender:</span>
                      <strong>{lifestyleData.gender === 'male' ? 'Male' : 'Female'}</strong>
                    </div>
                    <div className="review-item">
                      <span>Age:</span>
                      <strong>{lifestyleData.age} years</strong>
                    </div>
                  </div>
                </div>

                <div className="review-card">
                  <h3>Body Measurements</h3>
                  <div className="review-data">
                    <div className="review-item">
                      <span>Height:</span>
                      <strong>{lifestyleData.height_cm} cm</strong>
                    </div>
                    <div className="review-item">
                      <span>Weight:</span>
                      <strong>{lifestyleData.weight_kg} kg</strong>
                    </div>
                    <div className="review-item highlight">
                      <span>BMI:</span>
                      <strong>{lifestyleData.bmi}</strong>
                    </div>
                    {lifestyleData.waist_circumference && (
                      <div className="review-item">
                        <span>Waist:</span>
                        <strong>{lifestyleData.waist_circumference} cm</strong>
                      </div>
                    )}
                  </div>
                </div>

                {(lifestyleData.systolic_bp || lifestyleData.diastolic_bp ||
                  lifestyleData.HbA1c || lifestyleData.hdl_cholesterol) && (
                  <div className="review-card">
                    <h3>Clinical Data</h3>
                    <div className="review-data">
                      {lifestyleData.systolic_bp && (
                        <div className="review-item">
                          <span>Blood Pressure:</span>
                          <strong>{lifestyleData.systolic_bp}/{lifestyleData.diastolic_bp || '?'} mmHg</strong>
                        </div>
                      )}
                      {lifestyleData.HbA1c && (
                        <div className="review-item">
                          <span>HbA1c:</span>
                          <strong>{lifestyleData.HbA1c}%</strong>
                        </div>
                      )}
                      {lifestyleData.hdl_cholesterol && (
                        <div className="review-item">
                          <span>HDL Cholesterol:</span>
                          <strong>{lifestyleData.hdl_cholesterol} mg/dL</strong>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="review-card">
                  <h3>Medical History</h3>
                  <div className="review-data">
                    <div className="review-item">
                      <span>Hypertension:</span>
                      <strong className={lifestyleData.has_hypertension ? 'text-warning' : 'text-success'}>
                        {lifestyleData.has_hypertension ? 'Yes' : 'No'}
                      </strong>
                    </div>
                    <div className="review-item">
                      <span>Cholesterol Med:</span>
                      <strong className={lifestyleData.takes_cholesterol_med ? 'text-warning' : 'text-success'}>
                        {lifestyleData.takes_cholesterol_med ? 'Yes' : 'No'}
                      </strong>
                    </div>
                    <div className="review-item">
                      <span>Family History:</span>
                      <strong className={lifestyleData.family_diabetes_history ? 'text-warning' : 'text-success'}>
                        {lifestyleData.family_diabetes_history ? 'Yes' : 'No'}
                      </strong>
                    </div>
                  </div>
                </div>

                <div className="review-card">
                  <h3>Lifestyle & Habits</h3>
                  <div className="review-data">
                    <div className="review-item">
                      <span>Smoking:</span>
                      <strong className={lifestyleData.smoking !== 'no' ? 'text-warning' : 'text-success'}>
                        {lifestyleData.smoking === 'no' ? 'Non-smoker' :
                         lifestyleData.smoking === 'yes' ? 'Current smoker' : 'Former smoker'}
                      </strong>
                    </div>
                    <div className="review-item">
                      <span>Alcohol:</span>
                      <strong className={lifestyleData.alcohol === 'heavy' ? 'text-warning' :
                                       lifestyleData.alcohol === 'no' ? 'text-success' : ''}>
                        {lifestyleData.alcohol === 'no' ? 'None' :
                         lifestyleData.alcohol === 'moderate' ? 'Moderate' : 'Heavy'}
                      </strong>
                    </div>
                    <div className="review-item">
                      <span>Physical Activity:</span>
                      <strong className={parseInt(lifestyleData.physical_activity) < 150 ? 'text-warning' : 'text-success'}>
                        {lifestyleData.physical_activity || 0} min/week
                      </strong>
                    </div>
                    <div className="review-item">
                      <span>Sleep:</span>
                      <strong className={parseFloat(lifestyleData.sleep_hours) < 7 || parseFloat(lifestyleData.sleep_hours) > 9 ? 'text-warning' : 'text-success'}>
                        {lifestyleData.sleep_hours || 0} hours/night
                      </strong>
                    </div>
                    <div className="review-item">
                      <span>Stress Level:</span>
                      <strong className={lifestyleData.stress_level === 'high' ? 'text-warning' :
                                       lifestyleData.stress_level === 'low' ? 'text-success' : ''}>
                        {lifestyleData.stress_level === 'low' ? 'Low' :
                         lifestyleData.stress_level === 'moderate' ? 'Moderate' : 'High'}
                      </strong>
                    </div>
                    <div className="review-item">
                      <span>Diet Quality:</span>
                      <strong className={lifestyleData.diet_quality === 'poor' ? 'text-warning' :
                                       lifestyleData.diet_quality === 'good' ? 'text-success' : ''}>
                        {lifestyleData.diet_quality === 'poor' ? 'Poor' :
                         lifestyleData.diet_quality === 'average' ? 'Average' : 'Good'}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>

              <div className="button-group">
                <button className="back-button" onClick={() => setStep(2)}>
                  Back
                </button>
                <button
                  className="analyze-button"
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader className="spinner" size={20} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Run AI Analysis
                      <ArrowRight size={20} />
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Retinal Image Confirmation Modal - Outside container for proper z-index */}
      <AnimatePresence>
        {showRetinalConfirmModal && (
          <motion.div
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={cancelRetinalImage}
          >
            <motion.div
              className="modal-content retinal-confirm-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button className="modal-close" onClick={cancelRetinalImage}>
                <X size={20} />
              </button>

              <div className="modal-header">
                <div className="modal-icon">
                  <Eye size={32} />
                </div>
                <h3>Confirm Retinal Image</h3>
              </div>

              <div className="modal-body">
                {pendingImagePreview && (
                  <div className="preview-container">
                    <img src={pendingImagePreview} alt="Uploaded preview" />
                  </div>
                )}

                <div className="warning-box">
                  <AlertTriangle size={20} />
                  <div>
                    <p className="warning-title">Is this a retinal fundus image?</p>
                    <p className="warning-text">
                      This tool is designed for retinal fundus images taken with specialized eye cameras.
                      Regular camera photos will not produce accurate results.
                    </p>
                  </div>
                </div>

                <div className="info-box">
                  <strong>Retinal images should show:</strong>
                  <ul>
                    <li>Circular view of the back of the eye</li>
                    <li>Blood vessels radiating from the center</li>
                    <li>Optic disc (bright spot) and macula visible</li>
                    <li>Red/orange coloration</li>
                  </ul>
                </div>
              </div>

              <div className="modal-actions">
                <button className="btn-cancel" onClick={cancelRetinalImage}>
                  <X size={18} />
                  Cancel - Choose Different Image
                </button>
                <button className="btn-confirm" onClick={confirmRetinalImage}>
                  <Eye size={18} />
                  Yes, This is a Retinal Image
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default AnalysisPage
