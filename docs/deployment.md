# Deployment Guide

## Overview

This guide covers deployment strategies for the Collaborative Document Editor, including development, staging, and production environments.

## Deployment Architecture

### Production Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                        │
│                    (Nginx/HAProxy/ALB)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    API Gateway                              │
│              (Kong/AWS API Gateway)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
┌─────────┴───┐ ┌─────┴─────┐ ┌───┴─────────┐
│   Web App   │ │   API     │ │  WebSocket  │
│   Service   │ │  Service  │ │   Service   │
└─────────────┘ └───────────┘ └─────────────┘
          │           │           │
          └───────────┼───────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
┌─────────┴───┐ ┌─────┴─────┐ ┌───┴─────────┐
│ PostgreSQL  │ │   Redis   │ │ File Storage│
│  Cluster    │ │  Cluster  │ │   (S3)      │
└─────────────┘ └───────────┘ └─────────────┘
```

## Environment Configurations

### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: collaborative_docs_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/collaborative_docs_dev
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=dev_jwt_secret
      - ENVIRONMENT=development
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  websocket:
    build: ./backend
    command: python websocket_server.py
    environment:
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/collaborative_docs_dev
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=dev_jwt_secret
      - ENVIRONMENT=development
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis

  web:
    build: ./frontend/web
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8001

volumes:
  postgres_data:
  redis_data:
```

### Staging Environment
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: collaborative_docs_staging
      POSTGRES_USER: staging_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://staging_user:${POSTGRES_PASSWORD}@postgres:5432/collaborative_docs_staging
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=staging
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  websocket:
    build: ./backend
    command: python websocket_server.py
    environment:
      - DATABASE_URL=postgresql://staging_user:${POSTGRES_PASSWORD}@postgres:5432/collaborative_docs_staging
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=staging
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Deployment

### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: collaborative-docs
```

### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: collaborative-docs-config
  namespace: collaborative-docs
data:
  DATABASE_URL: "postgresql://user:password@postgres-service:5432/collaborative_docs"
  REDIS_URL: "redis://redis-service:6379"
  JWT_SECRET: "your-jwt-secret"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
```

### Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: collaborative-docs-secrets
  namespace: collaborative-docs
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded-password>
  JWT_SECRET: <base64-encoded-jwt-secret>
  AWS_ACCESS_KEY_ID: <base64-encoded-access-key>
  AWS_SECRET_ACCESS_KEY: <base64-encoded-secret-key>
```

### PostgreSQL Deployment
```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: collaborative-docs
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: collaborative_docs
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: collaborative-docs-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: collaborative-docs
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: collaborative-docs
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### Redis Deployment
```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: collaborative-docs
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--appendonly", "yes"]
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: collaborative-docs
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: collaborative-docs
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### API Service Deployment
```yaml
# k8s/api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: collaborative-docs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
      - name: api
        image: collaborative-docs/api:latest
        envFrom:
        - configMapRef:
            name: collaborative-docs-config
        - secretRef:
            name: collaborative-docs-secrets
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: collaborative-docs
spec:
  selector:
    app: api-service
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### WebSocket Service Deployment
```yaml
# k8s/websocket.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: websocket-service
  namespace: collaborative-docs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: websocket-service
  template:
    metadata:
      labels:
        app: websocket-service
    spec:
      containers:
      - name: websocket
        image: collaborative-docs/websocket:latest
        envFrom:
        - configMapRef:
            name: collaborative-docs-config
        - secretRef:
            name: collaborative-docs-secrets
        ports:
        - containerPort: 8001
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: websocket-service
  namespace: collaborative-docs
spec:
  selector:
    app: websocket-service
  ports:
  - port: 80
    targetPort: 8001
  type: ClusterIP
```

### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: collaborative-docs-ingress
  namespace: collaborative-docs
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/websocket-services: websocket-service
spec:
  tls:
  - hosts:
    - api.collaborative-docs.com
    - ws.collaborative-docs.com
    secretName: collaborative-docs-tls
  rules:
  - host: api.collaborative-docs.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
  - host: ws.collaborative-docs.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: websocket-service
            port:
              number: 80
