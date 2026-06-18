# Ventas Porta

Aplicación Django para gestión de ventas con módulos de discador, ventas y usuarios.

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
# Ajustar SECRET_KEY y DATABASE_* en .env

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

## Uso

```bash
python manage.py runserver
```

Abrir `http://localhost:8000/admin/`.

## Validación de Producto y Venta

El formulario de ventas incluye validación por secciones:

1. **Cliente**: buscar/validar cliente existente o registrar cliente nuevo.
2. **Producto y Venta**: hacer clic en **Validar Producto** para consultar `/api/ventas/validar-producto/`.
3. **Guardar Venta**: permanece bloqueado hasta que Cliente y Producto estén validados.

El endpoint valida reglas de negocio para `CHIP` y `PACK`, portabilidad, modelo, plan, tipo de línea, precio y tipo de renta. La validación definitiva sigue en backend (`VentaForm.clean()` y `Venta.calcular_tipo_renta()`).

## Estructura

```
├── apps/
│   ├── discador/
│   │   ├── admin.py        # BaseLlamadaAdmin, CallRecordAdmin
│   │   ├── apps.py         # AppConfig
│   │   ├── models.py       # BaseLlamada, CallRecord
│   │   ├── tests.py        # Tests
│   │   ├── urls.py         # /discador/...
│   │   └── views.py        # Listado, detalle, dashboard agente
│   ├── users/
│   │   ├── admin.py        # UserAdmin + UserProfileAdmin
│   │   ├── apps.py         # UsersConfig
│   │   ├── models.py       # UserProfile
│   │   ├── signals.py      # post_save perfil
│   │   ├── tests.py        # Tests
│   │   ├── urls.py         # /users/...
│   │   └── views.py        # Login/logout/dashboard
│   └── ventas/
│       ├── admin.py        # VentaAdmin + inlines
│       ├── apps.py         # VentasConfig
│       ├── forms.py        # VentaForm, ItemVentaForm, SeguimientoBOForm
│       ├── models.py       # Venta, ItemVenta, SeguimientoBO, Cliente
│       ├── tests.py        # Tests
│       ├── urls.py         # /ventas/...
│       └── views.py        # CRUD ventas + AJAX cliente
├── config/
│   ├── settings.py         # Configuración Django (desde .env)
│   ├── urls.py             # Router principal
│   ├── wsgi.py / asgi.py   # Deployment
│   └── __init__.py         # PyMySQL bridge
├── docs/
│   └── documentacion.md    # Documentación completa
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── discador/
│   │   ├── agent_dashboard.html
│   │   ├── base_llamada_list.html
│   │   └── base_llamada_detail.html
│   ├── users/registration/login.html
│   └── ventas/
│       ├── venta_form.html
│       ├── venta_list.html
│       └── venta_detail.html
├── manage.py
├── requirements.txt
├── setup.sh
└── .env.example
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta Django |
| `DEBUG` | Modo debug (`True`/`False`) |
| `ALLOWED_HOSTS` | Hosts permitidos (CSV) |
| `DATABASE_ENGINE` | Motor de BD |
| `DATABASE_NAME` | Nombre de la base |
| `DATABASE_USER` | Usuario de BD |
| `DATABASE_PASSWORD` | Contraseña de BD |
| `DATABASE_HOST` | Host de BD |
| `DATABASE_PORT` | Puerto de BD |

## Documentación

Ver `docs/documentacion.md` para detalles de modelos, relaciones y configuración.
