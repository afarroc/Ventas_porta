# Documentación - Sistema de Gestión de Ventas

## 1. Descripción General

Sistema Django de gestión de ventas con tres módulos principales:

- **Módulo Discador**: Gestión de bases de llamadas, asignación de leads a agentes y registro de llamadas (CallRecord) con tipificación y ACW
- **Módulo Ventas**: Registro de ventas con ítems y seguimiento backoffice, integrado con clientes y bases de discador
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
| `nombres` | CharField | Nombres |
| `paterno` | CharField | Apellido paterno |
| `materno` | CharField | Apellido materno |
| `numero` | CharField | Número adicional |
| `telefono_1` | CharField | Teléfono principal |
| `telefono_2` | CharField | Teléfono secundario |
| `activo` | BooleanField | Cliente activo |

**Modelo: `Venta`** (`ventas_venta`)

Registro maestro de operaciones de venta.

**Secciones:**

#### Agente
- `agente_nombre`: Nombre del vendedor/agente (requerido)

#### Cliente (Transitorio)
- `cliente_nombres`, `cliente_paterno`, `cliente_materno`
- `cliente_documento`, `cliente_numero`
- `cliente_telefono_1`, `cliente_telefono_2`

#### Recibo Electrónico
- `recibo_electronico`: Sí/No/Si desea/No desea
- `correo_electronico_recibo`, `horario_visita`
- `clausulas`: Aceptación de cláusulas
- `abdcp`: Autorización para datos de portabilidad

#### Producto y Venta
- `producto_nombre`, `origen`, `operador`, `telefono_portar`
- `modelo_producto`, `plan_producto`
- `tipo_linea`: Prepago/Postpago/Línea nueva/Portabilidad
- `precio_venta`, `precio_plan`, `tipo_pago`

#### Dirección de Despacho
- `tipo_via`, `nombre_via`, `numero_via`
- `manzana`, `interior`, `lote`, `piso`
- `zona_tipo`, `zona_nombre`, `zona_referencia`
- `departamento`, `provincia`, `distrito`

#### Facturación
- `facturacion_requerida`: ¿Requiere Factura? (Sí/No)

#### Gestión del Discador (heredados)
- `contact_callable`, `es_callable`, `fecha_gestion`, `hora_gestion`
- `resultado_gestion`, `tipo_contacto`, `tipo_valido`
- `status_java`, `supervisor_nombre`

#### Backoffice/Resumen
- `base`, `tipo_renta`, `tipo_renta2`, `base3`
- `q_ventas`: Cantidad de ventas
- `fecha_venta`, `hora_venta`
- `observaciones`

**Modelo: `ItemVenta`** (`ventas_item`)

Desglose de productos/servicios en una venta (máximo 2 ítems).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | ForeignKey | Referencia a Venta (1:N) |
| `tipo_venta` | CharField | Tipo de venta |
| `tipo_producto` | CharField | Tipo de producto/servicio |
| `precio_plan` | DecimalField | Precio del plan |

**Modelo: `SeguimientoBO`** (`ventas_backoffice`)

Estado administrativo de la venta (backoffice, courier, supervisor).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | OneToOneField | Referencia a Venta (1:1) |
| `status_bo` | CharField | Estado Backoffice |
| `fecha_bo` | DateField | Fecha de estado BO |
| `sts_courier` | CharField | Estado del courier |
| `fch_courier` | DateField | Fecha del courier |
| `supervisor` | CharField | Nombre del supervisor |
| `intervalo` | CharField | Intervalo de tiempo |

---

## 3. Relaciones

```
Venta (1) ─────→ (N) ItemVenta
  │
  └─────→ (1) SeguimientoBO
  │
  └─────→ (1) Cliente (FK)
  │
  └─────→ (0..1) BaseLlamada (FK, opcional)

BaseLlamada (1) ─────→ (N) CallRecord
  │
  └─────→ (0..1) Venta (FK, opcional)

User (1) ─────→ (1) UserProfile
  │
  └─────→ (N) CallRecord (como agente)

UserProfile (1) ─────→ (N) UserProfile (supervisores → agentes)
```

---

