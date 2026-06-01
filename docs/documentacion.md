# Documentación - Sistema de Gestión de Ventas

## 1. Descripción General

Sistema Django de gestión de ventas con dos módulos principales:

- **Módulo Discador**: Gestión de bases de llamadas con resultados de contacto
- **Módulo Ventas**: Registro de ventas con ítems y seguimiento backoffice

---

## 2. Entidades Principales

### 2.1 Módulo Discador

**Modelo: `BaseLlamada`** (`discador_base`)

Contactos de la base de discado con sus resultados de gestión.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `telefono` | CharField | Teléfono del contacto (PK implícita por ID) |
| `nombres` | CharField | Nombres del contacto |
| `paterno` | CharField | Apellido paterno |
| `materno` | CharField | Apellido materno |
| `correo` | EmailField | Email del contacto |
| `documento` | CharField | Número de documento |
| `numero_base` | CharField | Número de identificación en la base |
| `observaciones` | TextField | Notas adicionales |
| `es_callable` | CharField | ¿Es contactable? (Sí/No) |
| `fecha_gestion` | DateField | Fecha de gestión |
| `resultado_gestion` | CharField | Resultado del contacto |
| `tipo_valido` | CharField | Tipo de validación (Válido/Inválido/No definido) |
| `creado` | DateTimeField | Timestamp de creación |
| `actualizado` | DateTimeField | Timestamp de actualización |

---

### 2.2 Módulo Ventas

**Modelo: `Venta`** (`ventas_venta`)

Registro maestro de operaciones de venta.

**Subsecciones:**

#### Agente
- `agente_nombre`: Nombre del vendedor/agente

#### Cliente (Transitorio)
- `cliente_nombres`, `cliente_paterno`, `cliente_materno`
- `cliente_documento`, `cliente_numero`
- `cliente_telefono_1`, `cliente_telefono_2`

#### Recibo Electrónico
- `recibo_electronico`: Sí/No/Si desea/No desea
- `correo_electronico_recibo`
- `horario_visita`
- `clausulas`: Aceptación de cláusulas
- `abdcp`: Autorización para datos de portabilidad

#### Producto y Venta
- `producto_nombre` (deprecated → usar ItemVenta)
- `origen`, `operador`, `telefono_portar`
- `modelo_producto`, `plan_producto`
- `tipo_linea`: Prepago/Postpago/Línea nueva/Portabilidad
- `precio_venta`, `precio_plan`
- `tipo_pago`

#### Dirección de Despacho
- `tipo_via`, `nombre_via`, `numero_via`
- `manzana`, `interior`, `lote`, `piso`
- `zona_tipo`, `zona_nombre`, `zona_referencia`
- `departamento`, `provincia`, `distrito`

#### Backoffice/Resumen
- `base`, `tipo_renta`, `tipo_renta2`, `base3`
- `q_ventas`: Cantidad de ventas
- `fecha_venta`, `hora_venta`
- `facturacion_requerida`

---

**Modelo: `ItemVenta`** (`ventas_item`)

Desglose de productos/servicios en una venta (hasta 2 ítems).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | ForeignKey | Referencia a Venta (1:N) |
| `tipo_venta` | CharField | Tipo de venta asociada |
| `tipo_producto` | CharField | Tipo de producto/servicio |
| `precio_plan` | DecimalField | Precio del plan/producto |

---

**Modelo: `SeguimientoBO`** (`ventas_backoffice`)

Estado administrativo de la venta (backoffice, courier, supervisor).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `venta` | OneToOneField | Referencia a Venta (1:1) |
| `status_bo` | CharField | Estado Backoffice |
| `fecha_bo` | DateField | Fecha de estado BO |
| `sts_courier` | CharField | Estado del courier |
| `fch_courier` | DateField | Fecha de entrega/courier |
| `supervisor` | CharField | Nombre del supervisor |
| `intervalo` | CharField | Intervalo de tiempo |

---

## 3. Relaciones

```
Venta (1) ─────→ (N) ItemVenta
  │
  └─────→ (1) SeguimientoBO

BaseLlamada (futuro) ─────→ Venta (relación FK aún no implementada)
```

---

## 4. Estructura del Proyecto

```
gestion_ventas/
├── manage.py
├── venv/                      # Entorno virtual Python
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuración (BD, apps, etc.)
│   ├── urls.py               # URLs principales
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── discador/
│   │   ├── __init__.py
│   │   ├── models.py         # Modelo BaseLlamada
│   │   ├── admin.py          # Admin para BaseLlamada
│   │   ├── views.py          # Vistas
│   │   ├── urls.py           # URLs
│   │   └── tests.py          # Tests unitarios
│   └── ventas/
│       ├── __init__.py
│       ├── models.py         # Modelos Venta, ItemVenta, SeguimientoBO
│       ├── admin.py          # Admin para ventas
│       ├── views.py          # Vistas
│       ├── urls.py           # URLs
│       └── tests.py          # Tests unitarios
├── static/                   # Archivos estáticos (CSS, JS)
├── templates/                # Plantillas HTML
├── docs/
│   └── documentacion.md      # Esta documentación
└── db/
    └── (migraciones de BD)
```

---

## 5. Configuración de Base de Datos

**Motor:** MySQL/MariaDB  
**Nombre:** `gestion_ventas`  
**Usuario:** `ventas_user`  
**Contraseña:** `tu-password`  
**Host:** `192.169.18.59`  
**Puerto:** `3306`

### Crear Base de Datos y Usuario

Ver [db/README.md](../db/README.md) para instrucciones detalladas.

**Script SQL automatizado:**

```sql
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS gestion_ventas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario con permisos
CREATE USER IF NOT EXISTS 'ventas_user'@'%' IDENTIFIED BY 'tu-password';
GRANT ALL PRIVILEGES ON gestion_ventas.* TO 'ventas_user'@'%';
FLUSH PRIVILEGES;
```

### Configuración en `.env`:

```env
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=gestion_ventas
DATABASE_USER=ventas_user
DATABASE_PASSWORD=tu-password
DATABASE_HOST=192.169.18.59
DATABASE_PORT=3306
```

---

## 6. Comandos Útiles

### Activar entorno virtual
```bash
source venv/bin/activate
```

### Crear migraciones
```bash
python manage.py makemigrations
```

### Aplicar migraciones
```bash
python manage.py migrate
```

### Crear superusuario para admin
```bash
python manage.py createsuperuser
```

### Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

### Ejecutar tests
```bash
python manage.py test
```

---

## 7. Panel de Administración

Accesible en `http://localhost:8000/admin/` con credenciales de superusuario.

**Módulos disponibles:**
- Bases de Llamada (filtrable por fecha, tipo_valido)
- Ventas (filtrable por tipo_linea, fecha_venta)
- Ítems de Venta
- Seguimientos Backoffice

---

## 8. Notas de Desarrollo

- **ItemVenta**: Diseñada para hasta 2 ítems por venta (límite sugerido)
- **Cliente Transitorio**: Los datos se almacenan como texto en Venta hasta implementar entidad "Cliente"
- **BaseLlamada**: Sin FK directa a Venta aún; preparada para futura relación
- **Charset**: UTF8MB4 para soportar caracteres especiales y emojis

---

## 9. Dependencias

- Django 4.2.13
- PyMySQL 1.1.0

---

**Fecha de creación:** 1 de junio de 2026  
**Estado:** Proyecto inicial - estructura de modelos completada
