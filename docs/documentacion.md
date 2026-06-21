# Documentación - Sistema de Gestión de Ventas

Estado actual: 2026-06-20. Rama: `feature/catalogo-productos-retail`.

## 1. Descripción General

Sistema Django para gestión de ventas retail con trazabilidad Lead → Venta y flujo postventa por áreas.

### Módulos principales

- **Discador / WFM**: bases de llamadas, asignación de leads a agentes, llamadas, ACW, tipificación y dashboard agente.
- **Ventas**: registro de ventas con cliente, producto, portabilidad, precios, tipo de renta, ubigeo, items y validaciones frontend/backend.
- **Usuarios**: autenticación, perfiles de usuario, roles, disponibilidad, supervisión y estados operativos.
- **Postventa / BO**: seguimiento administrativo de ventas.
- **Despacho**: estado físico del despacho y tracking.
- **Courier**: estado de entrega por proveedor courier y tracking.
- **Catálogo Retail**: app opcional no registrada actualmente; la integración comercial se mantiene mediante fallback legacy.

## 2. Estado Actual del Proyecto

### Apps registradas

Apps registradas en `config/settings.py`:

```text
apps.discador
apps.ventas
apps.users
apps.postventa
apps.despacho
apps.courier
```

`apps.catalogo` existe en el repositorio, pero no está registrada en `INSTALLED_APPS`. Por eso la integración comercial debe ser opcional y tolerante a ausencia de la app.

### Cambios relevantes 2026-06-20

- `BaseLlamada.id_lead` cambió de `UUIDField` a `HexUUIDField` para compatibilidad con MySQL `char(32)`.
- Migración aplicada: `apps/discador/migrations/0011_alter_basellamada_id_lead.py`.
- `apps/ventas/catalogo_utils.py` consulta `apps.catalogo` solo si `apps.is_installed('apps.catalogo')` devuelve `True`.
- Endpoints de precio y validación usan catálogo primero y fallback legacy después.
- Se agregaron precios legacy:
  - `IPHONE_4S + ENTEL_75_CONTROL = 75`
  - `IPHONE_6_PLUS + ENTEL_75_CONTROL = 75`
- Se corrigió `prefetch_related('venta_set')` por `prefetch_related('ventas_asociadas')`.
- Se eliminó referencia rota a `{% url 'catalogo:index' %}` en `templates/home.html`.
- `VentaForm` maneja `BlankChoiceIterator` de Django 5.x reconstruyendo choices cuando no se puede hacer `append`.
- Botones de guardado:
  - `templates/ventas/venta_form.html`: `btnGuardarVentaFull`
  - `templates/ventas/venta_form_modal.html`: `btnGuardarVenta`
- El guardado queda bloqueado hasta validar Cliente y Producto.

### Validaciones ejecutadas

```bash
venv/bin/python manage.py check
venv/bin/python manage.py makemigrations --check --dry-run
```

Endpoint validado:

```text
GET /api/ventas/validar-producto/?origen=LINEA_NUEVA&producto=PACK&modelo=IPHONE_6_PLUS&plan=ENTEL_75_CONTROL&tipo_linea=POSTPAGO
```

Respuesta validada:

```json
{
  "ok": true,
  "precio": "75",
  "precio_plan": "75",
  "tipo_renta": "R.MEDIA",
  "catalogo": false,
  "oferta_id": null,
  "mensaje": "Producto PACK validado correctamente."
}
```

### Bloqueo conocido

`venv/bin/python manage.py test apps.discador --noinput` queda inestable por setup/teardown del test database MySQL:

```text
test_ventas_20260601
auth_user
users_profile
```

El bloqueo no está relacionado con el cambio de `id_lead`.

## 3. Mapa de Documentación

### Raíz `/`

| Archivo | Uso |
|---|---|
| `README.md` | Inicio rápido, estado actual, estructura y mapa de documentación. |
| `DEPLOYMENT.md` | Configuración de BD y arranque. |
| `HANDOFF_2026-06-11.md` | Fix de ubigeo. |

### `docs/`

| Archivo | Uso |
|---|---|
| `docs/INDICE.md` | Índice y orden de lectura. |
| `docs/documentacion.md` | Documentación principal. |
| `docs/HISTORIAL.md` | Registro cronológico de cambios. |
| `docs/DEV_REFERENCE.md` | Referencia técnica de arquitectura, apps separadas, servicios y signals. |
| `docs/queries_referenciadas.md` | Queries de trazabilidad Lead → Venta y postventa. |
| `docs/HANDOFF_2026-06-05_ventas.md` | Handoff de ventas. |
| `docs/HANDOFF_2026-06-06_venta_refactor.md` | Refactor del modelo Venta. |
| `docs/HANDOFF_2026-06-07_apps_separacion.md` | Separación de apps postventa, despacho y courier. |
| `docs/HANDOFF_2026-06-07_trazabilidad.md` | Trazabilidad Lead → Venta. |
| `docs/HANDOFF_2026-06-08_estado_actual.md` | Estado de sprints, bugs críticos y reglas retail. |
| `docs/HANDOFF_2026-06-10_modelo_venta_refactor.md` | Refactor del modelo Venta. |

