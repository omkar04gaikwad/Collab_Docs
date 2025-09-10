# Development Setup Guide

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: At least 10GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

### Required Software

#### 1. Docker and Docker Compose
```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version
```

#### 2. Node.js and npm
```bash
# Install Node.js 18+ (LTS recommended)
# Download from: https://nodejs.org/

# Verify installation
node --version
npm --version
```

#### 3. Python 3.11+
```bash
# Install Python 3.11+
# Download from: https://www.python.org/downloads/

# Verify installation
python --version
pip --version
```

#### 4. Git
```bash
# Install Git
# Download from: https://git-scm.com/downloads

# Verify installation
git --version
```

#### 5. Database Tools (Optional)
- **PostgreSQL Client**: pgAdmin or DBeaver
- **Redis Client**: RedisInsight or Redis Commander

## Project Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd collaborative-docs
```

### 2. Environment Configuration

#### Create Environment Files
```bash
# Backend environment
cp backend/.env.example backend/.env

# Frontend environment
cp frontend/web/.env.example frontend/web/.env.local
```

#### Backend Environment Variables
```bash
# backend/.env
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/collaborative_docs_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-development-jwt-secret-key-here
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
FILE_UPLOAD_PATH=./uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,application/pdf
```

#### Frontend Environment Variables
```bash
# frontend/web/.env.local
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8001
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0
```

### 3. Database Setup

#### Start Development Databases
```bash
# Start PostgreSQL and Redis using Docker Compose
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for databases to be ready
docker-compose -f docker-compose.dev.yml logs postgres
docker-compose -f docker-compose.dev.yml logs redis
```

#### Run Database Migrations
```bash
cd backend
python -m alembic upgrade head
```

#### Seed Development Data (Optional)
```bash
cd backend
python scripts/seed_data.py
```

### 4. Backend Setup

#### Install Python Dependencies
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Backend Requirements
```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
redis==5.0.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

#### Start Backend Services
```bash
# Terminal 1: Start API server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start WebSocket server
cd backend
python websocket_server.py --reload --host 0.0.0.0 --port 8001
```

### 5. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend/web

# Install dependencies
npm install

# Start development server
npm start
```

#### Frontend Package.json
```json
{
  "name": "collaborative-docs-web",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",
    "quill": "^1.3.7",
    "react-quill": "^2.0.0",
    "@mui/material": "^5.14.0",
    "@mui/icons-material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.47.0",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.45.0",
    "eslint-plugin-react": "^7.33.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "typescript": "^5.0.0",
    "react-scripts": "5.0.1"
  }
}
```

## Development Workflow

### 1. Code Structure
```
collaborative-docs/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── config.py               # Configuration settings
│   │   ├── database.py             # Database connection
│   │   ├── models/                 # SQLAlchemy models
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── api/                    # API routes
│   │   ├── services/               # Business logic
│   │   ├── crdt/                   # CRDT implementation
│   │   └── utils/                  # Utility functions
│   ├── websocket_server.py         # WebSocket server
│   ├── requirements.txt
│   ├── alembic/                    # Database migrations
│   └── tests/                      # Test files
├── frontend/
│   ├── web/
│   │   ├── src/
│   │   │   ├── components/         # React components
│   │   │   ├── pages/              # Page components
│   │   │   ├── hooks/              # Custom hooks
│   │   │   ├── services/           # API services
│   │   │   ├── store/              # State management
│   │   │   ├── utils/              # Utility functions
│   │   │   └── types/              # TypeScript types
│   │   ├── public/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── mobile/                     # React Native app
├── docs/                          # Documentation
├── docker-compose.dev.yml         # Development Docker setup
└── k8s/                           # Kubernetes manifests
```

### 2. Development Commands

#### Backend Commands
```bash
# Start API server with auto-reload
python -m uvicorn main:app --reload

