# Ventas Porta

Aplicación Django para gestión de ventas con módulos de discador y backoffice.

## Requisitos

- Python 3.12+
- Django 4.2
- MySQL / MariaDB
- pip

## Instalación

```bash
git clone <REPO_URL>
cd Ventas_Porta

cp .env.example .env
# Ajustar DATABASE_URL y SECRET_KEY en .env

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

## Uso

```bash
python manage.py runserver
```

Abrir `http://localhost:8000/admin/`.

## Estructura

```
├── apps/
│   ├── discador/      # BaseLlamada, CallRecord
│   └── ventas/        # Venta, ItemVenta, SeguimientoBO
├── config/
├── templates/
├── static/
├── manage.py
└── requirements.txt
```

## Documentación

Ver `docs/` para detalles de despliegue y configuración.