## 4. Estructura del Proyecto

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
│   │   ├── __init__.py                         # Vacío
│   │   ├── apps.py                             # AppConfig: DiscadorConfig
│   │   ├── models.py                           # Modelo: BaseLlamada (tabla discador_base)
│   │   ├── admin.py                            # Admin: BaseLlamadaAdmin con fieldsets
│   │   ├── views.py                            # Views: BaseLlamadaListView (paginado 50)
│   │   ├── urls.py                             # URLs: /discador/bases/
│   │   ├── tests.py                            # Tests unitarios
│   │   └── migrations/
│   │       ├── __init__.py
│   │       └── 0001_initial.py                 # Migración inicial BaseLlamada
│   ├── users/
│   │   ├── __init__.py                         # Vacío
│   │   ├── apps.py                             # AppConfig: UsersConfig
│   │   ├── models.py                           # Modelo: UserProfile (roles, estados, supervisor)
│   │   ├── admin.py                            # Admin: UserAdmin + UserProfileAdmin con inlines
│   │   ├── views.py                            # Views: HomeView, logout
│   │   ├── urls.py                             # URLs: /users/login/, /users/logout/
│   │   ├── tests.py                            # Tests unitarios
│   │   ├── signals.py                          # Señales: auto-crear perfil
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── 0001_initial.py                 # Migración inicial UserProfile
│   │       ├── 0002_userprofile_rol_*.py       # Agregó rol, codigo_agente
│   │       └── 0003_userprofile_estado.py      # Agregó estado
│   └── ventas/
│       ├── __init__.py                         # Vacío
│       ├── apps.py                             # AppConfig: VentasConfig
│       ├── models.py                           # Modelos: Venta, ItemVenta, SeguimientoBO
│       ├── forms.py                            # Formularios: VentaForm, ItemVentaForm, SeguimientoBOForm
│       ├── admin.py                            # Admin: VentaAdmin + Inlines
│       ├── views.py                            # Views: Home, VentaListView, VentaDetailView, VentaCreateView
│       ├── urls.py                             # URLs: /ventas/, /ventas/nueva/, /ventas/<id>/
│       ├── tests.py                            # Tests unitarios
│       └── migrations/
│           ├── __init__.py
│           ├── 0001_initial.py                 # Migración inicial
│           ├── 0002_alter_venta_options_venta_*.py  # Agregó campos discador
│           └── 0003_alter_venta_verbose_names.py    # Verbose names
└── templates/
    ├── base.html                               # Layout VP framework
    ├── home.html                               # Dashboard principal
    ├── users/
    │   └── registration/
    │       └── login.html                      # Login de usuarios
    ├── discador/
    │   ├── agent_dashboard.html                # Dashboard del agente (modales para obtener/liberar lead)
    │   ├── base_llamada_list.html              # Lista de bases de llamada con búsqueda
    │   └── base_llamada_detail.html            # Detalle de base con historial de llamadas
    └── ventas/
        ├── venta_list.html                     # Lista de ventas (tabla VP)
        ├── venta_detail.html                   # Detalle de venta
        └── venta_form.html                     # Formulario alta/edición (cards VP)
```

### Estructura de archivos estáticos

```
Ventas_Porta/
└── static/
    └── css/
        └── form-data.css                       # Estilos VP framework (variables CSS, botones, cards, tablas, modales, utilidades flex)
