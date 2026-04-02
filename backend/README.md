# Diabetes Detection AI - Backend

Multimodal AI framework for early diabetes detection using agentic architecture.

## Features

- **Retinal Image Analysis**: CNN-based diabetic retinopathy detection
- **Lifestyle Risk Prediction**: Gradient Boosting model for demographic/behavioral risk assessment
- **Multimodal Fusion**: Optimized weight fusion combining retinal and lifestyle predictions
- **LLM-Powered Advice**: Personalized recommendations using Groq AI
- **What-If Simulations**: Interactive scenarios showing impact of lifestyle changes
- **Agentic Architecture**: Autonomous AI agents coordinating multimodal analysis

## Architecture

```
Backend (Agentic AI)
│
├── Orchestrator Agent (Master coordinator)
│   │
│   ├── Retinal Agent (CNN analysis)
│   ├── Lifestyle Agent (Gradient Boosting prediction)
│   ├── Fusion Agent (Multimodal integration)
│   ├── LLM Agent (Groq AI advice)
│   └── Simulation Agent (What-if scenarios)
│
└── REST API (Flask)
```

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
OR

```bash
cd backend
docker build -t diabetics-pred-backend . 
docker run -p 5000:5000 --name diabetics-backend diabetics-pred-backend                                                                                                                                                        │
```

### 2. Configure Environment

Edit `.env` file with your API keys:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /health
```

### Retinal Analysis
```
POST /api/retinal/analyze
Content-Type: multipart/form-data
Body: image (file)
```

### Lifestyle Prediction
```
POST /api/lifestyle/predict
Content-Type: application/json
Body: {
  "age": 45,
  "bmi": 28.5,
  "physical_activity": 120,
  "sleep_hours": 6.5,
  "family_history": true,
  "smoking": false
}
```

### Complete Analysis (Recommended)
```
POST /api/advice/complete-analysis
Content-Type: multipart/form-data
Body:
  - image (file)
  - lifestyle_data (JSON string)
```

### Simulations
```
POST /api/simulation/create
Content-Type: application/json
Body: {
  "risk_score": 0.65,
  "lifestyle_data": {...},
  "risk_factors": [...]
}
```

## Project Structure

```
backend/
├── agents/                 # Agentic AI components
│   ├── orchestrator.py     # Master coordinator
│   ├── retinal_agent.py    # Retinal analysis agent
│   ├── lifestyle_agent.py  # Lifestyle prediction agent
│   ├── llm_agent.py        # LLM advice agent
│   ├── fusion_agent.py     # Multimodal fusion agent
│   └── simulation_agent.py # What-if simulation agent
│
├── models/                 # AI/ML models
│   ├── retinal/            # CNN models
│   ├── lifestyle/          # Gradient Boosting models
│   ├── llm/                # LLM interface
│   └── fusion/             # Fusion logic
│       ├── ensemble.py     # Weighted fusion with optimized weights
│       ├── weight_optimizer.py # Gradient descent weight optimization
│       └── optimal_weights.json # Cross-validated optimal weights
│
├── api/                    # REST API routes
│   ├── routes.py           # Route registration
│   ├── retinal_routes.py   # Retinal endpoints
│   ├── lifestyle_routes.py # Lifestyle endpoints
│   ├── advice_routes.py    # Advice endpoints
│   └── simulation_routes.py # Simulation endpoints
│
├── utils/                  # Utilities
│   └── logger.py           # Logging configuration
│
├── app.py                  # Flask application
├── config.py               # Configuration
└── requirements.txt        # Dependencies
```

## Multimodal Fusion

The system uses optimized weight fusion to combine retinal and lifestyle predictions:

### Weight Optimization
- **Method**: Cross-validated gradient descent with L-BFGS-B optimization
- **Constraint**: w1 + w2 = 1 (weighted average)
- **Current Weights**:
  - Retinal: 10.3%
  - Lifestyle: 89.7%
- **Loss**: 0.027 (MSE + L2 regularization)

### Training Fusion Weights
```bash
python train_fusion_weights.py
```

This will:
1. Generate/load training data with ground truth labels
2. Optimize weights using gradient descent and scipy
3. Cross-validate across 5 folds
4. Save optimal weights to `models/fusion/optimal_weights.json`

### Fusion Process
```python
# Runtime: Weights are loaded from JSON
fused_score = w1 * retinal_risk + w2 * lifestyle_risk
# Example: 0.103 * 0.7 + 0.897 * 0.3 = 0.341
```

## Development

### Adding a New Agent

1. Create agent class inheriting from `BaseAgent`
2. Implement `execute()` method
3. Add agent to orchestrator
4. Create API route if needed

### Running Tests

```bash
pytest tests/
```

## Performance Targets

- Retinal Analysis: >90% sensitivity
- Lifestyle Prediction: AUC >0.85
- Processing Time: <2s per request
- LLM Advice Relevance: >85%

## License

Research project for diabetes prevention

## Author

L.M. Radith Dinusitha
Informatics Institute of Technology
