# Documentación - Sistema de Gestión de Ventas

## 1. Descripción General

Sistema Django de gestión de ventas con cuatro módulos principales:

- **Módulo Discador**: Gestión de bases de llamadas, asignación de leads a agentes y registro de llamadas (CallRecord) con tipificación y ACW
- **Módulo Ventas**: Registro de ventas con ítems y datos maestros, integrado con clientes y bases de discador
- **Módulo Postventa**: Seguimiento postventa por área: BO, Despacho y Courier. Cada área gestiona su propio flujo sobre la misma entidad Venta.
- **Módulo Usuarios**: Autenticación, perfiles de usuario con roles (Agente/Supervisor/Administrador) y estados operativos

---

## 2. Entidades Principales

### 2.1 Módulo Discador

**Modelo: `BaseLlamada`** (`discador_base`)

Contactos de la base de discado con sus resultados de gestión.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | AutoField | Identificador único autoincremental |
| `id_lead` | UUIDField | Identificador único del lead |
| `telefono` | CharField | Teléfono del contacto (único) |
| `nombres` | CharField | Nombres del contacto |
| `paterno` | CharField | Apellido paterno |
| `materno` | CharField | Apellido materno |
| `correo` | EmailField | Email del contacto |
| `documento` | CharField | Número de documento (DNI, RUT) |
| `observaciones` | TextField | Notas adicionales |
| `contact_callable` | CharField | ¿Es contactable? (0=No, 1=Sí) |
| `ultimo_intento` | CharField | Último intento registrado en CRM |
| `ultimo_resultado_crm` | CharField | Último resultado en CRM |
| `es_callable` | CharField | ¿Es contactable? (0=No, 1=Sí) |
| `fecha_gestion` | DateField | Fecha de gestión |
| `hora_gestion` | TimeField | Hora de gestión |
| `resultado_gestion` | CharField | Resultado del contacto (Sin gestión/Gestionado/Venta Convertida) |
| `tipo_contacto` | CharField | Tipo de contacto |
| `tipo_valido` | CharField | Válido/Inválido/No definido |
| `status_java` | CharField | Status JAVA |
| `supervisor_nombre` | CharField | Nombre del supervisor |
| `base_procedencia` | CharField | Base de procedencia del lead (POT, RSG_01, etc.) |
| `base_manual` | BooleanField | Indica si el lead fue cargado manualmente (no existe en base) |
| `venta` | ForeignKey(Venta) | Venta asociada generada desde este lead (trazabilidad bidireccional) |
| `creado` | DateTimeField | Timestamp de creación |
| `actualizado` | DateTimeField | Timestamp de actualización |

**Modelo: `CallRecord`** (`discador_llamada`)

Registro individual de llamada por agente con resultado, ACW y tipificación.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `agente` | ForeignKey(User) | Agente que realizó la llamada |
| `base_llamada` | ForeignKey(BaseLlamada) | Lead asociado |
| `inicio` | DateTimeField | Inicio de la llamada |
| `fin` | DateTimeField | Fin de la llamada |
| `duracion` | DurationField | Duración calculada (inicio - fin) |
| `resultado` | CharField | Contestada/No contestada/Ocupada/Desconectada/No voz/Fax/Otro/Liberado sin uso |
| `observaciones` | TextField | Observaciones del agente |
| `acw_start` | DateTimeField | Inicio de trabajo post-llamada |
| `acw_end` | DateTimeField | Fin de trabajo post-llamada |
| `disposition` | CharField | Tipificación: Venta/No contesta/Cuelga/Fax/No desea/Otro/Liberado sin uso |
| `liberado_sin_uso` | BooleanField | Marcado como liberado sin gestión |

---

### 2.2 Módulo Usuarios

**Modelo: `UserProfile`** (`users_profile`)

