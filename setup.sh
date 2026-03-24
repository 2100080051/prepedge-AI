#!/bin/bash

# PrepEdge AI - Complete Setup Script

echo "🚀 PrepEdge AI - Setup Script"
echo "=============================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Setup Backend
echo -e "\n${BLUE}Setting up Backend...${NC}"
cd backend

# Check Python version
python --version || echo "Python not found"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt -q

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file - Please update with your credentials${NC}"
else
    echo ".env file already exists"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Setup Frontend
echo -e "\n${BLUE}Setting up Frontend...${NC}"
cd ../frontend

# Install npm dependencies
echo "Installing Node dependencies..."
npm install -q

# Create .env.local file
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF
    echo -e "${GREEN}✓ Created .env.local file${NC}"
else
    echo ".env.local file already exists"
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"

# Summary
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # (or venv\\Scripts\\activate on Windows)"
echo "   python main.py"
echo ""
echo "2. Frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