```

## Docker Configuration

### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
# frontend/web/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
```nginx
# frontend/web/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # API proxy
        location /api/ {
            proxy_pass http://api-service:80/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket proxy
        location /ws/ {
            proxy_pass http://websocket-service:80/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      run: |
        cd frontend/web
        npm ci
    
    - name: Run frontend tests
      run: |
        cd frontend/web
        npm test -- --coverage --watchAll=false

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ secrets.DOCKER_REGISTRY }}
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push backend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: |
          ${{ secrets.DOCKER_REGISTRY }}/collaborative-docs/api:${{ github.sha }}
          ${{ secrets.DOCKER_REGISTRY }}/collaborative-docs/api:latest
    
    - name: Build and push websocket image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: |
          ${{ secrets.DOCKER_REGISTRY }}/collaborative-docs/websocket:${{ github.sha }}
          ${{ secrets.DOCKER_REGISTRY }}/collaborative-docs/websocket:latest
    
    - name: Build and push frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend/web
        push: true
        tags: |
          ${{ secrets.DOCKER_REGISTRY }}/collaborative-docs/web:${{ github.sha }}
          ${{ secrets.DOCKER_REGISTRY }}/collaborative-docs/web:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        # Update image tags in Kubernetes manifests
        sed -i "s|collaborative-docs/api:latest|collaborative-docs/api:${{ github.sha }}|g" k8s/api.yaml
        sed -i "s|collaborative-docs/websocket:latest|collaborative-docs/websocket:${{ github.sha }}|g" k8s/websocket.yaml
        sed -i "s|collaborative-docs/web:latest|collaborative-docs/web:${{ github.sha }}|g" k8s/web.yaml
        
        # Apply Kubernetes manifests
        kubectl apply -f k8s/
    
    - name: Wait for deployment
      run: |
        kubectl rollout status deployment/api-service -n collaborative-docs
        kubectl rollout status deployment/websocket-service -n collaborative-docs
        kubectl rollout status deployment/web-service -n collaborative-docs
```

## Monitoring and Observability

### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-service'
    static_configs:
      - targets: ['api-service:8000']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'websocket-service'
    static_configs:
      - targets: ['websocket-service:8001']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Collaborative Docs Monitoring",
    "panels": [
      {
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "WebSocket Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "websocket_connections_active",
            "legendFormat": "Active Connections"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "{{datname}}"
          }
        ]
      }
    ]
  }
}
```

## Backup and Recovery

### Database Backup Script
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="collaborative_docs"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -h postgres-service -U postgres $DB_NAME | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Backup Redis
redis-cli -h redis-service --rdb $BACKUP_DIR/redis_$DATE.rdb

# Upload to S3
aws s3 cp $BACKUP_DIR/postgres_$DATE.sql.gz s3://collaborative-docs-backups/database/
aws s3 cp $BACKUP_DIR/redis_$DATE.rdb s3://collaborative-docs-backups/redis/

# Clean up old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
```

### Recovery Script
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_NAME="collaborative_docs"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Restore PostgreSQL
gunzip -c $BACKUP_FILE | psql -h postgres-service -U postgres $DB_NAME

echo "Database restored from $BACKUP_FILE"
```

## Security Considerations

### Network Security
- Use TLS/SSL for all communications
- Implement proper firewall rules
- Use private networks for internal communication
- Enable DDoS protection

### Application Security
- Regular security updates
- Container image scanning
- Secrets management
- Input validation and sanitization
- Rate limiting and throttling

### Data Security
- Encryption at rest and in transit
- Regular security audits
- Access logging and monitoring
- Backup encryption
- Data retention policies

## Scaling Strategies

### Horizontal Scaling
- Multiple API service replicas
- Load balancer distribution
- Database read replicas
- Redis cluster setup

### Vertical Scaling
- Resource limits and requests
- Auto-scaling based on metrics
- Performance monitoring
- Capacity planning

### Performance Optimization
- Connection pooling
- Caching strategies
- CDN integration
- Database query optimization