Orden recomendado:

1. `README.md`
2. `docs/INDICE.md`
3. `docs/documentacion.md`
4. `docs/HISTORIAL.md`
5. `docs/DEV_REFERENCE.md`
6. `docs/queries_referenciadas.md`
7. Handoffs por fecha.

## 4. Entidades Principales

### 4.1 Módulo Discador

#### Modelo `BaseLlamada` (`discador_base`)

Contactos de la base de discado con resultados de gestión y trazabilidad hacia venta.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | AutoField | Identificador interno autoincremental. |
| `id_lead` | `HexUUIDField` | UUID almacenado en hex como `char(32)` compatible con MySQL. |
| `telefono` | CharField | Teléfono único. |
| `nombres` | CharField | Nombres del contacto. |
| `paterno` | CharField | Apellido paterno. |
| `materno` | CharField | Apellido materno. |
| `correo` | EmailField | Correo. |
| `documento` | CharField | DNI, RUT u otra identificación. |
| `observaciones` | TextField | Notas de base. |
| `contact_callable` | CharField | Contacto llamable: `0` No, `1` Sí. |
| `ultimo_intento` | CharField | Último intento registrado en CRM. |
| `ultimo_resultado_crm` | CharField | Último resultado en CRM. |
| `es_callable` | CharField | Es callable: `0` No, `1` Sí. |
| `fecha_gestion` | DateField | Fecha de gestión. |
| `hora_gestion` | TimeField | Hora de gestión. |
| `resultado_gestion` | CharField | `SIN_GESTION`, `GESTIONADO`, `VENTA_CONVERTIDA`. |
| `tipo_contacto` | CharField | Tipo de contacto. |
| `tipo_valido` | CharField | `Válido`, `Inválido`, vacío. |
| `status_java` | CharField | Status JAVA. |
| `supervisor_nombre` | CharField | Supervisor. |
| `base_procedencia` | CharField | Base de procedencia: `POT`, `RSG_01`. |
| `base_manual` | BooleanField | Lead cargado manualmente. |
| `venta` | ForeignKey(`ventas.Venta`) | Venta asociada, related_name `lead_venta`. |
| `creado` | DateTimeField | Timestamp de creación. |
| `actualizado` | DateTimeField | Timestamp de actualización. |

#### Modelo `CallRecord`

Registro individual de llamada.

| Campo | Tipo | Descripción |
|---|---|---|
| `agente` | ForeignKey(User) | Agente que realizó la llamada. |
| `base_llamada` | ForeignKey(BaseLlamada) | Lead asociado. |
| `inicio` | DateTimeField | Inicio de llamada. |
| `fin` | DateTimeField | Fin de llamada. |
| `duracion` | DurationField | `fin - inicio`. |
| `resultado` | CharField | Contestada, no contestada, ocupada, desconectada, no voz, fax, otro, liberado sin uso. |
| `observaciones` | TextField | Observaciones del agente. |
| `acw_start` | DateTimeField | Inicio de ACW. |
| `acw_end` | DateTimeField | Fin de ACW. |
| `disposition` | CharField | Tipificación. |
| `liberado_sin_uso` | BooleanField | Lead liberado sin gestión. |

### 4.2 Módulo Usuarios

#### Modelo `UserProfile` (`users_profile`)

Perfil extendido de `User`.

| Campo | Tipo | Descripción |
|---|---|---|
| `user` | OneToOneField(User) | Usuario Django. |
| `rol` | CharField | Agente, Supervisor, Administrador. |
| `codigo_agente` | CharField | Código de agente. |
| `telefono` | CharField | Teléfono de usuario. |
| `supervisor` | ForeignKey(self) | Supervisor jerárquico. |
| `zona` | CharField | Zona de trabajo. |
| `turno` | CharField | Diurno, nocturno, híbrido. |
| `activo` | BooleanField | Usuario activo. |
| `estado` | CharField | Activo, inactivo, baja, vacaciones. |
| `disponibilidad` | CharField | Disponible, pausa, no listo, en llamada, coach. |

### 4.3 Módulo Ventas

#### Modelo `Cliente` (`ventas_cliente`)

Cliente maestro con documento único.

| Campo | Tipo | Descripción |
|---|---|---|
| `tipo_documento` | CharField | DNI, RUC, CE, Pasaporte. |
| `documento` | CharField | Documento único. |
| `nombres` | CharField | Nombres. |
| `paterno` | CharField | Apellido paterno. |
| `materno` | CharField | Apellido materno. |
| `telefono_1` | CharField | Teléfono principal. |
| `telefono_2` | CharField | Teléfono secundario. |
| `activo` | BooleanField | Cliente activo. |

#### Modelo `Venta` (`ventas_venta`)

Registro maestro de operaciones de venta.

Secciones del formulario:

| Sección | Campos principales |
|---|---|
| Agente | `agente` |
| Cliente | `cliente`, campos de búsqueda/registro, `cliente_validado` |
| Recibo Electrónico | `recibo_electronico`, `correo_electronico_recibo`, `horario_visita`, `clausulas`, `abdcp` |
| Producto y Venta | `producto_nombre`, `origen`, `operador`, `telefono_portar`, `modelo_producto`, `plan_producto`, `precio_venta`, `precio_plan`, `tipo_linea`, `tipo_renta`, `producto_validado` |
| Dirección de Despacho | `tipo_via`, `nombre_via`, `numero_via`, ubigeo, zona, referencia |
| Facturación | `facturacion_requerida` |
| Items | `ItemVenta` en relación 1:N |
| Postventa | `SeguimientoBO`, `EstadoDespacho`, `EstadoCourier` |

### 4.4 Módulo Postventa

#### Recibo Electrónico
- `recibo_electronico`: Sí/No/Si desea/No desea
- `correo_electronico_recibo`, `horario_visita`
- `clausulas`: Aceptación de cláusulas
- `abdcp`: Autorización para datos de portabilidad

#### Producto y Venta
- `producto_nombre`: `CHIP` o `PACK`
- `origen`: PORTABILIDAD (requiere operador y telefono_portar) o LINEA_NUEVA
- `operador`: Claro/Movistar/Viettel/Virgin (obligatorio si origen=PORTABILIDAD)
- `telefono_portar`: Número a portar (obligatorio si origen=PORTABILIDAD)
- `modelo_producto`: Modelo de equipo solo para `PACK`; para `CHIP` debe estar vacío o `'0'` y se normaliza a vacío
- `plan_producto`: Plan ENTEL obligatorio. Para `CHIP` solo planes `ENTEL_CHIP_*`; para `PACK` puede ser CONTROL, CHIP o LIBRE
- `precio_plan`: Precio del plan (readonly, determinado por plan_producto)
- `precio_venta`: Precio de venta determinado por regla canónica
- `tipo_linea`: Postpago (default) o Prepago; no condiciona modelo ni plan, pero sí condiciona precio en `PACK`
- `tipo_renta`: R.BAJA/R.MEDIA/R.ALTA (calculado automáticamente)

**Regla canónica de precio:**

| Producto | tipo_linea | Precio de venta |
|----------|------------|-----------------|
| `CHIP` | cualquiera | `1` fijo |
| `PACK` | `POSTPAGO` | matriz `modelo_producto + plan_producto` |
| `PACK` | `PREPAGO` | precio fijo por `modelo_producto` |

**Endpoint de precio:**

- `GET /api/ventas/precio-venta/?producto=PACK&modelo=MOTO_G_PLAY&plan=ENTEL_CONTROL_49_CONTROL&tipo_linea=POSTPAGO`
- Retorna `{"ok": true, "precio": 49}` si existe precio definido.
- Retorna `{"ok": false, "mensaje": "..."}` si falta dato o no existe combinación.
- La validación definitiva está en backend (`apps/ventas/forms.py` y `apps/ventas/models.py`); el frontend solo sincroniza selects y tipo de renta.

**Endpoint de validación de Producto y Venta:**

- `GET /api/ventas/validar-producto/?origen=LINEA_NUEVA&producto=PACK&modelo=MOTO_G_PLAY&plan=ENTEL_CONTROL_49_CONTROL&tipo_linea=POSTPAGO`
- Retorna `ok=true`, `precio`, `precio_plan`, `tipo_renta` y `mensaje` cuando la combinación es válida.
- Retorna `ok=false`, `campo` y `mensaje` cuando falta operador/teléfono en portabilidad, modelo de equipo en PACK, plan válido, o cuando no existe precio/tipo_renta definido.
- El botón **Validar Producto** del formulario llama a este endpoint y bloquea **Guardar Venta** hasta que Cliente y Producto estén validados.

**Regla canónica de `tipo_renta`:**

`tipo_renta` se calcula desde una tabla explícita llave-valor definida en `apps/ventas/models.py` y replicada en `static/js/venta-form.js`.

- Para `CHIP`, el valor de la llave es `precio_plan`.
- Para `PACK`, el valor de la llave es `precio_venta`.
- Si una combinación no existe en backend, se lanza `ValueError`.
- En frontend, si no existe mapping, el campo queda vacío; actualmente todas las combinaciones reales de precio definidas en las matrices están cubiertas.

| Origen | Producto | Valores con R.BAJA | Valores con R.MEDIA | Valores con R.ALTA |
|--------|----------|-------------------|--------------------|-------------------|
| `PORTABILIDAD` | `PACK` | 1, 4, 9, 13, 29, 49 | 74, 75, 89 | 99, 129, 149, 189, 199, 229, 249, 299, 349, 399, 599, 699 |
| `PORTABILIDAD` | `CHIP` | 25, 29, 39, 45, 49 | 59, 74, 75, 89 | 99, 109, 145, 209 |
| `LINEA_NUEVA` | `PACK` | 1, 4, 9, 13, 29, 49 | 75, 89 | 99, 129, 149, 189, 199, 229, 249, 299, 349, 399, 599, 699 |
| `LINEA_NUEVA` | `CHIP` | 25, 29, 39, 45 | 59, 74, 89 | 109, 145, 209 |

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
#### Modelo `SeguimientoBO` (`postventa_seguimientobo`)