Perfil extendido del usuario de Django con rol, estado operativo, disponibilidad y supervisión.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user` | OneToOneField(User) | Relación con usuario Django |
| `rol` | CharField | Rol: Agente/Supervisor/Administrador |
| `codigo_agente` | CharField | Código único de agente (opcional) |
| `telefono` | CharField | Teléfono del usuario |
| `supervisor` | ForeignKey(self) | Supervisor asignado (solo supervisores) |
| `zona` | CharField | Zona de trabajo |
| `turno` | CharField | Turno: Diurno/Nocturno/Híbrido |
| `activo` | BooleanField | Usuario activo |
| `estado` | CharField | Estado operativo: Activo/Inactivo/Baja/Vacaciones |
| `disponibilidad` | CharField | Disponibilidad del agente: Disponible/Pausa/No Listo/En Llamada/Coach |

---

### 2.3 Módulo Ventas

**Modelo: `Cliente`** (`ventas_cliente`)

Cliente maestro con documento único.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `documento` | CharField | Documento único (DNI/RUT) |
| `tipo_documento` | CharField | DNI/RUC/CE/Pasaporte (nuevo) |
| `nombres` | CharField | Nombres |
| `paterno` | CharField | Apellido paterno |
| `materno` | CharField | Apellido materno |
| `telefono_1` | CharField | Teléfono principal |
| `telefono_2` | CharField | Teléfono secundario |
| `activo` | BooleanField | Cliente activo |

**Modelo: `Venta`** (`ventas_venta`)

Registro maestro de operaciones de venta.

**Secciones del Formulario (actualizado 2026-06-09):**

#### Agente
- `agente`: ForeignKey a User (reemplaza campo transitorio `agente_nombre`)

#### Cliente
- `cliente`: ForeignKey a Cliente (formulario permite buscar/crear cliente inline)

#### Recibo Electrónico
- `recibo_electronico`: Sí/No/Si desea/No desea
- `correo_electronico_recibo`, `horario_visita`
- `clausulas`: Aceptación de cláusulas
- `abdcp`: Autorización para datos de portabilidad

#### Producto y Venta
- `producto_nombre`: CHIP (sin modelo, precio fijo S/. 1) o PACK (con modelo y precio variable)
- `origen`: PORTABILIDAD (requiere operador y telefono_portar) o LINEA_NUEVA
- `operador`: Claro/Movistar/Viettel/Virgin (obligatorio si origen=PORTABILIDAD)
- `telefono_portar`: Número a portar (obligatorio si origen=PORTABILIDAD)
- `modelo_producto`: Modelo de equipo (solo para PACK)
- `plan_producto`: Plan ENTEL → determina `precio_plan`
- `precio_plan`: Precio del plan (readonly, determinado por plan_producto)
- `precio_venta`: Precio de venta (filtrado por modelo_producto)
- `tipo_linea`: Postpago (default) o Prepago
- `tipo_renta`: R.BAJA/R.MEDIA/R.ALTA (calculado automáticamente)

#### Dirección de Despacho
- `tipo_via`: Avenida/Calle/Jirón/Pasaje/Prolongación/Carretera/Malecón/Alameda/Urbanización/Asociación/Pueblo Joven (choices - 11 opciones)
- `nombre_via`, `numero_via`, `manzana`, `interior`, `lote`, `piso`
- `centro_poblado`: Centro poblado o asentamiento humano (opcional)
- `zona_tipo`, `zona_nombre`, `zona_referencia`
- `departamento`, `provincia`, `distrito` (combos dependientes jerárquicos vía AJAX)

#### Facturación
- `facturacion_requerida`: ¿Requiere Factura? (Sí/No)

**Secciones eliminadas del formulario (ver Sección 12):**
- Gestión del Discador → `/discador/resultados/` (datos en BaseLlamada)
- Ítems de la Venta → `/ventas/<id>/item/nuevo/` (relación 1:N)
- Seguimiento Backoffice → `/ventas/<id>/backoffice/nuevo/` (relación 1:1)
- Backoffice/Resumen eliminado (reemplazado por SeguimientoBO)

---

### 2.4 Módulo Postventa

**Modelo: `SeguimientoBO`** (`postventa_seguimientobo`)

Trazabilidad administrativa de la venta — etapa BO del flujo postventa.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | OneToOneField | FK a Venta (1:1) |
| `status_bo` | CharField | Estado BO: EN_BASE/PDTE_BO/EN_BO/VALIDADO/EN_DESPACHO/DESPACHADO |
| `fecha_bo` | DateField | Fecha de cambio de estado BO |
| `supervisor` | CharField | Nombre del supervisor |
| `observaciones` | TextField | Notas |
| `creado` | DateTimeField | Timestamp de creación |
| `actualizado` | DateTimeField | Timestamp de actualización |

**Modelo: `Proveedor`** (`postventa_proveedor`)

Entidad independiente para proveedores de despacho/courier.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | CharField | Nombre único del proveedor |
| `activo` | BooleanField | Estado activo |
| `creado` | DateTimeField | Timestamp de creación |

**Modelo: `EstadoDespacho`** (`postventa_estadodespacho`)

Trazabilidad de la etapa de despacho/entrega del producto.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | OneToOneField | FK a Venta (1:1) |
| `etapa` | CharField | Etapa: EN_BASE/PDTE_DESPACHO/EN_PREPARACION/EN_TRANSITO/ENTREGADO/RECHAZADO |
| `fecha_etapa` | DateField | Fecha del cambio de etapa |
| `proveedor` | ForeignKey | FK a Proveedor (opcional) |
| `tracking` | CharField | N° Seguimiento/Tracking |
| `observaciones` | TextField | Notas |
| `creado` | DateTimeField | Timestamp de creación |
| `actualizado` | DateTimeField | Timestamp de actualización |

**Modelo: `EstadoCourier`** (`postventa_estadocourier`)

Trazabilidad del proveedor de courier (flujo paralelo al despacho).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | OneToOneField | FK a Venta (1:1) |
| `sts_courier` | CharField | Estado courier: PDTE_BO/EN_RUTA/ENTREGADO/RECHAZADO |
| `fch_courier` | DateField | Fecha del estado courier |
| `proveedor` | ForeignKey | FK a Proveedor (opcional) |
| `tracking` | CharField | N° Seguimiento/Tracking |
| `observaciones` | TextField | Notas |
| `creado` | DateTimeField | Timestamp de creación |
| `actualizado` | DateTimeField | Timestamp de actualización |

---

## 3. Relaciones

```
Venta (1) ─────→ (N) ItemVenta
  │
  ├─────→ (1) SeguimientoBO          [postventa — área BO]
  │
  ├─────→ (1) EstadoDespacho         [postventa — área Despacho]
  │
  ├─────→ (1) EstadoCourier          [postventa — área Courier]
  │
  └─────→ (1) Cliente (FK)
  │
  └─────→ (0..1) BaseLlamada (FK, opcional)

