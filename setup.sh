#!/bin/bash
# Script de setup inicial del proyecto

echo "================================"
echo "Setup: Sistema de Gestión Ventas"
echo "================================"
echo ""

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

echo "Activando entorno virtual..."
source venv/bin/activate

# Verificar y crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "⚠️  Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "✏️  Por favor, edita .env con tus credenciales reales"
    echo ""
fi

echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Aplicando migraciones..."
python manage.py migrate

echo ""
echo "================================"
echo "✅ Setup completado"
echo "================================"
echo ""
echo "Próximos pasos:"
echo "1. Editar .env con credenciales correctas si es necesario"
echo "2. Crear superusuario: python manage.py createsuperuser"
echo "3. Iniciar servidor: python manage.py runserver"
echo "4. Acceder admin: http://localhost:8000/admin/"
echo ""