| Campo | Tipo | Descripción |
|---|---|---|
| `venta` | OneToOneField | Venta relacionada. |
| `status_bo` | CharField | `EN_BASE`, `PDTE_BO`, `EN_BO`, `VALIDADO`, `EN_DESPACHO`, `DESPACHADO`. |
| `fecha_bo` | DateField | Fecha de cambio BO. |
| `supervisor` | CharField | Supervisor. |
| `observaciones` | TextField | Notas. |
| `creado` | DateTimeField | Timestamp de creación. |
| `actualizado` | DateTimeField | Timestamp de actualización. |

#### Modelo `HistorialEstado` (`postventa_historial`)

Registra cambios de estado en BO, despacho y courier.

| Campo | Tipo | Descripción |
|---|---|---|
| `venta` | ForeignKey | Venta relacionada. |
| `area` | CharField | `BO`, `DESPACHO`, `COURIER`. |
| `estado_anterior` | CharField | Estado anterior. |
| `estado_nuevo` | CharField | Estado nuevo. |
| `usuario` | ForeignKey(User) | Usuario que realizó el cambio. |
| `fecha_cambio` | DateTimeField | Timestamp del cambio. |
| `observaciones` | TextField | Notas. |

### 4.5 Módulo Despacho

#### Modelo `Proveedor` (`despacho_proveedor`)

Proveedor de despacho.

#### Modelo `EstadoDespacho` (`despacho_estado`)

| Campo | Tipo | Descripción |
|---|---|---|
| `venta` | OneToOneField | Venta relacionada. |
| `etapa` | CharField | `EN_BASE`, `PDTE_DESPACHO`, `EN_PREPARACION`, `EN_TRANSITO`, `ENTREGADO`, `RECHAZADO`. |
| `fecha_etapa` | DateField | Fecha de etapa. |
| `proveedor` | ForeignKey | Proveedor. |
| `tracking` | CharField | Tracking único por venta entre despacho y courier. |
| `observaciones` | TextField | Notas. |

### 4.6 Módulo Courier

#### Modelo `ProveedorCourier` (`courier_proveedor`)

Proveedor de courier.

#### Modelo `EstadoCourier` (`courier_estado`)

| Campo | Tipo | Descripción |
|---|---|---|
| `venta` | OneToOneField | Venta relacionada. |
| `sts_courier` | CharField | `PDTE_BO`, `EN_RUTA`, `ENTREGADO`, `RECHAZADO`. |
| `fch_courier` | DateField | Fecha de estado. |
| `proveedor` | ForeignKey | Proveedor courier. |
| `tracking` | CharField | Tracking. |
| `observaciones` | TextField | Notas. |

### 4.7 Módulo Catálogo Retail

`apps.catalogo` existe, pero no está registrada en `config/settings.py`.

#### Modelos

| Modelo | Tabla | Uso |
|---|---|---|
| `Producto` | `catalogo_producto` | Productos/equipos/chips. |
| `ProveedorCatalogo` | `catalogo_proveedor` | Proveedores comerciales. |
| `Oferta` | `catalogo_oferta` | Oferta por producto, proveedor, plan, tipo de línea y origen. |
| `ChipCompatibilidad` | `catalogo_chip_compatibilidad` | Compatibilidad equipo/chip. |

#### Endpoints si la app está registrada

| Endpoint | Método | Descripción |
|---|---|---|
| `/api/catalogo/productos/` | GET | Productos con ofertas. |
| `/api/catalogo/productos/{sku}/ofertas/` | GET | Ofertas por producto. |
| `/api/catalogo/equipos/{sku}/chips/` | GET | Chips compatibles. |
| `/api/catalogo/ofertas/validar/` | POST | Validar oferta. |

#### Integración actual

- `apps/ventas/catalogo_utils.py` expone:
  - `obtener_oferta_catalogo_para_venta()`
  - `precio_plan_legacy()`
  - `PLAN_PRECIO_MAP`
- Si `apps.catalogo` no está instalada, `obtener_oferta_catalogo_para_venta()` retorna `None`.
- Los endpoints de ventas usan fallback legacy cuando no hay oferta comercial.

## 5. Relaciones

```text
Venta (1) ─────→ (N) ItemVenta
  │
  ├─────→ (1) SeguimientoBO          [BO]
  ├─────→ (1) EstadoDespacho         [Despacho]
  ├─────→ (1) EstadoCourier          [Courier]
  ├─────→ (1) Cliente
  └─────→ (0..1) BaseLlamada

BaseLlamada (1) ─────→ (N) CallRecord
BaseLlamada (0..1) ───→ (1) Venta

User (1) ─────→ (1) UserProfile
UserProfile (1) ────→ (N) UserProfile supervisados
UserProfile (1) ────→ (N) CallRecord
Proveedor (1) ─────→ (N) EstadoDespacho
ProveedorCourier (1) ─→ (N) EstadoCourier
```

## 6. Arquitectura por Áreas

```text
Lead (BaseLlamada) ────────── discador / WFM
        │
        ▼
Venta (Operaciones) ───────── ventas
        │
        ├── BO ────────────── SeguimientoBO
        ├── Despacho ─────── EstadoDespacho
        └── Courier ──────── EstadoCourier
```