BaseLlamada (1) ─────→ (N) CallRecord
  │
  └─────→ (0..1) Venta (FK, opcional)

User (1) ─────→ (1) UserProfile
  │
  └───→ (N) CallRecord (como agente)

Proveedor (1) ─────→ (N) EstadoDespacho
Proveedor (1) ─────→ (N) EstadoCourier

UserProfile (1) ─────→ (N) UserProfile (supervisores → agentes)
```

---

## 4. Arquitectura por Áreas

El sistema se organiza por áreas de negocio independientes, cada una gestiona su propio flujo sobre la misma entidad `Venta`:

```
Lead (BaseLlamada) ────────── discador / WFM
       │
       ▼
   Venta (Operaciones) ──── entrada de venta
       │
       ├── postventa ──── SeguimientoBO (validación, administrativo)
       │
       ├── despacho ──── EstadoDespacho (preparación, tránsito, entrega)
       │
       └── courier ──── EstadoCourier (proveedor, tracking, entrega)
```

Cada área registra sus propios estados y fechas sobre la misma venta, manteniendo trazabilidad completa del flujo.

**Tabla de responsabilidades por área:**

| Área | Modelo | Función |
|------|--------|---------|
| WFM / Discador | BaseLlamada, CallRecord | Gestión de leads, llamadas, bases |
| Operaciones | Venta, ItemVenta, Cliente | Registro de venta y cliente |
| Postventa (BO) | SeguimientoBO | Validación, seguimiento administrativo |
| Despacho | EstadoDespacho, Proveedor | Preparación, tránsito, entrega física |
| Courier | EstadoCourier, Proveedor | Estado del proveedor de entrega |

---

## 5. Estructura del Proyecto

```
Ventas_Porta/
├── manage.py                                    # Punto de entrada Django
├── requirements.txt                             # Dependencias: Django, PyMySQL, python-decouple
├── README.md                                    # Documentación rápida
├── DEPLOYMENT.md                                # Guía de despliegue
├── .env                                         # Variables de entorno (NO versionar)
├── config/
│   ├── __init__.py                             # pymysql.install_as_MySQLdb()
│   ├── settings.py                             # Configuración principal Django
│   ├── urls.py                                 # URLs raíz del proyecto
│   ├── wsgi.py                                 # WSGI para producción
│   └── asgi.py                                 # ASGI para producción
├── apps/
│   ├── __init__.py                             # Paquete apps
│   ├── discador/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                           # BaseLlamada, CallRecord
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── migrations/
│   ├── users/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   ├── signals.py
│   │   └── migrations/
│   ├── ventas/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py                           # Venta, ItemVenta, Cliente
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── ubigeo_peru.py
│   │   ├── tests.py
│   │   └── migrations/
│   └── postventa/
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py                           # SeguimientoBO, EstadoDespacho, EstadoCourier, Proveedor
│       ├── admin.py
│       ├── views.py
│       ├── urls.py
│       └── migrations/
└── templates/
    ├── base.html
    ├── home.html
    ├── users/
    │   └── registration/
    │       └── login.html
    ├── discador/
    │   ├── agent_dashboard.html
    │   ├── base_llamada_list.html
    │   └── base_llamada_detail.html
    ├── ventas/
    │   ├── venta_list.html
    │   ├── venta_detail.html
    │   ├── venta_form.html
    │   ├── venta_form_modal.html
    │   ├── item_form.html
    │   └── backoffice_form.html
    └── postventa/
        ├── backoffice_list.html
        ├── despacho_list.html
        └── courier_list.html
