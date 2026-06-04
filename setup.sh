#!/bin/bash
# Project setup script

set -e

echo "================================"
echo "Setup: Ventas Porta"
echo "================================"
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Edit .env with your credentials"
    echo ""
fi

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Running migrations..."
python manage.py migrate

echo ""
echo "================================"
echo "Setup complete"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update .env with your credentials"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Run server: python manage.py runserver"
