import json
from pathlib import Path

# Cargar ubigeo desde JSON (única fuente de verdad)
_JSON_PATH = Path(__file__).parent.parent.parent / 'static' / 'data' / 'ubigeo-peru.json'
with open(_JSON_PATH, 'r', encoding='utf-8') as _f:
    _UBIGEO_DATA = json.load(_f)

DEPTO_CHOICES = [('', 'Seleccione departamento')]
PROV_CHOICES = {}
DISTRITOS_CHOICES = {}

for item in _UBIGEO_DATA:
    depto_code = item['departamento']
    prov_code = item['provincia']
    dist_code = item['distrito']
    nombre = item['nombre']

    if prov_code == '00' and dist_code == '00':
        DEPTO_CHOICES.append((depto_code, nombre))
    elif dist_code == '00':
        if depto_code not in PROV_CHOICES:
            PROV_CHOICES[depto_code] = [('', 'Seleccione provincia')]
        PROV_CHOICES[depto_code].append((prov_code, nombre))
    else:
        key = f"{depto_code}_{prov_code}"
        if key not in DISTRITOS_CHOICES:
            DISTRITOS_CHOICES[key] = [('', 'Seleccione distrito')]
        DISTRITOS_CHOICES[key].append((dist_code, nombre))

del item, depto_code, prov_code, dist_code, nombre, key