```

### Estructura de archivos estáticos

```
Ventas_Porta/
└── static/
    └── css/
        └── form-data.css
```

---

## 6. Detalles por Archivo

### config/__init__.py
Instala PyMySQL como driver MySQLdb para Django.

### config/settings.py
Configura BD con parámetros desde `.env`, charset utf8mb4, LANGUAGE_CODE='es-pe'.
Apps registradas: `apps.discador`, `apps.ventas`, `apps.users`, `apps.postventa`.

### config/urls.py
Incluye URLs de las tres apps: `ventas` (raíz), `discador` y `users`.

### apps/users/models.py
Modelo `UserProfile` extendiendo `User` con roles (Agente/Supervisor/Administrador), estados operativos (estado), disponibilidad del agente (disponibilidad) y supervisión jerárquica.

### apps/users/admin.py
UserAdmin custom con inline de UserProfile, fieldsets y list_display extendido.

### apps/users/views.py
HomeView (dashboard) con contexto de perfil, y logout_view personalizado.

### apps/users/urls.py
URLs de autenticación: login y logout.

### apps/discador/models.py
Modelo `BaseLlamada` en tabla `discador_base` con `base_procedencia` y `base_manual`.
Modelo `CallRecord` en tabla implícita con campos de llamada, ACW y tipificación.

### apps/discador/admin.py
BaseLlamadaAdmin con fieldsets, filters, readonly y búsqueda. CallRecordAdmin con fieldsets de información y ACW.

### apps/discador/views.py
BaseLlamadaListView (paginado 50, filtrado por rol), BaseLlamadaDetailView.

### apps/discador/urls.py
URLs: dashboard del agente (/), listado de bases (/bases/), detalle de base (/base/<id>/), check-incoming (AJAX).

### apps/ventas/models.py
Tres modelos: Venta (50+ campos + tipo_renta2 + multiples_lineas), ItemVenta (FK), Cliente.

### apps/ventas/forms.py
VentaForm con widgets select/date/time/textarea, campos base_* readonly para visualización. ItemVentaForm, SeguimientoBOForm.

### apps/ventas/views.py
VentaCreateView con inlineformset_factory. `venta_modal_partial()` y `venta_api_create()` para modal. `_check_lead_access()` para seguridad UUID. `get_provincias()` y `get_distritos()` para combos jerárquicos de ubigeo. BackofficeListView para listado consolidado postventa.

### apps/ventas/urls.py
URLs: /ventas/, /ventas/nueva/, /ventas/<id>/, /ventas/backoffice/

### apps/ventas/ubigeo_peru.py
Datos de ubigeo Peruano: DEPTO_CHOICES, PROV_CHOICES, DISTRITOS_CHOICES.

### apps/postventa/models.py
Cuatro modelos: SeguimientoBO (estado BO), EstadoDespacho (etapa de entrega), EstadoCourier (estado courier), Proveedor.

### templates/ventas/venta_form.html
Formulario organizado en cards VP.

### templates/ventas/venta_form_modal.html
Formulario simplificado para modal via API.

### templates/ventas/backoffice_list.html
Listado consolidado postventa con columnas: BASE, TIPO RENTA, TIPO RENTA2, BASE, Status BO, Fecha BO, Sts Courier, Fch. Courier.

---

## 7. Flujo de Trabajo del Agente

### 7.1 Estados de Disponibilidad

| Estado | Color | Condición |
|--------|-------|-----------|
| `DISPONIBLE` | Verde | Puede obtener leads y contestar llamadas |
| `PAUSA` | Amarillo | No disponible para llamadas |
| `LISTO_NO` | Rojo | Llamada finalizada, pendiente tipificación |
| `EN_LLAMADA` | Gris | Llamada en curso |
| `COACH` | Azul | En coaching/entrenamiento |

### 7.2 Transiciones de Estado

```
DISPONIBLE → Obtener Lead → DISPONIBLE (lead asignado)
DISPONIBLE → Llamada entrante → EN_LLAMADA
EN_LLAMADA → Finalizar → LISTO_NO (pendiente tipificación)
LISTO_NO → Tipificar → DISPONIBLE
LISTO_NO → Liberar Lead → DISPONIBLE + auditoría (liberado_sin_uso)
PAUSA/COACH → Cambiar disponibilidad → DISPONIBLE
Click "Registrar Venta" → Modal cargado vía API → Submit vía API → Recarga página
```

---

## 8. Flujo Postventa por Áreas

```
Venta registrada
    │
    ▼
