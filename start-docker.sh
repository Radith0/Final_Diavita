#!/bin/bash

# Stop and remove existing containers
echo "Stopping existing containers..."
docker stop diabetes-postgres diabetes-backend diabetes-frontend 2>/dev/null
docker rm diabetes-postgres diabetes-backend diabetes-frontend 2>/dev/null

# Start PostgreSQL
echo "Starting PostgreSQL..."
docker run -d --name diabetes-postgres \
    -e POSTGRES_USER=diabetesapp \
    -e POSTGRES_PASSWORD=diabetesapp123 \
    -e POSTGRES_DB=diabetes_db \
    -p 5433:5432 \
    -v diabetes_postgres_data:/var/lib/postgresql/data \
    postgres:15-alpine

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 10

# Build and start Backend
echo "Building Backend..."
cd backend
docker build -t diabetes-backend .

echo "Starting Backend..."
docker run -d --name diabetes-backend \
    --link diabetes-postgres:postgres \
    -e DATABASE_URL=postgresql://diabetesapp:diabetesapp123@postgres:5432/diabetes_db \
    -e JWT_SECRET_KEY='your-secret-key-change-in-production' \
    -e JWT_ACCESS_TOKEN_EXPIRES=3600 \
    -e FLASK_ENV=production \
    -e DEBUG=False \
    -e PORT=5000 \
    -e CORS_ORIGINS='http://localhost:3000' \
    -e GROQ_API_KEY="${GROQ_API_KEY:-your-groq-api-key-here}" \
    -e LOG_LEVEL=INFO \
    -p 5001:5000 \
    -v "$(pwd)/logs:/app/logs" \
    -v "$(pwd)/uploads:/app/uploads" \
    diabetes-backend

# Build and start Frontend
echo "Building Frontend..."
cd ../frontend
docker build -t diabetes-frontend .

echo "Starting Frontend..."
docker run -d --name diabetes-frontend \
    --link diabetes-backend:backend \
    -p 3000:80 \
    diabetes-frontend

cd ..

# Show status
echo ""
echo "=== Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep diabetes

echo ""
echo "=== Application URLs ==="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:5001"
echo "PostgreSQL: localhost:5433"

echo ""
echo "=== Checking Services ==="
sleep 5
curl -s http://localhost:5001/health | python3 -m json.tool 2>/dev/null && echo "✓ Backend is healthy" || echo "✗ Backend not ready yet"

echo ""
echo "To view logs: docker logs <container-name>"
echo "To stop all: docker stop diabetes-postgres diabetes-backend diabetes-frontend"