# Ventas Porta

Aplicación Django para gestión de ventas, discador, postventa, despacho, courier y usuarios.

## Estado actual

- Rama: `feature/catalogo-productos-retail`
- Apps registradas en `config/settings.py`: `apps.discador`, `apps.ventas`, `apps.users`, `apps.postventa`, `apps.despacho`, `apps.courier`
- `apps.catalogo` existe como app no registrada; la integración comercial se mantiene opcional mediante `apps/ventas/catalogo_utils.py` con fallback a reglas legacy.
- `BaseLlamada.id_lead` usa `HexUUIDField` para almacenar UUID como `char(32)` compatible con MySQL.
- Migración aplicada: `apps/discador/migrations/0011_alter_basellamada_id_lead.py`
- Validaciones de Producto y Venta disponibles en `/api/ventas/precio-venta/` y `/api/ventas/validar-producto/`.
- El botón **Guardar Venta** permanece bloqueado hasta validar Cliente y Producto.

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
source venv/bin/activate
python manage.py runserver
```

Abrir `http://localhost:8000/admin/`.

## Validación de Producto y Venta

El formulario de ventas valida por secciones:

1. **Cliente**: buscar/validar cliente existente o registrar cliente nuevo.
2. **Producto y Venta**: hacer clic en **Validar Producto** para consultar `/api/ventas/validar-producto/`.
3. **Guardar Venta**: permanece bloqueado hasta que Cliente y Producto estén validados.

El endpoint valida reglas de negocio para `CHIP` y `PACK`, portabilidad, modelo, plan, tipo de línea, precio y tipo de renta. La validación definitiva sigue en backend (`VentaForm.clean()` y `Venta.calcular_tipo_renta()`).

## Documentación del repositorio

### Raíz `/`

| Archivo | Uso |
|---|---|
| `README.md` | Inicio rápido, estado actual, estructura y documentación principal. |
| `DEPLOYMENT.md` | Configuración de base de datos y arranque del servicio. |
| `HANDOFF_2026-06-11.md` | Fix de ubigeo: JSON local, `apps/ventas/ubigeo_peru.py`, `initUbigeoPeru()`. |

### `docs/`

| Archivo | Uso |
|---|---|
| `docs/documentacion.md` | Documentación principal del sistema. |
| `docs/HISTORIAL.md` | Registro de cambios por fecha. |
| `docs/DEV_REFERENCE.md` | Referencia técnica de arquitectura, apps separadas, servicios y signals. |
| `docs/queries_referenciadas.md` | Queries de trazabilidad Lead → Venta y postventa. |
| `docs/HANDOFF_2026-06-05_ventas.md` | Handoff de ventas. |
| `docs/HANDOFF_2026-06-06_venta_refactor.md` | Refactor del modelo Venta. |
| `docs/HANDOFF_2026-07_apps_separacion.md` | Separación de apps postventa, despacho y courier. |
| `docs/HANDOFF_2026-07_trazabilidad.md` | Trazabilidad Lead → Venta. |
| `docs/HANDOFF_2026-08_estado_actual.md` | Estado de sprints, bugs críticos y reglas retail. |
| `docs/HANDOFF_2026-10_modelo_venta_refactor.md` | Refactor del modelo Venta. |

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
│   ├── ventas/
│   │   ├── admin.py        # VentaAdmin + inlines
│   │   ├── apps.py         # VentasConfig
│   │   ├── forms.py        # VentaForm, ItemVentaForm
│   │   ├── models.py       # Venta, ItemVenta, Cliente
│   │   ├── tests.py        # Tests
│   │   ├── urls.py         # /ventas/...
│   │   ├── ubigeo_peru.py  # Ubigeo Perú
│   │   └── views.py        # CRUD ventas + AJAX endpoints
│   ├── postventa/
│   ├── despacho/
│   └── courier/
├── config/
│   ├── settings.py         # Configuración Django desde .env
│   ├── urls.py             # Router principal
│   ├── wsgi.py / asgi.py   # Deployment
│   └── __init__.py         # PyMySQL bridge
├── docs/                   # Documentación
├── static/
│   ├── js/venta-form.js    # Validación cliente/producto y ubigeo
│   └── data/ubigeo-peru.json
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── discador/
│   ├── users/registration/
│   ├── ventas/
│   ├── postventa/
│   ├── despacho/
│   └── courier/
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

## Comandos útiles

```bash
source venv/bin/activate
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py runserver
```

Validación principal: `docs/documentacion.md`.