| Área | App | Modelos principales | Función |
|---|---|---|---|
| WFM / Discador | `apps.discador` | `BaseLlamada`, `CallRecord` | Gestión de leads y llamadas. |
| Operaciones | `apps.ventas` | `Venta`, `ItemVenta`, `Cliente` | Registro de venta y cliente. |
| BO | `apps.postventa` | `SeguimientoBO`, `HistorialEstado` | Validación administrativa. |
| Despacho | `apps.despacho` | `Proveedor`, `EstadoDespacho` | Preparación, tránsito y entrega física. |
| Courier | `apps.courier` | `ProveedorCourier`, `EstadoCourier` | Estado de entrega por proveedor courier. |
| Catálogo | `apps.catalogo` | `Producto`, `Oferta`, `ProveedorCatalogo` | Catálogo comercial opcional. |

## 7. Estructura del Proyecto

```text
Ventas_Porta/
├── manage.py
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── HANDOFF_2026-06-11.md
├── .env.example
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── discador/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── migrations/0011_alter_basellamada_id_lead.py
│   ├── users/
│   ├── ventas/
│   │   ├── models.py
│   │   ├── forms.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── ubigeo_peru.py
│   │   ├── catalogo_utils.py
│   │   └── tests.py
│   ├── postventa/
│   ├── despacho/
│   └── courier/
├── docs/
│   ├── INDICE.md
│   ├── documentacion.md
│   ├── HISTORIAL.md
│   ├── DEV_REFERENCE.md
│   ├── queries_referenciadas.md
│   └── HANDOFF_*.md
├── static/
│   ├── js/venta-form.js
│   ├── css/form-data.css
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
└── venv/
```

## 8. Detalles por Archivo

### `config/__init__.py`

Instala PyMySQL como driver MySQLdb para Django.

### `config/settings.py`

Carga configuración desde `.env`, usa MySQL/MariaDB, charset `utf8mb4`, `LANGUAGE_CODE='es-pe'` y registra apps operativas. No registra `apps.catalogo`.

### `config/urls.py`

Incluye URLs raíz de `ventas`, `discador` y `users`. No incluye namespace `catalogo`.

### `apps/discador/models.py`

Define `HexUUIDField` y modelos `BaseLlamada`, `CallRecord`.

### `apps/discador/migrations/0011_alter_basellamada_id_lead.py`

Cambia `BaseLlamada.id_lead` a `HexUUIDField`.

### `apps/discador/views.py`

Incluye:

- `BaseLlamadaListView`
- `BaseLlamadaDetailView`
- `AgentDashboardView`
- `ResultadoDiscadoListView`
- `ResultadoDiscadoDetailView`

`ResultadoDiscadoListView` y `ResultadoDiscadoDetailView` usan `prefetch_related('ventas_asociadas')`.

### `apps/ventas/models.py`

Define `Cliente`, `Venta`, `ItemVenta`, matrices de precios, planes, modelos y `TIPO_RENTA_TABLE`.

### `apps/ventas/forms.py`

`VentaForm` implementa:

- búsqueda/registro de cliente
- validación de producto y venta
- integración con catálogo opcional
- fallback legacy
- normalización de `modelo_producto='0'`
- manejo de `BlankChoiceIterator`
- validación de portabilidad
- validación de recibo electrónico
- validación multilínea
- validación de cliente existente

### `apps/ventas/views.py`

Endpoints principales:

- `/ventas/buscar-cliente/`
- `/ventas/validar-cliente/`
- `/ventas/recargar-lead/<uuid:id_lead>/`
- `/ventas/modal/<uuid:id_lead>/`
- `/api/ventas/crear/<uuid:id_lead>/`
- `/api/ventas/precio-venta/`
- `/api/ventas/validar-producto/`

### `apps/ventas/catalogo_utils.py`

Capa de integración comercial:

- retorna `None` si `apps.catalogo` no está instalada
- consulta `Oferta` si está disponible
- mantiene fallback legacy mediante `PLAN_PRECIO_MAP`

### `apps/ventas/ubigeo_peru.py`

Genera `DEPTO_CHOICES`, `PROV_CHOICES` y `DISTRITOS_CHOICES` desde `static/data/ubigeo-peru.json`.

### `static/js/venta-form.js`

Implementa:

- búsqueda y registro de cliente
- validación de cliente
- validación de producto
- sincronización de campos ocultos
- bloqueo/desbloqueo de guardar
- carga de ubigeo Perú
- normalización de precios

### `templates/ventas/venta_form.html`

Formulario completo de nueva venta. Usa `btnGuardarVentaFull`.

### `templates/ventas/venta_form_modal.html`

Formulario modal de venta. Usa `btnGuardarVenta`.

### `templates/home.html`

Dashboard principal. No contiene enlaces al namespace `catalogo`.

## 9. Flujo de Trabajo del Agente

### Estados de disponibilidad

| Estado | Uso |
|---|---|
| `DISPONIBLE` | Puede obtener leads y contestar llamadas. |
| `PAUSA` | No disponible para llamadas. |
| `LISTO_NO` | Llamada finalizada, pendiente tipificación. |
| `EN_LLAMADA` | Llamada en curso. |
| `COACH` | En coaching/entrenamiento. |

