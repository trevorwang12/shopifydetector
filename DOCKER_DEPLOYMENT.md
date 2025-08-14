# Docker Deployment Guide
## Shopify Theme Detector

**Date**: 2024-08-14  
**Version**: 1.0  
**Status**: Production Ready 🚀

---

## 🎯 Overview

This guide provides comprehensive Docker deployment instructions for the Shopify Theme Detector application. The deployment includes multiple configurations for development, staging, and production environments with nginx reverse proxy, SSL termination, and optional monitoring.

### 📦 What's Included

- **Dockerfile**: Multi-stage build with security best practices
- **docker-compose.yml**: Standard deployment with nginx
- **docker-compose.dev.yml**: Development environment with hot reload
- **docker-compose.prod.yml**: Production environment with monitoring
- **Nginx Configuration**: Reverse proxy with SSL and security headers
- **Monitoring**: Prometheus integration for metrics collection

---

## 🚀 Quick Start

### Prerequisites
```bash
# Required software
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

# Minimum system requirements
- RAM: 512MB available
- Storage: 1GB available
- CPU: 1 core
```

### 1. Clone and Prepare
```bash
# Clone repository
git clone <repository-url>
cd shopifydetector

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Create logs directory
mkdir -p logs/nginx
```

### 2. Development Deployment
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Access application
open http://localhost:5000
```

### 3. Production Deployment
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Access via nginx
open http://localhost
```

---

## 📋 Deployment Options

### Option 1: Simple Development
**Use Case**: Local development with hot reload
```bash
docker-compose -f docker-compose.dev.yml up -d
```
**Features**:
- ✅ Hot reload enabled
- ✅ Debug mode on
- ✅ Volume mounting for live changes
- ✅ Minimal resource usage

### Option 2: Standard Deployment
**Use Case**: Testing and staging environments
```bash
docker-compose up -d
```
**Features**:
- ✅ Nginx reverse proxy
- ✅ Production Flask settings
- ✅ Health checks
- ✅ Basic monitoring

### Option 3: Production Deployment
**Use Case**: Live production environment
```bash
docker-compose -f docker-compose.prod.yml up -d
```
**Features**:
- ✅ SSL termination
- ✅ Advanced security headers
- ✅ Redis caching
- ✅ Prometheus monitoring
- ✅ Resource limits
- ✅ Auto-restart policies

---

## 🔧 Configuration

### Environment Variables

#### Core Application Settings
```bash
# .env file
FLASK_DEBUG=False              # Enable/disable debug mode
FLASK_ENV=production          # Environment type
PORT=5000                     # Application port
SECRET_KEY=your-secret-key    # Flask secret key
```

#### Docker Compose Override
```bash
# Override default settings
export COMPOSE_PROJECT_NAME=shopify-detector
export COMPOSE_FILE=docker-compose.prod.yml
```

### SSL Configuration (Production)
```bash
# Create SSL directory
mkdir -p ssl

# Add your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Update nginx/prod.conf with your domain
sed -i 's/your-domain.com/yourdomain.com/g' nginx/prod.conf
```

---

## 🔒 Security Configuration

### 1. SSL/TLS Setup
```bash
# Generate self-signed certificate for testing
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Or use Let's Encrypt (recommended)
# Install certbot and run:
# certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

### 2. Security Headers
The nginx configuration includes comprehensive security headers:
- **HSTS**: HTTP Strict Transport Security
- **CSP**: Content Security Policy  
- **X-Frame-Options**: Clickjacking protection
- **X-XSS-Protection**: XSS attack prevention

### 3. Rate Limiting
```nginx
# API rate limiting: 10 requests/second
limit_req zone=api burst=5 nodelay;

# General rate limiting: 2 requests/second  
limit_req zone=general burst=20 nodelay;
```

---

## 📊 Monitoring Setup

### Prometheus Metrics
```bash
# Start with monitoring
docker-compose -f docker-compose.prod.yml up -d

# Access Prometheus
open http://localhost:9090

# View available metrics
curl http://localhost:9090/api/v1/label/__name__/values
```

### Application Health Checks
```bash
# Check application health
curl http://localhost:5000/health

# Check via nginx
curl http://localhost/health

