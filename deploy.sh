#!/bin/bash

# MeshNet Ultra Deployment Script
# Deploys the entire stack with Docker

set -e

echo "🚀 MeshNet Ultra Deployment"
echo "============================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs config web/static web/templates prometheus_data grafana_data ssl

# Generate SSL certificates (for development)
if [ ! -f ssl/cert.pem ]; then
    echo "🔐 Generating SSL certificates..."
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem \
        -days 365 -nodes -subj "/CN=localhost"
fi

# Ask for deployment type
echo ""
echo "Select deployment type:"
echo "1. Development (localhost)"
echo "2. Production (domain)"
read -p "Enter choice (1 or 2): " deploy_type

if [ "$deploy_type" == "2" ]; then
    read -p "Enter domain name: " domain
    read -p "Enter email for SSL: " email
    
    # Update nginx config with domain
    sed -i "s/server_name _;/server_name $domain;/g" nginx.conf
    
    # Use Let's Encrypt
    echo "🔐 Setting up Let's Encrypt..."
    # In production, use certbot with docker
fi

# Set environment variables
echo "📝 Setting up environment..."
read -p "Enter Node ID (or press Enter for auto): " node_id
read -p "Enter Node Role (gateway/client/auto): " node_role

cat > .env << EOF
NODE_ID=${node_id:-auto}
NODE_ROLE=${node_role:-auto}
LOG_LEVEL=info
ENABLE_QUANTUM=true
ENABLE_AI=true
ENABLE_BLOCKCHAIN=true
GRAFANA_PASSWORD=admin123
EOF

# Build and start
echo "🏗️ Building Docker images..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access your MeshNet Ultra:"
echo "   Dashboard: http://localhost:80"
echo "   Grafana: http://localhost:3001"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "📊 Check status: docker-compose ps"
echo "📋 View logs: docker-compose logs -f"
echo "🛑 Stop: docker-compose down"