```

---

## 5. Detalles por Archivo

### config/__init__.py
Instala PyMySQL como driver MySQLdb para Django.

### config/settings.py
Configura BD con parámetros desde `.env`, charset utf8mb4, LANGUAGE_CODE='es-pe'.

### config/urls.py
Incluye URLs de las tres apps: `ventas` (raíz), `discador` y `users`.

### apps/users/models.py
Modelo `UserProfile` extendiendo `User` con roles (Agente/Supervisor/Administrador), estados operativos (estado), disponibilidad del agente (disponibilidad) y supervisión jerárquica.

### apps/users/admin.py
UserAdmin custom con inline de UserProfile, fieldsets y list_display extendido. Filtra supervisores a solo usuarios con rol SUPERVISOR.

### apps/users/views.py
HomeView (dashboard) con contexto de perfil, y logout_view personalizado.

### apps/users/urls.py
URLs de autenticación: login y logout.

### apps/discador/models.py
Modelo `BaseLlamada` en tabla `discador_base` con choices `CONTACT_CALLABLE`, `TIPO_VALIDO`.
Modelo `CallRecord` en tabla implícita con campos de llamada, ACW y tipificación. Actualiza `ultimo_intento` y `ultimo_resultado_crm` en BaseLlamada al guardar.

### apps/discador/admin.py
BaseLlamadaAdmin con fieldsets, filters, readonly y búsqueda. CallRecordAdmin con fieldsets de información y ACW.

### apps/discador/views.py
BaseLlamadaListView (paginado 50, filtrado por rol), BaseLlamadaDetailView.
AgentDashboardView: Dashboard de agente con:
- Gestión de leads vía AJAX (obtener_lead)
- Control de disponibilidad (DISPONIBLE/PAUSA/LISTO_NO/EN_LLAMADA/COACH)
- Iniciar/finalizar llamada con actualización de disponibilidad
- Liberar lead con auditoría (liberado_sin_uso)
- check_incoming_call endpoint para polling de llamadas entrantes (30s)

### apps/discador/urls.py
URLs: dashboard del agente (/), listado de bases (/bases/), detalle de base (/base/<id>/), check-incoming (AJAX).

### apps/ventas/models.py
Tres modelos: Venta (50+ campos), ItemVenta (FK), SeguimientoBO (OneToOne).

### apps/users/signals.py
Señal `post_save` para `User`: crea automáticamente un `UserProfile` cuando se crea un usuario nuevo.

### apps/ventas/forms.py
VentaForm con widgets select/date/time/textarea, ItemVentaForm, SeguimientoBOForm.

### apps/ventas/views.py
VentaCreateView con inlineformset_factory (extra=2, max_num=2).

### templates/ventas/venta_form.html
Formulario organizado en cards VP con secciones: Agente, Cliente, Recibo, Producto/Venta, Dirección, Facturación, Gestión del Discador, Backoffice. Botones Buscar/Validar cliente con AJAX.

---

## 6. Flujo de Trabajo del Agente

### 6.1 Estados de Disponibilidad

| Estado | Color | Condición |
|--------|-------|-----------|
| `DISPONIBLE` | Verde | Puede obtener leads y contestar llamadas |
| `PAUSA` | Amarillo | No disponible para llamadas |
| `LISTO_NO` | Rojo | Llamada finalizada, pendiente tipificación |
| `EN_LLAMADA` | Gris | Llamada en curso |
| `COACH` | Azul | En coaching/entrenamiento |

### 6.2 Transiciones de Estado

```
DISPONIBLE → Obtener Lead → DISPONIBLE (lead asignado)
DISPONIBLE → Llamada entrante → EN_LLAMADA
EN_LLAMADA → Finalizar → LISTO_NO (pendiente tipificación)
LISTO_NO → Tipificar → DISPONIBLE
LISTO_NO → Liberar Lead → DISPONIBLE + auditoría (liberado_sin_uso)
PAUSA/COACH → Cambiar disponibilidad → DISPONIBLE
```

---

## 5.1 Rutas (URLs)

```
/                          → HomeView (dashboard principal)
/users/login/              → LoginView
/users/logout/             → logout_view
/discador/                 → AgentDashboardView (POST: cambiar_estado, obtener_lead, iniciar_llamada, finalizar_llamada, liberar_lead)
/discador/bases/           → BaseLlamadaListView
/discador/base/<int:pk>/   → BaseLlamadaDetailView
/discador/check-incoming/  → AJAX: verificar llamadas entrantes (poll cada 30s)
/ventas/                   → VentaListView
/ventas/<int:pk>/          → VentaDetailView
/ventas/nueva/             → VentaCreateView
/ventas/nueva/<int:base_llamada_id>/ → VentaCreateView (con base pre-cargada)
/ventas/buscar-cliente/    → AJAX: buscar cliente por documento
/ventas/validar-cliente/   → AJAX: validar existencia de cliente
/admin/                    → Panel de administración Django
```

**Control de acceso:**
- `LoginRequiredMixin` en todas las vistas protegidas
- Filtrado de `BaseLlamada` por rol en views:
  - `ADMIN`: ve todos los leads
  - `SUPERVISOR`: ve sus leads y los de sus agentes
  - `AGENTE`: ve solo sus propios leads
- `disponibilidad` controla flujo de agente: solo DISPONIBLE puede obtener leads

---

## 7. Configuración de Base de Datos

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

## 7. Dependencias

```
Django==4.2.13
PyMySQL==1.1.0
python-decouple==3.8
```

---

## 8. Comandos

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

## 8. Panel de Administración

Accesible en `http://localhost:8000/admin/`.

**Módulos disponibles:**
- **Usuarios** (`User`): gestión de usuarios con perfil inline (rol, código, supervisor, estado)
- **Perfiles de Usuario** (`UserProfile`): listado filtrable por activo, turno, zona; búsqueda por username y código
- **Bases de Llamada** (`BaseLlamada`): listado con filtros por es_callable, tipo_valido, fecha; búsqueda por teléfono, nombres, documento
- **Registros de Llamada** (`CallRecord`): historial con filtros por resultado, disposition, fecha
- **Ventas** (`Venta`): con inlines para ítems y seguimiento backoffice
- **Clientes** (`Cliente`): listado de clientes por documento
- **Ítems de Venta** (`ItemVenta`)
- **Seguimientos Backoffice** (`SeguimientoBO`)