Area BO: SeguimientoBO
    EN_BASE → PDTE_BO → EN_BO → VALIDADO → EN_DESPACHO → DESPACHADO
    │
    ├── Area Despacho: EstadoDespacho
    │       PDTE_DESPACHO → EN_PREPARACION → EN_TRANSITO → ENTREGADO / RECHAZADO
    │
    └── Area Courier: EstadoCourier
            PDTE_BO → EN_RUTA → ENTREGADO / RECHAZADO
```

Cada área opera de forma independiente sobre la misma venta. Los datos de proveedor y tracking se registran en las entidades correspondientes.

---

## 9. Rutas (URLs) y API Endpoints

### URLs Principales

```
/                           → HomeView (dashboard principal)
/users/login/               → LoginView
/users/logout/              → logout_view
/discador/                  → AgentDashboardView
/discador/bases/            → BaseLlamadaListView
/discador/base/<int:pk>/    → BaseLlamadaDetailView
/discador/check-incoming/   → AJAX polling
/ventas/                    → VentaListView
/ventas/<int:pk>/           → VentaDetailView
/ventas/nueva/              → VentaCreateView
/ventas/nueva/<uuid:id_lead>/ → VentaCreateView (con lead pre-cargado)
/ventas/backoffice/         → BackofficeListView (listado consolidado postventa)
/ventas/<int:venta_id>/item/nuevo/ → ItemVentaCreateView
/postventa/                 → Dashboard BO (métricas y últimas ventas)
/postventa/backoffice/         → BackofficeListView (listado consolidado postventa)
/postventa/backoffice/venta/<id>/ → Formulario SeguimientoBO por venta
/postventa/backoffice/<int:pk>/editar/ → Editar SeguimientoBO
/postventa/dashboard/conversion/ → DashboardConversiónView
/postventa/despacho/venta/<int:venta_id>/ → EstadoDespachoCreateView
/postventa/despacho/venta/<int:pk>/editar/ → EstadoDespachoUpdateView
/postventa/courier/venta/<int:venta_id>/ → EstadoCourierCreateView
/postventa/courier/venta/<int:pk>/editar/ → EstadoCourierUpdateView
/admin/                     → Panel administración
```

### API Endpoints

| Endpoint | Method | Descripción |
|----------|--------|-----------|
| `/ventas/buscar-cliente/` | GET | Busca cliente por tipo_documento + documento |
| `/ventas/validar-cliente/` | GET | Valida existencia de cliente |
| `/ventas/recargar-lead/<uuid>/` | GET | Recarga datos del lead |
| `/ventas/modal/<uuid>/` | GET | HTML formulario modal vía API |
| `/api/ventas/crear/<uuid>/` | POST | Crea venta vía API JSON |
| `/api/ubigeo/provincias/` | GET | Obtiene provincias por departamento (AJAX) |
| `/api/ubigeo/distritos/` | GET | Obtiene distritos por departamento+provincia (AJAX) |

---

## 10. Configuración de Base de Datos

La configuración se carga exclusivamente desde `.env` (no hardcodeada).

```
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=<nombre_bd>
DATABASE_USER=<usuario>
DATABASE_PASSWORD=<password>
DATABASE_HOST=<host>
DATABASE_PORT=3306
```

- Motor: MySQL/MariaDB  
- Charset: `utf8mb4`  
- Variables requeridas: `DATABASE_ENGINE`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`

