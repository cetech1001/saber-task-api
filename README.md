# Saber Task API (Production-Ready FastAPI)

A robust, production-ready task management API built with FastAPI, SQLAlchemy, and comprehensive testing. Features include CRUD operations, filtering, pagination, search, health checks, and structured logging.

## 🚀 Features

- **Complete CRUD Operations** for task management
- **Advanced Filtering** by completion status and priority
- **Full-text Search** across title and description
- **Pagination Support** with configurable page sizes
- **Health Check Endpoints** for monitoring
- **Structured Logging** with configurable levels
- **Comprehensive Test Suite** (unit + integration)
- **Docker Support** with multi-stage builds
- **Environment-based Configuration**
- **Production-ready Error Handling**
- **API Documentation** (OpenAPI/Swagger)
- **Database Migrations** with Alembic

## 🏗️ Architecture

```
app/
├── api/v1/endpoints/     # API route handlers
├── crud/                 # Database operations
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic models
├── config.py             # Environment configuration
├── database.py           # Database connection and session management
├── exceptions.py         # Exception handlers
├── logging_config.py     # Logging configuration
└── main.py               # FastAPI application
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and setup
git clone <repository>
cd saber-task-api

# Copy environment template
cp .env.example .env

# Run with Docker Compose
docker-compose up --build

# For development (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Run the application
uvicorn app.main:app --reload
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## 🔧 Configuration

Set these environment variables (see `.env.example`):

```bash
DATABASE_URL=sqlite:///./data/app.db

DEBUG=false
LOG_LEVEL=INFO
API_V1_STR=/api/v1

HOST=0.0.0.0
PORT=8000

ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=50
```

## 🧪 Testing

```bash
# Run all tests
PYTHONPATH=. pytest

# Run with coverage
PYTHONPATH=. pytest --cov=app --cov-report=html

# Run specific test categories
PYTHONPATH=. pytest tests/unit/          # Unit tests only
PYTHONPATH=. pytest tests/integration/   # Integration tests only
```

## 📋 API Endpoints

### Tasks
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/` - List tasks (with filters, search, pagination)
- `GET /api/v1/tasks/{id}/` - Get specific task
- `PUT /api/v1/tasks/{id}/` - Update task
- `DELETE /api/v1/tasks/{id}/` - Delete task
- `GET /api/v1/tasks/summary` - Get task statistics

### Health
- `GET /api/v1/health` - Health check with database connectivity
- `GET /api/v1/health/readiness` - Kubernetes-style readiness probe
- `GET /api/v1/health/liveness` - Kubernetes-style liveness probe

### Query Parameters (GET /tasks/)
- `completed` (bool) - Filter by completion status
- `priority` (int) - Filter by priority (1=High, 2=Medium, 3=Low)
- `q` (string) - Search in title/description
- `page` (int) - Page number (default: 1)
- `size` (int) - Items per page (default: 50, max: 1000)

## 🐳 Docker Deployment

### Production Build
```bash
docker build -t saber-task-api .
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./data/app.db saber-task-api

OR

docker compose up --build
```

### Development with Docker Compose
```bash
# Start with hot reload
docker-compose -f docker-compose-dev.yml up

# View logs
docker-compose logs -f app
```

## 🔍 Monitoring & Logging

- **Structured Logging**: JSON-formatted logs with request/response tracking
- **Health Checks**: Multiple endpoints for different monitoring needs
- **Metrics**: Built-in request timing and status code tracking
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes

## 📈 Performance Features

- **Optimized Database Queries** with proper indexing
- **Request/Response Middleware** for timing
- **Connection Pooling** for database efficiency
- **Pagination** to handle large datasets
- **Health Checks** for uptime monitoring

## 🛡️ Security Features

- **Input Validation** with Pydantic models
- **SQL Injection Protection** via SQLAlchemy
- **CORS Configuration** for cross-origin requests
- **Non-root Docker User** for container security
- **Environment-based Secrets** management

## 📝 Example Requests

```bash
# Create a task
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the FastAPI task management system",
    "priority": 1,
    "due_date": "2024-12-31T23:59:59"
  }'

# List tasks with filters
curl "http://localhost:8000/api/v1/tasks/?completed=false&priority=1&page=1&size=10"

# Search tasks
curl "http://localhost:8000/api/v1/tasks/?q=project&page=1&size=5"

# Get task summary
curl "http://localhost:8000/api/v1/tasks/summary"

# Health check
curl "http://localhost:8000/api/v1/health"
```

## 🏷️ Project Structure Benefits

- **Separation of Concerns**: Clear boundaries between API, business logic, and data layers
- **Scalability**: Modular structure supports growth and team collaboration  
- **Testability**: Comprehensive test coverage with proper mocking
- **Maintainability**: Well-organized code with consistent patterns
- **Production Ready**: Logging, monitoring, and deployment configurations included

Built using FastAPI, SQLAlchemy, and modern Python best practices.
