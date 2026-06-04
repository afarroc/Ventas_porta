# Deployment

## Configuración BD

```env
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=ventas_<timestamp>
DATABASE_USER=<tu-usuario>
DATABASE_PASSWORD=<tu-password>
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

## Inicio

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```