### Transiciones

```text
DISPONIBLE → Obtener Lead → lead asignado
DISPONIBLE → Llamada entrante → EN_LLAMADA
EN_LLAMADA → Finalizar → LISTO_NO
LISTO_NO → Tipificar → DISPONIBLE
LISTO_NO → Liberar Lead → DISPONIBLE + auditoría
```

### Obtención de lead

Reglas actuales:

- el agente debe estar `DISPONIBLE`
- no debe existir `current_lead_id`
- no debe existir llamada en curso
- se excluyen leads ya gestionados por el agente
- se excluyen leads con `resultado_gestion='VENTA_CONVERTIDA'`

`current_lead_id` almacena `str(lead.id_lead)`, es decir, UUID en formato hex.

## 10. Flujo Postventa por Áreas

```text
Venta registrada
    │
    ▼
BO
EN_BASE → PDTE_BO → EN_BO → VALIDADO → EN_DESPACHO → DESPACHADO
    │
    ├── Despacho
    │   PDTE_DESPACHO → EN_PREPARACION → EN_TRANSITO → ENTREGADO / RECHAZADO
    │
    └── Courier
        PDTE_BO → EN_RUTA → ENTREGADO / RECHAZADO
```

Reglas:

1. `EstadoDespacho` requiere `SeguimientoBO.status_bo` en `VALIDADO` o `EN_DESPACHO`.
2. `EstadoCourier` requiere `SeguimientoBO.status_bo == 'DESPACHADO'`.
3. `tracking` no debe duplicarse entre despacho y courier de la misma venta.
4. `HistorialEstado` registra cambios de estado.

## 11. Rutas y API Endpoints

### URLs principales

```text
/                                      → HomeView
/users/login/                          → LoginView
/users/logout/                         → logout_view
/discador/                             → AgentDashboardView
/discador/bases/                       → BaseLlamadaListView
/discador/base/<int:pk>/               → BaseLlamadaDetailView
/ventas/                               → VentaListView
/ventas/<int:pk>/                      → VentaDetailView
/ventas/nueva/                         → VentaCreateView
/ventas/nueva/<uuid:id_lead>/          → VentaCreateView con lead pre-cargado
/ventas/backoffice/                    → BackofficeListView
/postventa/                            → Dashboard BO
/postventa/backoffice/                 → BackofficeListView
/postventa/backoffice/venta/<int:venta_id>/ → SeguimientoBOCreateView
/postventa/backoffice/<int:pk>/editar/ → SeguimientoBOUpdateView
/postventa/dashboard/conversion/       → DashboardConversionView
/postventa/despacho/venta/<int:venta_id>/ → EstadoDespachoCreateView
/postventa/despacho/venta/<int:pk>/editar/ → EstadoDespachoUpdateView
/postventa/courier/venta/<int:venta_id>/ → EstadoCourierCreateView
/postventa/courier/venta/<int:pk>/editar/ → EstadoCourierUpdateView
/admin/                                → Admin
```

### API endpoints

| Endpoint | Method | Descripción |
|----------|--------|-----------|
| `/ventas/buscar-cliente/` | GET | Busca cliente por tipo_documento + documento |
| `/ventas/validar-cliente/` | GET | Valida existencia de cliente |
| `/ventas/recargar-lead/<uuid>/` | GET | Recarga datos del lead |
| `/ventas/modal/<uuid>/` | GET | HTML formulario modal vía API |
| `/api/ventas/crear/<uuid>/` | POST | Crea venta vía API JSON |
| `/api/ventas/precio-venta/` | GET | Obtiene precio de venta según reglas canónicas |
| `/api/ventas/validar-producto/` | GET | Valida Producto y Venta; retorna precio, precio_plan y tipo_renta calculados |
| `/api/ubigeo/provincias/` | GET | Obtiene provincias por departamento (AJAX) |
| `/api/ubigeo/distritos/` | GET | Obtiene distritos por departamento+provincia (AJAX) |
| Endpoint | Método | Descripción |
|---|---|---|
| `/ventas/buscar-cliente/` | GET | Busca cliente por tipo de documento y documento. |
| `/ventas/validar-cliente/` | GET | Valida existencia de cliente. |
| `/ventas/registrar-cliente/<uuid:id_lead>/` | POST | Registra cliente sin crear venta. |
| `/ventas/recargar-lead/<uuid:id_lead>/` | GET | Recarga datos del lead. |
| `/ventas/modal/<uuid:id_lead>/` | GET | Renderiza formulario modal de venta. |
| `/api/ventas/crear/<uuid:id_lead>/` | POST | Crea venta vía API JSON. |
| `/api/ventas/precio-venta/` | GET | Obtiene precio de venta. |
| `/api/ventas/validar-producto/` | GET | Valida Producto y Venta. |
| `/api/ubigeo/provincias/` | GET | Obtiene provincias por departamento. |
| `/api/ubigeo/distritos/` | GET | Obtiene distritos por departamento y provincia. |
| `/api/venta/<int:pk>/trazabilidad/` | GET | Retorna trazabilidad de venta, lead, BO, despacho, courier e historial. |

## 12. Validación de Producto y Venta

