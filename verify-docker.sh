#!/bin/bash

# Docker Configuration Verification Script
# Run this script to verify Docker setup before deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Docker Configuration Verification ===${NC}\n"

# Check if Docker is installed
echo -e "${BLUE}1. Checking Docker installation...${NC}"
if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is installed: $(docker --version)${NC}"
else
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if Docker Compose is installed
echo -e "\n${BLUE}2. Checking Docker Compose installation...${NC}"
if command -v docker-compose >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker Compose is installed: $(docker-compose --version)${NC}"
elif docker compose version >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker Compose (plugin) is installed: $(docker compose version)${NC}"
else
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo -e "${YELLOW}Please install Docker Compose${NC}"
    exit 1
fi

# Check if Docker daemon is running
echo -e "\n${BLUE}3. Checking Docker daemon...${NC}"
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker daemon is running${NC}"
else
    echo -e "${RED}✗ Docker daemon is not running${NC}"
    echo -e "${YELLOW}Please start Docker and try again${NC}"
    exit 1
fi

# Verify required files exist
echo -e "\n${BLUE}4. Checking required files...${NC}"

required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "docker-compose.prod.yml"
    ".dockerignore"
    "requirements.txt"
    "app.py"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file${NC}"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo -e "\n${RED}Missing required files:${NC}"
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

# Check directory structure
echo -e "\n${BLUE}5. Checking directory structure...${NC}"

required_dirs=(
    "blog"
    "blog/posts"
    "i18n"
    "templates"
    "nginx"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ $dir/${NC}"
    else
        echo -e "${YELLOW}⚠ $dir/ (will be created if needed)${NC}"
    fi
done

# Validate Docker Compose files
echo -e "\n${BLUE}6. Validating Docker Compose files...${NC}"

compose_files=(
    "docker-compose.yml"
    "docker-compose.dev.yml"  
    "docker-compose.prod.yml"
)

for compose_file in "${compose_files[@]}"; do
    if docker-compose -f "$compose_file" config >/dev/null 2>&1; then
        echo -e "${GREEN}✓ $compose_file is valid${NC}"
    else
        echo -e "${RED}✗ $compose_file has syntax errors${NC}"
        docker-compose -f "$compose_file" config
        exit 1
    fi
done

# Check Python dependencies
echo -e "\n${BLUE}7. Checking Python requirements...${NC}"
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓ requirements.txt found${NC}"
    echo -e "${BLUE}Dependencies:${NC}"
    cat requirements.txt | head -10
    if [ $(wc -l < requirements.txt) -gt 10 ]; then
        echo "... and $(( $(wc -l < requirements.txt) - 10 )) more"
    fi
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Check environment configuration
echo -e "\n${BLUE}8. Checking environment configuration...${NC}"
if [ -f ".env.example" ]; then
    echo -e "${GREEN}✓ .env.example found${NC}"
else
    echo -e "${YELLOW}⚠ .env.example not found${NC}"
fi

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
else
    echo -e "${YELLOW}⚠ .env file not found (will use defaults)${NC}"
fi

# Test Docker build (dry run)
echo -e "\n${BLUE}9. Testing Docker build configuration...${NC}"
if docker build --dry-run . >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Dockerfile syntax is valid${NC}"
else
    echo -e "${RED}✗ Dockerfile has issues${NC}"
    docker build --dry-run .
    exit 1
fi

# Final summary
echo -e "\n${GREEN}=== Verification Complete ===${NC}"
echo -e "${GREEN}✓ All checks passed! Docker deployment is ready.${NC}\n"

echo -e "${BLUE}Next steps:${NC}"
echo -e "  ${YELLOW}Development:${NC} ./start.sh dev"
echo -e "  ${YELLOW}Production:${NC}  ./start.sh prod"
echo -e "  ${YELLOW}Standard:${NC}    ./start.sh standard"
echo -e "  ${YELLOW}Help:${NC}        ./start.sh help"

echo -e "\n${BLUE}Quick test:${NC}"
echo -e "  docker build -t shopify-theme-detector:test ."
echo -e "  docker run --rm -p 5000:5000 shopify-theme-detector:test"