---

## 11. Dependencias

```
Django==4.2.13
PyMySQL==1.1.0
python-decouple==3.8
```

---

## 12. Comandos

```bash
# Setup inicial
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Superusuario (requerido para Admin)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Tests
python manage.py test

# Shell Django (para crear usuarios con perfil)
python manage.py shell
```

---

## 13. Panel de Administración

Accesible en `http://localhost:8000/admin/`.

**Módulos disponibles:**
- **Usuarios** (`User`): gestión de usuarios con perfil inline (rol, código, supervisor, estado)
- **Perfiles de Usuario** (`UserProfile`): listado filtrable por activo, turno, zona; búsqueda por username y código
- **Bases de Llamada** (`BaseLlamada`): listado con filtros por es_callable, tipo_valido, fecha; búsqueda por teléfono, nombres, documento
- **Registros de Llamada** (`CallRecord`): historial con filtros por resultado, disposition, fecha
- **Ventas** (`Venta`): con inlines para ítems y cliente
- **Clientes** (`Cliente`): listado de clientes por documento
- **Seguimiento BO** (`SeguimientoBO`)
- **Estado Despacho** (`EstadoDespacho`)
- **Estado Courier** (`EstadoCourier`)
- **Proveedores** (`Proveedor`)

---

## 15. Trazabilidad Lead → Venta (2026-06-08)

### 15.1 Relación Bidireccional Lead-Venta

Relaciones implementadas (Sprint 1):
- `Venta.base_llamada` → FK a BaseLlamada (related_name='ventas_asociadas')
- `BaseLlamada.venta` → FK opcional a Venta (related_name='lead_venta')

Propósito: Círculo completo de trazabilidad - desde el lead se accede a la venta generada y viceversa.

### 15.2 Estados del Lead y Bloqueo

| Estado | Descripción | Transiciones válidas |
|--------|-------------|-------------------|
| `SIN_GESTIONAR` | Lead sin llamada ni venta | → GESTIONADO, → VENTA |
| `GESTIONADO` | Llamada realizada (sin venta) | → VENTA |
| `VENTA_CONVERTIDA` | Lead convertido en venta | ESTADO_FINAL |

**Regla implementada**: Los leads con `resultado_gestion == 'VENTA_CONVERTIDA'` no pueden asignarse a agentes en el discador (`apps/discador/views.py`).

### 15.3 Queries de Trazabilidad

```python
# Venta completa con historial (futuro)
venta = Venta.objects.select_related(
    'base_llamada', 'cliente'
).prefetch_related(
    'bo_seguimiento', 'despacho_estado', 'courier_estado'
).get(id=venta_id)

# Lead → Venta (cuando se implemente FK)
if base_venta.venta:
    venta = base_venta.venta
    # Acceder a toda la trazabilidad

# Estadísticas de conversión por base
from django.db.models import Count
stats = BaseLlamada.objects.values('base_procedencia').annotate(
    total=Count('id'),
    con_venta=Count('venta')
).order_by('-total')
```

---

## 16. Servicio de Registro y Signals de Historial

### 16.1 Servicio `registrar_cambio_estado()` (`apps/postventa/services.py`)

Helper para registrar cambios de estado en `HistorialEstado`.

```python
from apps.postventa.services import registrar_cambio_estado

registrar_cambio_estado(
    venta=venta,
    area='BO',               # BO, DESPACHO, COURIER
    estado_anterior='',
    estado_nuevo='EN_BO',
    usuario=request.user,
    observaciones='Notas'
)
```

### 16.2 Signals de Persistencia Automática (`apps/postventa/signals.py`)

Se registran automáticamente cambios en `HistorialEstado` vía Django signals:
- `post_save` en `SeguimientoBO` → crea registro en área BO
- `post_save` en `EstadoDespacho` → crea registro en área DESPACHO
- `post_save` en `EstadoCourier` → crea registro en área COURIER

Los views de cada área llaman a `registrar_cambio_estado()` en `form_valid()` para registrar tanto el estado inicial (creación) como cambios posteriores (actualización).

---

## 17. Historial de Estados Postventa

### 18.1 Modelo `HistorialEstado` (`postventa_historial`)