### Endpoint de precio

```text
GET /api/ventas/precio-venta/?producto=PACK&modelo=MOTO_G_PLAY&plan=ENTEL_CONTROL_49_CONTROL&tipo_linea=POSTPAGO&origen=LINEA_NUEVA
```

Respuesta exitosa:

```json
{
  "ok": true,
  "precio": 49,
  "precio_plan": 49,
  "catalogo": false
}
```

### Endpoint de validación

```text
GET /api/ventas/validar-producto/?origen=LINEA_NUEVA&producto=PACK&modelo=MOTO_G_PLAY&plan=ENTEL_CONTROL_49_CONTROL&tipo_linea=POSTPAGO
```

Respuesta exitosa:

```json
{
  "ok": true,
  "precio": "49",
  "precio_plan": "49",
  "tipo_renta": "R.BAJA",
  "catalogo": false,
  "oferta_id": null,
  "mensaje": "Producto PACK validado correctamente."
}
```

### Validaciones frontend

`static/js/venta-form.js`:

- `validarProducto()` llama a `/api/ventas/validar-producto/`
- sincroniza campos ocultos:
  - `id_precio_venta`
  - `id_precio_plan`
  - `id_tipo_renta`
  - `id_tipo_linea`
- marca `producto_validado=true`
- llama `actualizarSubmitVenta()`
- bloquea guardar si Cliente o Producto no están validados

### Validaciones backend

`VentaForm.clean()`:

- valida documento de cliente
- valida cliente existente o registrado previamente
- valida portabilidad
- valida `CHIP`
- valida `PACK`
- valida tipo de línea
- valida recibo electrónico
- valida multilínea
- evita registrar venta si el lead ya fue `VENTA_CONVERTIDA`

## 13. Reglas de Negocio Retail

### Precio

| Producto | Tipo de línea | Regla |
|---|---|---|
| `CHIP` | cualquiera | `precio_venta = 1`, sin modelo, plan obligatorio. |
| `PACK` | `POSTPAGO` | `precio_venta = PRECIOS_POSTPAGO[(modelo, plan)]`. |
| `PACK` | `PREPAGO` | `precio_venta = PRECIOS_PREPAGO[modelo]`. |

### Planes CHIP

`PLANES_CHIP`:

```text
ENTEL_CHIP_29_CONTROL
ENTEL_CHIP_39_CONTROL
ENTEL_CHIP_45_CONTROL
ENTEL_CHIP_59_CONTROL
ENTEL_CHIP_74_CONTROL
ENTEL_CHIP_89_CONTROL
ENTEL_CHIP_109_CONTROL
ENTEL_CHIP_145_CONTROL
```

### Mapa legacy de precio de plan

`PLAN_PRECIO_MAP`:

| Plan | Precio |
|---|---:|
| `ENTEL_CHIP_29_CONTROL` | 29 |
| `ENTEL_CHIP_39_CONTROL` | 39 |
| `ENTEL_CHIP_45_CONTROL` | 45 |
| `ENTEL_CHIP_59_CONTROL` | 59 |
| `ENTEL_CHIP_74_CONTROL` | 74 |
| `ENTEL_CHIP_89_CONTROL` | 89 |
| `ENTEL_CHIP_109_CONTROL` | 109 |
| `ENTEL_CHIP_145_CONTROL` | 145 |
| `ENTEL_CONTROL_49_CONTROL` | 49 |
| `ENTEL_CONTROL_75_CONTROL` | 75 |
| `ENTEL_CONTROL_99_CONTROL` | 99 |
| `ENTEL_CONTROL_149_CONTROL` | 149 |
| `ENTEL_CONTROL_199_CONTROL` | 199 |
| `ENTEL_75_CONTROL` | 75 |
| `ENTEL_LIBRE_149_LIBRE` | 149 |
| `ENTEL_LIBRE_99_LIBRE` | 99 |
| `PREPAGO` | 0 |

### Tipo de renta

| Origen | Producto | Precio usado | R.BAJA | R.MEDIA | R.ALTA |
|---|---|---|---|---|---|
| `PORTABILIDAD` | `PACK` | `precio_venta` | 1, 4, 9, 13, 29, 49 | 74, 75, 89 | 99+ |
| `PORTABILIDAD` | `CHIP` | `precio_plan` | 25, 29, 39, 45, 49 | 59, 74, 75, 89 | 99, 109, 145, 209 |
| `LINEA_NUEVA` | `PACK` | `precio_venta` | 1, 4, 9, 13, 29, 49 | 75, 89 | 99+ |
| `LINEA_NUEVA` | `CHIP` | `precio_plan` | 25, 29, 39, 45 | 59, 74, 89 | 109, 145, 209 |

## 14. Configuración de Base de Datos

```env
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=<nombre_bd>
DATABASE_USER=<usuario>
DATABASE_PASSWORD=<password>
DATABASE_HOST=<host>
DATABASE_PORT=3306
```

Configuración:

- Motor: MySQL/MariaDB
- Charset: `utf8mb4`
- `BaseLlamada.id_lead`: hex UUID compatible con `char(32)`

## 15. Dependencias

