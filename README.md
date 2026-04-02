# Diabetes Prediction Application

A comprehensive diabetes detection and prediction application with machine learning backend and React frontend.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Groq API key for AI features

### Setup Instructions

1. **Create environment file:**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

2. **Option A: Use the startup script (Recommended if docker-compose has issues):**
```bash
# Make script executable
chmod +x start-docker.sh

# Run the startup script
./start-docker.sh
```

3. **Option B: Start with Docker Compose:**
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

**Note:** If you encounter iptables/networking errors with docker-compose, use the `start-docker.sh` script instead.

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
- PostgreSQL: Port 5433

## 📋 Individual Docker Commands

### Option 1: Run PostgreSQL Database
```bash
docker run -d --name diabetes-postgres \
    -e POSTGRES_USER=diabetesapp \
    -e POSTGRES_PASSWORD=diabetesapp123 \
    -e POSTGRES_DB=diabetes_db \
    -p 5433:5432 \
    -v diabetes_postgres_data:/var/lib/postgresql/data \
    postgres:15-alpine
```

### Option 2: Build and Run Backend
```bash
# Build backend image
cd backend
docker build -t diabetes-backend .

# Run backend container
docker run -d --name diabetes-backend \
    --link diabetes-postgres:postgres \
    -e DATABASE_URL=postgresql://diabetesapp:diabetesapp123@postgres:5432/diabetes_db \
    -e JWT_SECRET_KEY='your-secret-key-change-in-production' \
    -e JWT_ACCESS_TOKEN_EXPIRES=3600 \
    -e FLASK_ENV=production \
    -e DEBUG=False \
    -e PORT=5000 \
    -e CORS_ORIGINS='http://localhost:3000' \
    -e GROQ_API_KEY='your-groq-api-key-here' \
    -e LOG_LEVEL=INFO \
    -p 5001:5000 \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/uploads:/app/uploads" \
    diabetes-backend
```

### Option 3: Build and Run Frontend
```bash
# Build frontend image
cd frontend
docker build -t diabetes-frontend .

# Run frontend container
docker run -d --name diabetes-frontend \
    --link diabetes-backend:backend \
    -p 3000:80 \
    diabetes-frontend
```

## 🛠️ Development Mode

Run backend with Docker and frontend with npm for development:
```bash
# Start backend services
docker-compose up postgres backend

# In another terminal, run frontend dev server
cd frontend
npm install
npm run dev
```

## 📊 Container Management

### Check container status:
```bash
docker ps
```

### View logs:
```bash
docker logs diabetes-backend
docker logs diabetes-frontend
docker logs diabetes-postgres
```

### Stop all containers:
```bash
docker-compose down
```

### Clean up everything:
```bash
docker-compose down -v
docker system prune -a
```

## 🔧 Environment Variables

Required in `.env` file:
```
GROQ_API_KEY=your-actual-api-key-here
```

Optional (have defaults):
```
POSTGRES_USER=diabetesapp
POSTGRES_PASSWORD=diabetesapp123
POSTGRES_DB=diabetes_db
JWT_SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000
```

## 🏥 Features

- **User Authentication**: Secure JWT-based authentication system
- **Diabetes Risk Analysis**: ML-powered prediction model
- **Health Plans**: Personalized health recommendations
- **Progress Tracking**: Monitor health improvements over time
- **Admin Dashboard**: Manage users and system settings
- **AI Recommendations**: Groq-powered health insights

## 📝 API Documentation

Backend API endpoints are available at:
- Health check: `GET /health`
- Authentication: `/api/auth/*`
- Analysis: `/api/analyze/*`
- Results: `/api/results/*`
- Plans: `/api/plans/*`

## 🐛 Troubleshooting

### Backend connection issues:
```bash
# Check if backend is running
docker ps | grep diabetes-backend

# Test health endpoint
curl http://localhost:5001/health
```

### Database connection issues:
```bash
# Check PostgreSQL logs
docker logs diabetes-postgres

# Connect to database
docker exec -it diabetes-postgres psql -U diabetesapp -d diabetes_db
```

### Port conflicts:
If port 5000 is in use, the backend runs on port 5001 by default.

## 📚 Additional Documentation

- [Docker Commands Guide](./DOCKER_COMMANDS.md)
- [Setup Instructions](./SETUP_INSTRUCTIONS.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Authentication Guide](./FRONTEND_AUTH_GUIDE.md)

## 📄 License

This project is licensed under the MIT License.