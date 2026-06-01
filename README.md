# Sistema de Gestión de Ventas - Porta

Sistema Django para gestión integral de ventas con módulos de discador y backoffice.

## Configuración

**Base de datos remota:**
- **Host:** `192.168.18.59` (SSH puerto 8022)
- **Base de datos:** `ventas_<timestamp>`
- **Usuario BD:** Configurar en `.env`

## Instalación

```bash
cp .env.example .env
# Editar .env con credenciales reales

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Accede a `http://localhost:8000/admin/`

## Estructura

```
├── apps/
│   ├── discador/      # BaseLlamada
│   └── ventas/        # Venta, ItemVenta, SeguimientoBO
├── config/
├── templates/         # Bootstrap 5
└── manage.py
```

## Repositorio

https://github.com/afarroc/Ventas_porta

---
**Deploy:** 1 Junio 2026