```text
Django==4.2.13
PyMySQL==1.1.0
python-decouple==3.8
```

## 16. Comandos

```bash
# Entorno
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Migraciones
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations --check --dry-run

# Validación
python manage.py check

# Superusuario
python manage.py createsuperuser

# Servidor
python manage.py runserver

# Tests
python manage.py test
```

## 17. Panel de Administración

URL: `http://localhost:8000/admin/`.

Módulos disponibles:

- Usuarios
- Perfiles de Usuario
- Bases de Llamada
- Registros de Llamada
- Ventas
- Clientes
- Seguimiento BO
- Estado Despacho
- Estado Courier
- Proveedores

## 18. Trazabilidad Lead → Venta

Relaciones:

- `Venta.base_llamada` → `BaseLlamada`
- `BaseLlamada.venta` → `Venta`
- related_name de `Venta` hacia `BaseLlamada`: `ventas_asociadas`
- related_name de `BaseLlamada` hacia `Venta`: `lead_venta`

Queries:

```python
venta = Venta.objects.select_related(
    'base_llamada', 'cliente'
).prefetch_related(
    'bo_seguimiento', 'despacho_estado', 'courier_estado'
).get(id=venta_id)

base = BaseLlamada.objects.select_related('venta').prefetch_related(
    'venta__bo_seguimiento',
    'venta__despacho_estado',
    'venta__courier_estado'
).get(id_lead=uuid_val)
```

## 19. Dashboard de Conversión

URL:

```text
/postventa/dashboard/conversion/
```

Métricas:

| Métrica | Fórmula |
|---|---|
| Total Leads | `COUNT(BaseLlamada)` |
| Total Ventas | `COUNT(Venta)` |
| Leads Convertidos | Leads con `venta` |
| Tasa Conversión | Leads convertidos / total leads |

Query base:

```python
BaseLlamada.objects.values('base_procedencia').annotate(
    total=Count('id'),
    con_venta=Count('venta', distinct=True),
    sin_venta=Count('id', filter=Q(venta__isnull=True))
).order_by('-total')
```

## 20. Validaciones y Pruebas

### Validaciones recomendadas

```bash
venv/bin/python manage.py check
venv/bin/python manage.py makemigrations --check --dry-run
```

### Pruebas conocidas

`apps.discador` queda bloqueada por inestabilidad del test database MySQL:

```text
test_ventas_20260601
auth_user
users_profile
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

### 19.2 Regla canónica de precio

| Producto | tipo_linea | Regla |
|----------|------------|-------|
| `CHIP` | cualquiera | `precio_venta = 1`, `modelo_producto` vacío o `'0'`, `plan_producto` obligatorio y solo `ENTEL_CHIP_*` |
| `PACK` | `POSTPAGO` | `modelo_producto` obligatorio y no chip; `plan_producto` obligatorio; `precio_venta = matriz(modelo, plan)` |
| `PACK` | `PREPAGO` | `modelo_producto` obligatorio y no chip; `plan_producto` obligatorio; `precio_venta = precio fijo por modelo` |

`tipo_linea` no condiciona modelo ni plan, pero sí condiciona la regla de precio cuando `producto_nombre = PACK`.

Para `CHIP`, `tipo_renta` se calcula con `precio_plan`, no con `precio_venta`.

### 19.3 Validaciones Implementadas

1. **Producto CHIP**: sin modelo de equipo, precio fijo S/. 1, plan obligatorio solo `ENTEL_CHIP_*`
2. **Producto PACK**: modelo de equipo obligatorio, plan obligatorio, precio por matriz postpago o prepago según `tipo_linea`
3. **Origen PORTABILIDAD**: operador y teléfono_portar obligatorios
4. **Tipo documento**: DNI/RUC/CE/Pasaporte
5. **Recibo electrónico**: Si 'SI_DESEA', correo obligatorio
6. **Tipo renta multilínea**: Si `multiples_lineas=True`, se requiere `tipo_renta2`
7. **Tracking único**: No se permite duplicar tracking entre despacho y courier de la misma venta
8. **Lead VENTA_CONVERTIDA**: No se puede asignar a agentes en discador
9. **Calcular tipo_renta actualizado**: rangos definidos según §19.1
10. **Validación frontend de Producto y Venta**: botón **Validar Producto** consulta `/api/ventas/validar-producto/`, sincroniza `precio_venta`, `precio_plan` y `tipo_renta`, marca `producto_validado=true`, y mantiene bloqueado **Guardar Venta** hasta validar Cliente y Producto.

### 19.4 Validaciones Pendientes

1. Confirmar opciones de `MODELOS_PRODUCTO` con catálogo ENTEL actual
2. Verificar precios de venta y plan correspondientes al portafolio vigente
3. Completar matrices comerciales `PRECIOS_POSTPAGO` y `PRECIOS_PREPAGO` con todos los casos vigentes

### Pendientes

- Confirmar portafolio ENTEL 2026 con área comercial.
- Completar matrices `PRECIOS_POSTPAGO` y `PRECIOS_PREPAGO` con todos los casos vigentes.
- Registrar `apps.catalogo` solo cuando la app esté lista para producción.
- Completar tests estables para `apps.discador`.
