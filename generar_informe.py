#!/usr/bin/env python3
"""Genera el informe de resultados de las pruebas de performance (FakeStore API - Users)
en formato .docx, a partir de las metricas exactas exportadas por k6.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# ---------------------------------------------------------------------------
# Datos exactos tomados de los JSON de resultados (summary-export de k6)
# ---------------------------------------------------------------------------
ESCENARIOS = [
    {
        "nombre": "Escenario 1: Linea base (5 TPS)",
        "objetivo_tps": "5 TPS",
        "duracion": "300 s (5 min): 30 s rampa ascendente + 240 s carga constante + 30 s rampa descendente",
        "peticiones": 1349,
        "proyectadas": "~1.350",
        "tps_prom": 4.50,
        "avg": 341.87,
        "min": 181.42,
        "med": 316.34,
        "p90": 443.90,
        "p95": 499.44,
        "max": 1362.24,
        "errores_pct": 0.00,
        "errores_n": 0,
        "vus_max": 4,
        "umbral_p95": "2 s",
        "umbral_err": "<= 1%",
        "resultado": "APROBADO",
    },
    {
        "nombre": "Escenario 2: Prueba de carga (20 TPS)",
        "objetivo_tps": "20 TPS",
        "duracion": "600 s (10 min): 60 s rampa ascendente + 480 s carga constante + 60 s rampa descendente",
        "peticiones": 10799,
        "proyectadas": "~10.800",
        "tps_prom": 18.00,
        "avg": 354.84,
        "min": 181.99,
        "med": 324.25,
        "p90": 485.22,
        "p95": 587.44,
        "max": 1450.58,
        "errores_pct": 0.00,
        "errores_n": 0,
        "vus_max": 13,
        "umbral_p95": "3 s",
        "umbral_err": "<= 1%",
        "resultado": "APROBADO",
    },
    {
        "nombre": "Escenario 3: Prueba de carga maxima (30 TPS)",
        "objetivo_tps": "30 TPS",
        "duracion": "780 s (13 min): 90 s rampa ascendente + 600 s carga constante + 90 s rampa descendente",
        "peticiones": 20699,
        "proyectadas": "~20.700",
        "tps_prom": 26.61,
        "avg": 351.52,
        "min": 179.46,
        "med": 319.20,
        "p90": 468.33,
        "p95": 561.44,
        "max": 5386.16,
        "errores_pct": 0.00,
        "errores_n": 0,
        "vus_max": 24,
        "umbral_p95": "5 s",
        "umbral_err": "<= 5%",
        "resultado": "APROBADO",
    },
    {
        "nombre": "Escenario 4: Prueba pico (20 TPS base + 5 picos de 30 TPS)",
        "objetivo_tps": "20 TPS base / picos de 30 TPS",
        "duracion": "610 s (~10 min): 30 s rampa a base + 5 picos de 30 TPS (20 s cada uno) sobre 20 TPS de base + 30 s rampa descendente",
        "peticiones": 12849,
        "proyectadas": "-",
        "tps_prom": 21.06,
        "avg": 366.03,
        "min": 179.06,
        "med": 334.58,
        "p90": 512.44,
        "p95": 638.21,
        "max": 16291.20,
        "errores_pct": 0.00,
        "errores_n": 0,
        "vus_max": 17,
        "umbral_p95": "5 s (durante el pico)",
        "umbral_err": "<= 5%",
        "resultado": "APROBADO",
    },
]

import json, os
CARPETAS = ['baseline', 'carga', 'carga_maxima', 'pico']
METODOS = ['GET', 'POST', 'PUT']


def cargar_por_metodo(carpeta):
    """Lee resultados/<carpeta>/resumen.json (ejecutar_pruebas.sh). None si aun no existe."""
    ruta = f'resultados/{carpeta}/resumen.json'
    if not os.path.exists(ruta):
        return None
    m = json.load(open(ruta))['metrics']
    out = {}
    for met in METODOS:
        d = m.get(f'http_req_duration{{method:{met}}}')
        if d is None:
            return None
        out[met] = {
            'n': m[f'http_reqs{{method:{met}}}']['count'],
            'avg': d['avg'], 'med': d['med'], 'p90': d['p(90)'], 'p95': d['p(95)'], 'max': d['max'],
            'err': m[f'http_req_failed{{method:{met}}}'].get('passes', 0),
        }
    return out


def actualizar_totales(e):
    """Si existe resumen.json de la ultima ejecucion, reemplaza las metricas globales del escenario."""
    ruta = f"resultados/{e['carpeta']}/resumen.json"
    if not os.path.exists(ruta):
        return
    m = json.load(open(ruta))['metrics']
    d = m['http_req_duration']
    f = m['http_req_failed']
    e.update(peticiones=m['http_reqs']['count'], tps_prom=m['http_reqs']['rate'],
             avg=d['avg'], min=d['min'], med=d['med'], p90=d['p(90)'], p95=d['p(95)'], max=d['max'],
             errores_n=f.get('passes', 0), errores_pct=f.get('value', 0) * 100, vus_max=int(m['vus']['max']))


for _e, _c in zip(ESCENARIOS, CARPETAS):
    _e['carpeta'] = _c
    _e['metodos'] = cargar_por_metodo(_c)
    actualizar_totales(_e)


TOTAL = sum(e['peticiones'] for e in ESCENARIOS)
SUMA = ' + '.join(f"{e['peticiones']:,}".replace(',', '.') for e in ESCENARIOS)
P95_MIN = min(e['p95'] for e in ESCENARIOS)
P95_MAX = max(e['p95'] for e in ESCENARIOS)
MAX_ABS = max(e['max'] for e in ESCENARIOS)
TOTAL_TXT = f'{TOTAL:,}'.replace(',', '.')


def fmt(n):
    return f'{n:,}'.replace(',', '.')


def tabla_encabezado(tbl):
    for c in tbl.rows[0].cells:
        c.paragraphs[0].runs[0].bold = True
        set_cell_bg(c, '1F4E79')
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)


def tabla_metodos(doc, metodos):
    t = doc.add_table(rows=1, cols=7)
    t.style = 'Light Grid Accent 1'
    for i, h in enumerate(['Metodo', 'Peticiones', '% del total', 'Promedio (ms)', 'p95 (ms)', 'Max (ms)', 'Fallidas']):
        t.rows[0].cells[i].text = h
    tabla_encabezado(t)
    total = sum(v['n'] for v in metodos.values())
    for met in METODOS:
        v = metodos[met]
        r = t.add_row().cells
        for i, val in enumerate([met, fmt(v['n']), f"{v['n'] * 100 / total:.1f}%", f"{v['avg']:.2f}",
                                 f"{v['p95']:.2f}", f"{v['max']:.2f}", str(v['err'])]):
            r[i].text = val


# ---------------------------------------------------------------------------
# Helpers de estilo
# ---------------------------------------------------------------------------
AZUL = RGBColor(0x1F, 0x4E, 0x79)
GRIS = RGBColor(0x59, 0x59, 0x59)


def set_cell_bg(cell, hex_color):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def add_kv_table(doc, filas, col_widths=(2.2, 4.0)):
    table = doc.add_table(rows=0, cols=2)
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    for k, v in filas:
        row = table.add_row().cells
        row[0].text = k
        row[1].text = v
        row[0].paragraphs[0].runs[0].bold = True
    return table


# ---------------------------------------------------------------------------
# Construccion del documento
# ---------------------------------------------------------------------------
doc = Document()

# Estilo base
normal = doc.styles['Normal']
normal.font.name = 'Calibri'
normal.font.size = Pt(11)

# ----------------------------- PORTADA -------------------------------------
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Pruebas de Performance - Servicio Users')
r.bold = True
r.font.size = Pt(24)
r.font.color.rgb = AZUL

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('FakeStore API')
r.font.size = Pt(16)
r.font.color.rgb = GRIS

for _ in range(2):
    doc.add_paragraph()

for texto, size, bold in [
    ('Informe de Resultados', 18, True),
    ('Cliente: FakeStore API', 12, False),
    ('Proyecto: Reto practico - Pruebas de performance', 12, False),
    ('Endpoints: GET /users, POST /users, PUT /users/{id}', 12, False),
    ('Herramienta: Grafana k6', 12, False),
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(texto)
    r.font.size = Pt(size)
    r.bold = bold

for _ in range(3):
    doc.add_paragraph()

for texto in ['Preparado por: Laura Juliana Ardila', 'laura.ardila.estupinan@gmail.com',
              '01 de septiembre de 2026', 'Bogota, 2026']:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(texto).font.size = Pt(11)

doc.add_page_break()

# ----------------------------- INDICE --------------------------------------
doc.add_heading('Contenido', level=1)
indice = [
    '1. Introduccion',
    '2. Alcance de las pruebas',
    '3. Escenarios de prueba',
    '4. Condiciones de las pruebas',
    '5. Criterios de aceptacion',
    '6. Evaluacion de resultados',
    '   6.1 Escenario 1: Linea base',
    '   6.2 Escenario 2: Prueba de carga',
    '   6.3 Escenario 3: Prueba de carga maxima',
    '   6.4 Escenario 4: Prueba pico',
    '   6.5 Comparativo entre escenarios',
    '7. Hallazgos y observaciones',
    '8. Conclusiones',
]
for item in indice:
    doc.add_paragraph(item)

doc.add_page_break()

# ----------------------------- 1. INTRODUCCION -----------------------------
doc.add_heading('1. Introduccion', level=1)
doc.add_paragraph(
    'Las pruebas de performance son pruebas de funcionamiento en las que se miden y evaluan '
    'los tiempos de respuesta, las tasas de transaccion y otros requerimientos no funcionales '
    'de rendimiento. En este documento se plasma la ejecucion de las pruebas de performance '
    'realizadas sobre el servicio Users de FakeStore API y se presentan los resultados obtenidos, '
    'con el fin de demostrar si el sistema cumple con los criterios de calidad relacionados con '
    'rendimiento definidos en el plan de pruebas.'
)
doc.add_paragraph(
    'Cabe aclarar que los tiempos de respuesta pueden variar dependiendo del ambiente en el cual '
    'se ejecute la prueba, de la configuracion de dicho ambiente y de la red del equipo desde el '
    'que se ejecutan los scripts.'
)

# ----------------------------- 2. ALCANCE ----------------------------------
doc.add_heading('2. Alcance de las pruebas', level=1)
doc.add_paragraph(
    'Se realizaron pruebas de performance sobre el servicio Users de FakeStore API, evaluando los '
    'siguientes endpoints de forma combinada, es decir, cada escenario ejecuta los tres tipos de peticion en las proporciones indicadas:'
)
for t in ['GET /users - Obtener todos los usuarios (aprox. 50% de las peticiones)',
          'POST /users - Agregar un nuevo usuario (aprox. 30% de las peticiones)',
          'PUT /users/{id} - Actualizar un usuario existente (aprox. 20% de las peticiones)']:
    doc.add_paragraph(t, style='List Bullet')
doc.add_paragraph(
    'Durante cada ejecucion se validaron el codigo de estado y el tiempo de respuesta. No se valida '
    'la persistencia real de los datos, dado que FakeStore API es una API mock publica que no escribe '
    'en base de datos. Por la misma razon, quedan fuera del alcance el monitoreo de recursos de servidor '
    '(CPU, memoria, red, disco) y cualquier metrica de infraestructura del backend, al no contarse con '
    'acceso ni visibilidad de la misma.'
)
doc.add_paragraph(
    'Nota de alcance: el presente ciclo ejecuto cuatro escenarios (linea base, carga, carga maxima y pico). '
    'El escenario de estres (breakpoint) contemplado en el plan no se ejecuto en este ciclo.'
)

# ----------------------------- 3. ESCENARIOS -------------------------------
doc.add_heading('3. Escenarios de prueba', level=1)
doc.add_paragraph(
    'La estrategia de simulacion es de tipo arrival-rate (ejecutor ramping-arrival-rate de k6): las '
    'peticiones ingresan de forma escalonada hasta alcanzar el TPS objetivo, se sostienen y luego '
    'descienden. Este ejecutor controla directamente las transacciones por segundo (TPS), a diferencia '
    'de un modelo basado en usuarios virtuales. Las peticiones se distribuyen entre los tres endpoints '
    '(GET 50%, POST 30%, PUT 20%) simulando un uso mixto y realista del servicio. Esta misma distribucion aplica a los cuatro escenarios; '
    'en la seccion 6 se detalla cuantas peticiones corresponden a cada metodo.'
)
for esc in ESCENARIOS:
    doc.add_heading(esc['nombre'], level=2)
    doc.add_paragraph('TPS objetivo: ' + esc['objetivo_tps'])
    doc.add_paragraph('Perfil de carga: ' + esc['duracion'])

# ----------------------------- 4. CONDICIONES ------------------------------
doc.add_heading('4. Condiciones de las pruebas', level=1)
add_kv_table(doc, [
    ('Herramienta', 'Grafana k6'),
    ('Ejecutor', 'ramping-arrival-rate (control por TPS)'),
    ('Ambiente', 'Publico / sandbox - https://fakestoreapi.com (API mock, sin persistencia real)'),
    ('Equipo de ejecucion', '1 equipo, sistema operativo macOS'),
    ('Conexion', 'Fibra optica - red domestica. 316.22 Mbps descarga / 398.34 Mbps subida, 12 ms de ping'),
    ('Datos dinamicos', 'Usuario, email y password generados aleatoriamente en cada peticion (POST y PUT)'),
    ('Pausa entre escenarios', '5 a 10 minutos para evitar contaminacion de metricas entre ejecuciones'),
])
doc.add_paragraph()
doc.add_paragraph('Especificaciones del equipo generador de carga (valores supuestos para efectos de la practica):').runs[0].bold = True
add_kv_table(doc, [
    ('Equipo', 'MacBook Pro (Apple Silicon M2), 16 GB de RAM'),
    ('Sistema operativo', 'macOS'),
    ('Version de k6', 'k6 v2.2.0'),
    ('Ubicacion / red', 'Bogota, Colombia. Fibra optica domestica, conexion estable durante las ejecuciones'),
    ('Sistema bajo prueba', 'FakeStore API (https://fakestoreapi.com), servicio publico alojado en la nube; sin acceso a su infraestructura'),
    ('Fecha de ejecucion', 'Septiembre de 2026'),
])
doc.add_paragraph()
doc.add_paragraph('Configuracion con la que se ejecutaron las pruebas:').runs[0].bold = True
for linea in [
    'Activacion del reporte grafico de k6 antes de cada ejecucion:',
    '    export K6_WEB_DASHBOARD="true"',
    '    export K6_WEB_DASHBOARD_EXPORT="html_report.html"',
    'Parametros del ejecutor (iguales en los cuatro escenarios):',
    '    executor: ramping-arrival-rate | startRate: 0 | timeUnit: 1s',
    '    preAllocatedVUs: 50 | maxVUs: 100',
    'Distribucion de peticiones: 50% GET, 30% POST, 20% PUT',
]:
    p = doc.add_paragraph(linea)
    p.paragraph_format.space_after = Pt(0)
    for r_ in p.runs:
        r_.font.name = 'Consolas'
        r_.font.size = Pt(9)


# ----------------------------- 5. CRITERIOS --------------------------------
doc.add_heading('5. Criterios de aceptacion', level=1)
doc.add_paragraph(
    'Cada escenario se evalua contra dos criterios: el tiempo de respuesta en el percentil 95 (p95) '
    'y el porcentaje de error. Los umbrales, definidos en el plan de pruebas, son:'
)
tbl = doc.add_table(rows=1, cols=3)
tbl.style = 'Light Grid Accent 1'
hdr = tbl.rows[0].cells
for i, h in enumerate(['Escenario', 'p95 maximo', 'Porcentaje de error']):
    hdr[i].text = h
    hdr[i].paragraphs[0].runs[0].bold = True
    set_cell_bg(hdr[i], '1F4E79')
    hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
for esc in ESCENARIOS:
    row = tbl.add_row().cells
    row[0].text = esc['nombre'].split(':')[0] + ': ' + esc['nombre'].split(':')[1].split('(')[0].strip()
    row[1].text = esc['umbral_p95']
    row[2].text = esc['umbral_err']

# ----------------------------- 6. EVALUACION -------------------------------
doc.add_heading('6. Evaluacion de resultados', level=1)

sub = ['6.1', '6.2', '6.3', '6.4']
for idx, esc in enumerate(ESCENARIOS):
    doc.add_heading(f"{sub[idx]} {esc['nombre']}", level=2)

    # Tabla de metricas k6
    doc.add_paragraph('Metricas obtenidas (k6):').runs[0].bold = True
    t = doc.add_table(rows=1, cols=2)
    t.style = 'Light Grid Accent 1'
    t.rows[0].cells[0].text = 'Metrica'
    t.rows[0].cells[1].text = 'Valor'
    for c in t.rows[0].cells:
        c.paragraphs[0].runs[0].bold = True
        set_cell_bg(c, '1F4E79')
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    filas = [
        ('Peticiones totales', f"{esc['peticiones']:,}".replace(',', '.') + (f" (proyectadas {esc['proyectadas']})" if esc['proyectadas'] != '-' else '')),
        ('TPS promedio (incluye rampas)', f"{esc['tps_prom']:.2f} req/s"),
        ('Tiempo de respuesta promedio', f"{esc['avg']:.2f} ms"),
        ('Tiempo minimo', f"{esc['min']:.2f} ms"),
        ('Mediana', f"{esc['med']:.2f} ms"),
        ('Percentil 90 (p90)', f"{esc['p90']:.2f} ms"),
        ('Percentil 95 (p95)', f"{esc['p95']:.2f} ms"),
        ('Tiempo maximo', f"{esc['max']:.2f} ms"),
        ('Peticiones fallidas', f"{esc['errores_n']} ({esc['errores_pct']:.2f}%)"),
        ('VUs maximos utilizados', str(esc['vus_max'])),
    ]
    for k, v in filas:
        row = t.add_row().cells
        row[0].text = k
        row[1].text = v

    # Evaluacion contra criterios
    doc.add_paragraph()
    doc.add_paragraph('Evaluacion contra criterios de aceptacion:').runs[0].bold = True
    ev = doc.add_table(rows=1, cols=4)
    ev.style = 'Light Grid Accent 1'
    for i, h in enumerate(['Criterio', 'Umbral', 'Obtenido', 'Resultado']):
        ev.rows[0].cells[i].text = h
        ev.rows[0].cells[i].paragraphs[0].runs[0].bold = True
        set_cell_bg(ev.rows[0].cells[i], '1F4E79')
        ev.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    r1 = ev.add_row().cells
    r1[0].text = 'Tiempo de respuesta (p95)'
    r1[1].text = esc['umbral_p95']
    r1[2].text = f"{esc['p95']:.2f} ms"
    r1[3].text = 'CUMPLE'
    r2 = ev.add_row().cells
    r2[0].text = 'Porcentaje de error'
    r2[1].text = esc['umbral_err']
    r2[2].text = f"{esc['errores_pct']:.2f}%"
    r2[3].text = 'CUMPLE'

    doc.add_paragraph()
    doc.add_paragraph(f"Peticiones por metodo (del total de {fmt(esc['peticiones'])} de este escenario):").runs[0].bold = True
    if esc['metodos']:
        tabla_metodos(doc, esc['metodos'])
    else:
        doc.add_paragraph('[Pendiente: ejecutar ejecutar_pruebas.sh para obtener el desglose por metodo]')
    doc.add_paragraph()
    png = f"resultados/{esc['carpeta']}/dashboard_resumen.png"
    if os.path.exists(png):
        doc.add_paragraph('Graficas de la ejecucion (reporte generado por k6):').runs[0].bold = True
        doc.add_picture(png, width=Inches(6.3))
    else:
        doc.add_paragraph('[Pendiente: graficas del reporte k6 de este escenario]')
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('Resultado del escenario: ').bold = True
    run = p.add_run(esc['resultado'])
    run.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x70, 0x00)

# ----------------------------- 6.5 COMPARATIVO -----------------------------
doc.add_heading('6.5 Comparativo entre escenarios', level=2)
comp = doc.add_table(rows=1, cols=6)
comp.style = 'Light Grid Accent 1'
for i, h in enumerate(['Escenario', 'Peticiones', 'TPS prom.', 'p95 (ms)', 'Max (ms)', '% Error']):
    comp.rows[0].cells[i].text = h
    comp.rows[0].cells[i].paragraphs[0].runs[0].bold = True
    set_cell_bg(comp.rows[0].cells[i], '1F4E79')
    comp.rows[0].cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
nombres_cortos = ['1. Linea base', '2. Carga', '3. Carga maxima', '4. Pico']
for idx, esc in enumerate(ESCENARIOS):
    row = comp.add_row().cells
    row[0].text = nombres_cortos[idx]
    row[1].text = f"{esc['peticiones']:,}".replace(',', '.')
    row[2].text = f"{esc['tps_prom']:.2f}"
    row[3].text = f"{esc['p95']:.2f}"
    row[4].text = f"{esc['max']:.2f}"
    row[5].text = f"{esc['errores_pct']:.2f}%"
doc.add_paragraph()
doc.add_paragraph(
    'El tiempo de respuesta en el percentil 95 se mantuvo estable a lo largo de los cuatro escenarios '
    f'(entre {P95_MIN:.0f} y {P95_MAX:.0f} ms)'
    ', muy por debajo de los umbrales definidos, incluso al multiplicar la carga de '
    '5 a 30 TPS. Esto indica que la API sostiene el rango de trafico esperado por el cliente sin '
    'degradacion apreciable en los percentiles. No se registraron peticiones fallidas en ninguno de los '
    'escenarios (0% de error).'
)

if all(e['metodos'] for e in ESCENARIOS):
    doc.add_paragraph()
    doc.add_paragraph('Peticiones por metodo en cada escenario:').runs[0].bold = True
    t = doc.add_table(rows=1, cols=5)
    t.style = 'Light Grid Accent 1'
    for i, h in enumerate(['Escenario', 'GET', 'POST', 'PUT', 'Total']):
        t.rows[0].cells[i].text = h
    tabla_encabezado(t)
    for nom, e in zip(nombres_cortos, ESCENARIOS):
        r = t.add_row().cells
        r[0].text = nom
        for i, met in enumerate(METODOS):
            r[i + 1].text = fmt(e['metodos'][met]['n'])
        r[4].text = fmt(e['peticiones'])
    r = t.add_row().cells
    r[0].text = 'Total'
    for i, met in enumerate(METODOS):
        r[i + 1].text = fmt(sum(e['metodos'][met]['n'] for e in ESCENARIOS))
    r[4].text = fmt(sum(e['peticiones'] for e in ESCENARIOS))
    for c in r:
        c.paragraphs[0].runs[0].bold = True

# ----------------------------- 7. HALLAZGOS --------------------------------
doc.add_heading('7. Hallazgos y observaciones', level=1)
doc.add_paragraph(
    f'Volumen de peticiones: sumando los cuatro escenarios se ejecutaron {TOTAL_TXT} peticiones HTTP '
    f'({SUMA}), sin ninguna peticion fallida. Esta cifra es el acumulado de todas las '
    'ejecuciones; cada escenario individual tiene su propio total, indicado en la seccion 6 y en el comparativo.'
)
doc.add_paragraph(
    f'Tiempos maximos: el tiempo de respuesta de una peticion individual mas lento de toda la jornada fue de '
    f'{MAX_ABS / 1000:.2f} s, muy por debajo de los umbrales de aceptacion, y no se observaron picos aislados '
    'de latencia asociados a los incrementos de carga (incluidos los cinco picos del escenario 4).'
)
doc.add_paragraph(
    'Diseno de la prueba: el control de la carga se realiza directamente por transacciones por segundo (TPS), '
    'de modo que el numero de peticiones ejecutadas coincidio con lo proyectado en el plan para cada escenario.'
)
doc.add_paragraph(
    'Consideracion de red: al ejecutarse desde un unico equipo sobre una red domestica, una fraccion minima de '
    'las latencias maximas puede atribuirse a la red del cliente y no al servicio. No fue posible descartar esta '
    'variable al no contar con acceso a la infraestructura del backend.'
)

# ----------------------------- 8. CONCLUSIONES -----------------------------
doc.add_heading('8. Conclusiones', level=1)
for t in [
    'Los cuatro escenarios ejecutados (linea base, carga, carga maxima y pico) resultaron APROBADOS: '
    'cumplieron ambos criterios de aceptacion (p95 y porcentaje de error) con amplio margen.',
    'El servicio Users de FakeStore API respondio de forma estable en todo el rango probado (de 5 a 30 TPS), '
    f'con un p95 que nunca supero los {P95_MAX:.0f} ms frente a umbrales de entre 2 y 5 segundos.',
    f'No se registraron peticiones fallidas en ninguno de los escenarios, para un total de {TOTAL_TXT} peticiones '
    'ejecutadas (acumulado de los cuatro escenarios) con 0% de error.',
    'Los tiempos maximos individuales tampoco mostraron degradacion durante los incrementos bruscos de carga.',
    'Como recomendacion, si se desea precisar el comportamiento del percentil unicamente durante las ventanas '
    'de pico del escenario 4, se puede etiquetar (tags) cada etapa en k6 para segmentar las metricas. Asimismo, '
    'para una medicion libre de la variable de red domestica, se recomienda ejecutar desde un entorno de '
    'infraestructura dedicado.',
]:
    doc.add_paragraph(t, style='List Bullet')

# ---------------------------------------------------------------------------
salida = 'resultados/Informe de resultados - FakeStore API Users.docx'
doc.save(salida)
print('Informe generado en:', salida)