# Start WebSocket server with auto-reload
python websocket_server.py --reload

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# Run linting
flake8 app/
black app/
isort app/

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Create superuser
python scripts/create_superuser.py
```

#### Frontend Commands
```bash
# Start development server
npm start

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Build for production
npm run build

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check
```

### 3. Testing Strategy

#### Backend Testing
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_document():
    response = client.post(
        "/documents",
        json={"title": "Test Document", "content": "Test content"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Document"

def test_websocket_connection():
    with client.websocket_connect("/ws/test-doc") as websocket:
        websocket.send_json({"type": "join_document", "document_id": "test-doc"})
        data = websocket.receive_json()
        assert data["type"] == "joined"
```

#### Frontend Testing
```typescript
// src/components/__tests__/DocumentEditor.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import DocumentEditor from '../DocumentEditor';

describe('DocumentEditor', () => {
  test('renders document editor', () => {
    render(<DocumentEditor documentId="test-doc" />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  test('handles text input', () => {
    render(<DocumentEditor documentId="test-doc" />);
    const editor = screen.getByRole('textbox');
    // Test text input functionality
  });
});
```

### 4. Debugging

#### Backend Debugging
```python
# Enable debug mode in main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Add debug prints
print(f"Debug: {variable}")
```

#### Frontend Debugging
```typescript
// Use React Developer Tools browser extension
// Add debug logs
console.log('Debug:', variable);

// Use debugger statement
debugger;
```

### 5. Code Quality Tools

#### Backend Code Quality
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

#### Frontend Code Quality
```bash
# Install ESLint and Prettier
npm install --save-dev eslint prettier eslint-config-prettier

# .eslintrc.js
module.exports = {
  extends: [
    'react-app',
    'react-app/jest',
    'prettier'
  ],
  rules: {
    'no-unused-vars': 'warn',
    'no-console': 'warn'
  }
};
```

## Development Tools

### 1. IDE Configuration

#### VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-kubernetes-tools.vscode-kubernetes-tools"
  ]
}
```

#### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### 2. Database Management

#### pgAdmin Setup
```bash
# Connect to PostgreSQL
Host: localhost
Port: 5432
Database: collaborative_docs_dev
Username: dev_user
Password: dev_password
```

#### Redis Commander
```bash
# Install Redis Commander
npm install -g redis-commander

# Start Redis Commander
redis-commander --redis-host localhost --redis-port 6379
```

### 3. API Testing

#### Postman Collection
```json
{
  "info": {
    "name": "Collaborative Docs API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register User",
          "request": {
            "method": "POST",
            "header": [],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"password123\",\n  \"name\": \"Test User\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register",
              "host": ["{{base_url}}"],
              "path": ["auth", "register"]
            }
          }
        }
      ]
    }
  ]
}
```

### 4. Monitoring and Logging

#### Development Logging
```python
# backend/app/config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Check database logs
docker-compose -f docker-compose.dev.yml logs postgres

# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgres redis
```

#### 2. Redis Connection Issues
```bash
# Check if Redis is running
docker-compose -f docker-compose.dev.yml ps redis

# Test Redis connection
redis-cli -h localhost -p 6379 ping
```

#### 3. Port Conflicts
```bash
# Check if ports are in use
netstat -an | grep :8000
netstat -an | grep :8001
netstat -an | grep :3000

# Kill processes using ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

#### 4. Python Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf backend/venv
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 5. Node.js Dependencies Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Performance Optimization

#### Backend Performance
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)

# Enable Redis caching
import redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
```

#### Frontend Performance
```typescript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
});

// Use useMemo for expensive calculations
const expensiveValue = useMemo(() => {
  return expensiveCalculation(data);
}, [data]);
```

## Contributing Guidelines

### 1. Code Style
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write meaningful commit messages
- Add tests for new features
- Update documentation

### 2. Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### 3. Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request
7. Address review feedback
8. Merge when approved

## Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

### Learning Resources
- [CRDT Research Papers](https://crdt.tech/)
- [WebSocket RFC](https://tools.ietf.org/html/rfc6455)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