# Docker health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Log Management
```bash
# View application logs
docker-compose logs shopify-theme-detector

# View nginx logs
docker-compose logs nginx

# Tail logs in real-time
docker-compose logs -f --tail=100

# Nginx access logs
tail -f logs/nginx/access.log

# Nginx error logs  
tail -f logs/nginx/error.log
```

---

## 🛠️ Maintenance Commands

### Container Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart shopify-theme-detector

# Rebuild and restart
docker-compose up -d --build

# View resource usage
docker stats

# Clean up unused containers/images
docker system prune
```

### Updates and Deployment
```bash
# Update application
git pull origin main

# Rebuild and deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Rolling update (zero downtime)
docker-compose up -d --scale shopify-theme-detector=2
sleep 10
docker-compose up -d --scale shopify-theme-detector=1
```

### Backup and Recovery
```bash
# Backup volumes
docker run --rm -v shopify-detector_logs:/data -v $(pwd):/backup alpine tar czf /backup/logs-backup.tar.gz -C /data .

# Backup configuration
tar czf config-backup.tar.gz nginx/ monitoring/ *.yml .env

# Restore from backup
tar xzf logs-backup.tar.gz -C logs/
tar xzf config-backup.tar.gz
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
export PORT=5001
docker-compose up -d
```

#### 2. Permission Denied
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 nginx/
chmod 600 ssl/*.pem
```

#### 3. Container Won't Start
```bash
# Check logs
docker-compose logs shopify-theme-detector

# Debug container
docker run -it --rm shopify-theme-detector:latest /bin/bash

# Check resource limits
docker system df
```

#### 4. Nginx Configuration Error
```bash
# Test nginx config
docker run --rm -v $(pwd)/nginx:/etc/nginx nginx:alpine nginx -t

# Reload nginx
docker-compose exec nginx nginx -s reload
```

### Performance Issues
```bash
# Monitor resource usage
docker stats --no-stream

# Check application metrics
curl http://localhost:5000/health

# Monitor logs for errors
docker-compose logs --tail=100 | grep ERROR
```

### Debugging Steps
1. **Check container status**: `docker ps -a`
2. **View logs**: `docker-compose logs <service>`
3. **Test connectivity**: `curl http://localhost:5000/health`
4. **Check nginx config**: `nginx -t`
5. **Verify volumes**: `docker volume ls`

---

## 📈 Scaling and Performance

### Horizontal Scaling
```bash
# Scale application containers
docker-compose up -d --scale shopify-theme-detector=3

# Update nginx upstream
# Edit nginx/default.conf to include multiple upstream servers
```

### Performance Optimization
```yaml
# docker-compose.prod.yml optimizations
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

### Caching Strategy
- **Nginx**: Static file caching with 1-year expiration
- **Application**: Flask caching headers for dynamic content
- **Redis**: Optional caching layer for API responses

---

## 🎯 Production Checklist

### Pre-deployment
- [ ] SSL certificates configured
- [ ] Environment variables set
- [ ] Domain name configured in nginx
- [ ] Resource limits defined
- [ ] Backup strategy implemented
- [ ] Monitoring configured

### Security
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] SSL/TLS properly configured
- [ ] Sensitive data encrypted
- [ ] File permissions correct

### Performance
- [ ] Gzip compression enabled
- [ ] Static file caching configured
- [ ] Resource limits set
- [ ] Health checks working
- [ ] Logs properly configured

### Monitoring
- [ ] Prometheus metrics available
- [ ] Log aggregation setup
- [ ] Alerting configured
- [ ] Health checks operational
- [ ] Performance baselines established

---

## 🔗 Additional Resources

### Docker Documentation
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Docker Production Deployment](https://docs.docker.com/engine/swarm/)

### Nginx Configuration
- [Nginx Performance Tuning](https://nginx.org/en/docs/http/ngx_http_core_module.html)
- [SSL Configuration Guide](https://ssl-config.mozilla.org/)

### Monitoring
- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

## 📞 Support

For deployment issues or questions:

1. **Check Logs**: Review container and application logs
2. **Documentation**: Refer to this guide and official Docker docs  
3. **Community**: Docker and Flask community forums
4. **Issues**: Create issue in project repository

---

**Deployment Status**: ✅ **Production Ready**  
**Last Updated**: 2024-08-14  
**Next Review**: 2024-09-14