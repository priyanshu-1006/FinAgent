# 🚀 FinAgent Deployment Guide

This guide covers multiple deployment options for FinAgent.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
   - [Azure Container Apps](#azure-container-apps)
   - [AWS ECS/Fargate](#aws-ecsfargate)
   - [Google Cloud Run](#google-cloud-run)
   - [Railway/Render](#railwayrender)
5. [Production Checklist](#production-checklist)
6. [Monitoring & Logging](#monitoring--logging)

---

## Prerequisites

- Docker & Docker Compose installed
- Python 3.10+ (for local development)
- Node.js 18+ (for dummy bank)
- Gemini API Key (free at https://aistudio.google.com/app/apikey)

---

## Local Development

### 1. Clone and Setup

```bash
# Clone repository
git clone https://github.com/your-repo/finagent.git
cd finagent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required: GEMINI_API_KEY
```

### 3. Start Services

```bash
# Terminal 1: Start dummy bank
cd src/dummy-bank
npm install
npm run dev

# Terminal 2: Start FinAgent
python main.py server
```

### 4. Access Dashboard

Open http://localhost:8000 in your browser.

---

## Docker Deployment

### Quick Start (Development)

```bash
# Build and start all services
docker-compose up --build

# Access:
# - FinAgent Dashboard: http://localhost:8000
# - Dummy Bank: http://localhost:8080
```

### Production Mode

```bash
# Start with production profile (includes Nginx, Redis)
docker-compose --profile production up -d

# View logs
docker-compose logs -f finagent-api

# Stop all services
docker-compose down
```

### Individual Container Build

```bash
# Build FinAgent API
docker build -t finagent-api:latest .

# Run standalone
docker run -d \
  --name finagent \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key_here \
  -e HEADLESS=true \
  -e BANK_URL=http://your-bank-url \
  finagent-api:latest
```

---

## Cloud Deployment Options

### Azure Container Apps

**Best for**: Easy scaling, serverless containers

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name finagent-rg --location eastus

# 3. Create Container Apps environment
az containerapp env create \
  --name finagent-env \
  --resource-group finagent-rg \
  --location eastus

# 4. Deploy FinAgent
az containerapp create \
  --name finagent-api \
  --resource-group finagent-rg \
  --environment finagent-env \
  --image ghcr.io/your-repo/finagent:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 5 \
  --secrets gemini-key=your_api_key \
  --env-vars \
    GEMINI_API_KEY=secretref:gemini-key \
    HEADLESS=true \
    ENVIRONMENT=production
```

**Estimated cost**: ~$20-50/month for basic usage

---

### AWS ECS/Fargate

**Best for**: AWS ecosystem, enterprise features

#### 1. Create ECR Repository

```bash
# Create repository
aws ecr create-repository --repository-name finagent

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t finagent .
docker tag finagent:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finagent:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finagent:latest
```

#### 2. Create Task Definition (`task-definition.json`)

```json
{
  "family": "finagent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "finagent-api",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finagent:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "HEADLESS", "value": "true"},
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "secrets": [
        {
          "name": "GEMINI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:finagent/gemini-key"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/finagent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Deploy

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster your-cluster \
  --service-name finagent \
  --task-definition finagent \
  --desired-count 1 \
  --launch-type FARGATE
```

**Estimated cost**: ~$30-80/month for basic usage

---

### Google Cloud Run

**Best for**: Simplest deployment, pay-per-use

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/finagent

# 2. Deploy to Cloud Run
gcloud run deploy finagent \
  --image gcr.io/YOUR_PROJECT/finagent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars "HEADLESS=true,ENVIRONMENT=production" \
  --set-secrets "GEMINI_API_KEY=gemini-key:latest"
```

**Estimated cost**: ~$10-30/month (pay-per-request)

---

### Railway/Render (Easiest)

**Best for**: Quick deployment, hobby projects

#### Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up

# 3. Set environment variables in Railway dashboard
# Add: GEMINI_API_KEY, HEADLESS=true
```

#### Render

1. Connect your GitHub repository to Render
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt && playwright install chromium`
4. Set start command: `python -m uvicorn src.backend.server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard

**Estimated cost**: Free tier available, ~$7/month for always-on

---

## Production Checklist

### Security

- [ ] Set `HEADLESS=true` in production
- [ ] Generate secure `SECRET_KEY` using `openssl rand -hex 32`
- [ ] Store API keys in secrets manager (not environment variables)
- [ ] Enable HTTPS (TLS/SSL)
- [ ] Configure CORS origins properly
- [ ] Enable rate limiting
- [ ] Remove default credentials from code

### Performance

- [ ] Set `SLOW_MO=0` for production
- [ ] Configure proper resource limits (CPU/Memory)
- [ ] Enable response caching where appropriate
- [ ] Use Redis for session storage in multi-instance deployments

### Reliability

- [ ] Configure health checks
- [ ] Set up automatic restarts
- [ ] Configure logging to external service
- [ ] Set up error alerting (Sentry, PagerDuty, etc.)
- [ ] Enable auto-scaling based on load

### Monitoring

- [ ] Set up application logging
- [ ] Configure metrics collection
- [ ] Create dashboards for key metrics
- [ ] Set up uptime monitoring

---

## Monitoring & Logging

### Recommended Stack

| Service | Purpose | Cost |
|---------|---------|------|
| **Sentry** | Error tracking | Free tier available |
| **Datadog** | APM & Logs | ~$15/host/month |
| **Grafana Cloud** | Metrics & Dashboards | Free tier available |
| **UptimeRobot** | Uptime monitoring | Free tier available |

### Adding Sentry

```bash
pip install sentry-sdk[fastapi]
```

```python
# In server.py
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    environment=os.getenv("ENVIRONMENT", "development"),
    traces_sample_rate=0.1,
)
```

### Prometheus Metrics

```python
# Add to requirements.txt
prometheus-fastapi-instrumentator

# In server.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## Troubleshooting

### Browser Fails to Start in Container

```bash
# Ensure Playwright dependencies are installed
playwright install-deps chromium

# Check if running as non-root user
docker exec -it finagent-api whoami
```

### Vision API Rate Limits

- Add multiple API keys in `.env` for automatic rotation
- Implement caching for repeated element lookups
- Consider upgrading to paid tier for higher limits

### WebSocket Connection Drops

- Configure proper timeouts in reverse proxy
- Enable sticky sessions for load balancers
- Add WebSocket reconnection logic in frontend

---

## Support

- 📖 Documentation: [docs/](./docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/finagent/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-repo/finagent/discussions)