Registra cada cambio de estado en el flujo postventa.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | ForeignKey | Venta relacionada |
| `area` | CharField | BO/DESPACHO/COURIER |
| `estado_anterior` | CharField | Estado previo |
| `estado_nuevo` | CharField | Estado nuevo |
| `usuario` | ForeignKey(User) | Usuario que realizó el cambio |
| `fecha_cambio` | DateTimeField | Timestamp del cambio |
| `observaciones` | TextField | Notas adicionales |

### Queries de Historial

```python
# Historial de una venta
historial = venta.historial_estados.all().order_by('-fecha_cambio')

# Filtrar por área
historial_bo = venta.historial_estados.filter(area='BO')
```

---

## 17. Historial de Estados Postventa

### 17.1 Flujo Obligatorio

```
1. SeguimientoBO.status_bo debe ser 'VALIDADO' o 'EN_DESPACHO'
   ↓
2. EstadoDespacho.etapa puede crearse
   ↓
3. SeguimientoBO.status_bo debe ser 'DESPACHADO'
   ↓
4. EstadoCourier.sts_courier puede crearse
```

### 17.2 Reglas de Negocio

1. **Tracking único**: No se permite duplicar `tracking` entre `EstadoDespacho` y `EstadoCourier` de la misma venta (validación en views).
2. **StateDespacho**: Requiere `SeguimientoBO` con `status_bo` en `VALIDADO` o `EN_DESPACHO`.
3. **EstadoCourier**: Requiere `SeguimientoBO` con `status_bo == 'DESPACHADO'`.
4. **VENTA_CONVERTIDA**: Los leads con `resultado_gestion == 'VENTA_CONVERTIDA'` no pueden asignarse a agentes.

---

## 19. Dashboard de Conversión (Implementado)

### 19.1 Métricas Implementadas

| Métrica | Fórmula |
|---------|---------|
| Total Leads | COUNT(BaseLlamada) |
| Total Ventas | COUNT(Venta) |
| Leads Convertidos | BaseLlamada con venta FK |
| Tasa Conversión | Leads Convertidos / Total Leads |

### 19.2 URL

```
/postventa/dashboard/conversion/ → DashboardConversionView
```

### 19.3 Queries

```python
# Estadísticas por base
BaseLlamada.objects.values('base_procedencia').annotate(
    total=Count('id'),
    con_venta=Count('venta')
)
```

---

## 20. Reglas de Negocio Retail - Ventas

### 19.1 Tipo Renta por Combinación

| Origen | Producto | Precio | Tipo Renta |
|--------|----------|--------|------------|
| PORTABILIDAD | PACK | 29-49 | R.BAJA |
| PORTABILIDAD | PACK | 59-75 | R.MEDIA |
| PORTABILIDAD | PACK | 89-99+ | R.ALTA |
| PORTABILIDAD | CHIP | 39-59 | R.BAJA |
| PORTABILIDAD | CHIP | 74-89 | R.MEDIA |
| PORTABILIDAD | CHIP | 109+ | R.ALTA |
| LINEA_NUEVA | PACK | 49-75 | R.BAJA |
| LINEA_NUEVA | PACK | 76-98 | R.MEDIA |
| LINEA_NUEVA | PACK | 99+ | R.ALTA |
| LINEA_NUEVA | CHIP | 25-45 | R.BAJA |
| LINEA_NUEVA | CHIP | 59+ | R.MEDIA |

### 19.2 Validaciones Implementadas

1. **Producto CHIP**: Sin modelo ni precio variable (precio fijo S/. 1)
2. **Origen PORTABILIDAD**: Operador y teléfono_portar obligatorios
3. **Tipo documento**: DNI/RUC/CE/Pasaporte
4. **Recibo electrónico**: Si 'SI_DESEA', correo obligatorio
5. **Tipo renta multilínea**: Si `multiples_lineas=True`, se requiere `tipo_renta2`
6. **Tracking único**: No se permite duplicar tracking entre despacho y courier de la misma venta
7. **Lead VENTA_CONVERTIDA**: No se puede asignar a agentes en discador
8. **Calcular tipo_renta actualizado**: Rangos definidos según §19.1

### 19.3 Validaciones Pendientes

1. Confirmar opciones de MODELOS_PRODUCTO con catálogo ENTEL actual
2. Verificar precios de venta y plan correspondientes al portafolio vigente


