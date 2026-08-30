#!/bin/bash

# MeshNet Ultra Development Setup

echo "🔧 MeshNet Ultra - Development Setup"
echo "===================================="

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements_ultra.txt
pip install flask flask-socketio flask-cors prometheus-client

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs web/static web/templates

# Copy web files
echo "🌐 Setting up web dashboard..."
cp web_dashboard.py .

# Setup pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

pre-commit install

echo ""
echo "✅ Development environment ready!"
echo ""
echo "To start development:"
echo "  source venv/bin/activate"
echo "  python meshnet_production.py"
echo ""
echo "To start web dashboard:"
echo "  python web_dashboard.py"
echo ""
echo "Access dashboard at: http://localhost:3000"
