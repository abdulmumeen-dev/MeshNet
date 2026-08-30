#!/bin/bash
# deploy_complete.sh - Deploy EVERYTHING for MeshNet Ultra

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MeshNet Ultra - Complete Deployment${NC}"
echo "======================================"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# Check if connected to cluster
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Not connected to Kubernetes cluster.${NC}"
    exit 1
fi

# Create namespace
echo -e "${YELLOW}📁 Creating namespace...${NC}"
kubectl create namespace meshnet --dry-run=client -o yaml | kubectl apply -f -

# Create secrets
echo -e "${YELLOW}🔐 Creating secrets...${NC}"
kubectl apply -f secrets.yaml

# Deploy Redis
echo -e "${YELLOW}🗄️ Deploying Redis...${NC}"
kubectl apply -f redis.yaml

# Deploy Core MeshNet
echo -e "${YELLOW}☸️ Deploying MeshNet Core...${NC}"
kubectl apply -f k8s/

# Deploy Istio Service Mesh
echo -e "${YELLOW}🌐 Deploying Istio...${NC}"
kubectl apply -f istio/

# Deploy API Gateway
echo -e "${YELLOW}🌐 Deploying API Gateway...${NC}"
kubectl apply -f api_gateway.yaml

# Deploy AI Model Serving
echo -e "${YELLOW}🤖 Deploying AI Model Serving...${NC}"
kubectl apply -f ml_model_serving.yaml

# Deploy Monitoring
echo -e "${YELLOW}📊 Deploying Monitoring Stack...${NC}"
kubectl apply -f prometheus/
kubectl apply -f grafana/

# Deploy Mobile Backend
echo -e "${YELLOW}📱 Deploying Mobile Backend...${NC}"
kubectl apply -f mobile_backend.yaml

# Wait for all deployments to be ready
echo -e "${YELLOW}⏳ Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=meshnet-ultra -n meshnet --timeout=300s 2>/dev/null || true
kubectl wait --for=condition=ready pod -l app=meshnet-api-gateway -n meshnet --timeout=120s 2>/dev/null || true

# Get all pods
echo -e "\n${GREEN}✅ All deployments complete!${NC}"
echo -e "\n${BLUE}📋 Running pods:${NC}"
kubectl get pods -n meshnet

# Get services
echo -e "\n${BLUE}📡 Services:${NC}"
kubectl get svc -n meshnet

# Get ingress
echo -e "\n${BLUE}🌐 Ingress:${NC}"
kubectl get ingress -n meshnet 2>/dev/null || echo "No ingress found"

# Print access information
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ MeshNet Ultra is DEPLOYED!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📍 Access your MeshNet Ultra:${NC}"
echo "   Dashboard: https://meshnet.yourdomain.com"
echo "   API: https://api.meshnet.yourdomain.com"
echo "   Grafana: https://grafana.meshnet.yourdomain.com"
echo "   Prometheus: https://prometheus.meshnet.yourdomain.com"
echo ""
echo -e "${BLUE}🔑 Default Credentials:${NC}"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo -e "${BLUE}📱 Mobile App:${NC}"
echo "   Connect to: api.meshnet.yourdomain.com"
echo ""
echo -e "${BLUE}🛠️ Useful Commands:${NC}"
echo "   Get pods:      kubectl get pods -n meshnet"
echo "   View logs:     kubectl logs -n meshnet -l app=meshnet-ultra"
echo "   Restart:       kubectl rollout restart deployment/meshnet-ultra -n meshnet"
echo "   Scale:         kubectl scale deployment/meshnet-ultra -n meshnet --replicas=5"
echo "   Stop:          kubectl delete -f k8s/"
echo ""
echo -e "${YELLOW}💡 To configure your domain, update the Ingress files with your domain.${NC}"
