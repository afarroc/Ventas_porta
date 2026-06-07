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
| `id_lead` | UUIDField | Identificador único del lead |
| `telefono` | CharField | Teléfono del contacto (único) |
| `nombres` | CharField | Nombres del contacto |
| `paterno` | CharField | Apellido paterno |
| `materno` | CharField | Apellido materno |
| `correo` | EmailField | Email del contacto |
| `documento` | CharField | Número de documento (DNI, RUT) |
| `observaciones` | TextField | Notas adicionales |
| `contact_callable` | CharField | ¿Es contactable? (Sí/No) |
| `ultimo_intento` | CharField | Último intento registrado en CRM |
| `ultimo_resultado_crm` | CharField | Último resultado en CRM |
| `es_callable` | CharField | ¿Es contactable? (Sí/No) |
| `fecha_gestion` | DateField | Fecha de gestión |
| `hora_gestion` | TimeField | Hora de gestión |
| `resultado_gestion` | CharField | Resultado del contacto |
| `tipo_contacto` | CharField | Tipo de contacto |
| `tipo_valido` | CharField | Válido/Inválido/No definido |
| `status_java` | CharField | Status JAVA |
| `supervisor_nombre` | CharField | Nombre del supervisor |
| `base_procedencia` | CharField | Base de procedencia del lead (POT, RSG_01, etc.) |
| `base_manual` | BooleanField | Indica si el lead fue cargado manualmente (no existe en base) |
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

**Secciones del Formulario (actualizado 2026-06-06):**

#### Agente
- `agente_nombre`: Nombre del vendedor/agente (requerido)

#### Cliente (Transitorio)
- `cliente_tipo_documento`, `cliente_nombres`, `cliente_paterno`, `cliente_materno`
- `cliente_documento`
- `cliente_telefono_1`, `cliente_telefono_2`

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
/postventa/                 → Dashboard BO (métricas y últimas ventas)
/postventa/backoffice/      → Listado consolidado postventa (alias)
/postventa/backoffice/venta/<id>/ → Formulario SeguimientoBO por venta
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

## 14. Refactorización y Data Ownership (2026-06-06)

### Sprint 8 - Completado (2026-06-07)

| Tarea | Status |
|-------|--------|
| Templates despacho/courier/proveedor creados | ✅ |
| URLs despacho/courier/proveedor agregadas | ✅ |
| Botones acción en detalle venta | ✅ |
| Modelo SeguimientoBO duplicado eliminado | ✅ |
| Imports y referencias corregidas | ✅ |

### Campos Eliminados del Modelo Venta

| Campo | Motivo | Fuente Alternativa |
|-------|--------|-------------------|
| `contact_callable` | Dato del lead | BaseLlamada.contact_callable |
| `es_callable` | Redundante | BaseLlamada.es_callable |
| `fecha_gestion` | Dato del lead | BaseLlamada.fecha_gestion |
| `hora_gestion` | Dato del lead | BaseLlamada.hora_gestion |
| `resultado_gestion` | Dato del lead | BaseLlamada.resultado_gestion |
| `tipo_contacto` | Dato del lead | BaseLlamada.tipo_contacto |
| `tipo_valido` | Dato del lead | BaseLlamada.tipo_valido |
| `status_java` | Información CRM | BaseLlamada.status_java |
| `supervisor_nombre` | Dato del usuario | UserProfile |
| `fecha_venta` | Redundante | Venta.creado (timestamp) |
| `hora_venta` | Redundante | Venta.creado (timestamp) |

### Arquitectura Data Ownership

```
Venta           ───→ (1) BaseLlamada (FK) [datos del lead]
│                    └── contact_callable, es_callable, resultado_gestion, etc.
│
├─ SeguimientoBO (1:1) [postventa — área BO]
│    └── status_bo, fecha_bo, supervisor
│
├─ EstadoDespacho (1:1) [postventa — área Despacho]
│    └── etapa, fecha_etapa, proveedor, tracking
│
└─ EstadoCourier (1:1) [postventa — área Courier]
     └── sts_courier, fch_courier, proveedor, tracking
```

### Queries Clave Unificadas

```python
# Venta con datos del lead y postventa
venta = Venta.objects.select_related(
    'base_llamada', 'cliente'
).prefetch_related(
    'seguimiento_bo', 'estado_despacho', 'estado_courier', 'items'
).get(id=venta_id)

# Acceso a datos
venta.base_llamada.base_procedencia
venta.base_llamada.base_manual
venta.tipo_renta
venta.tipo_renta2
venta.seguimiento_bo.status_bo
venta.estado_despacho.etapa
venta.estado_courier.sts_courier
```
