# QA Performance con k6

Plantilla de pruebas de performance con [k6](https://grafana.com/docs/k6/). El ejemplo prueba el servicio **Users** de [FakeStore API](https://fakestoreapi.com). Sirve como guia para armar un proyecto nuevo: se cambia el servicio, los stages y los scripts, y la estructura se mantiene.

## Estructura

```
qa-performance-k6
├── lib/                        Codigo compartido por todos los scripts
│   ├── stages.js               Perfiles de carga (baseLine, load, load2, spike) y configBase
│   └── utils.js                BASE_URL, headers, generadores de datos, umbrales por metodo
├── scripts/                    Scripts k6
│   ├── individuales/           Un metodo HTTP por script (GET, POST, PUT) para pruebas de humo/debug
│   └── mixtos/                 Escenarios reales con mezcla 50% GET / 30% POST / 20% PUT
│       ├── users_mixed_baseline.js   Linea base (5 TPS)
│       ├── users_mixed_load.js       Carga (20 TPS)
│       ├── users_mixed_load2.js      Carga maxima (30 TPS)
│       └── users_mixed_spike.js      Picos (20 -> 30 TPS, 5 veces)
├── herramientas/               Utilidades de apoyo
│   ├── ejecutar_pruebas.sh     Corre los escenarios y guarda resultados
│   ├── generar_informe.py      Genera el informe .docx desde los resultados
│   └── stages_design/          Grafica los stages de lib/stages.js (HTML + PNG)
├── docs/                       Plan de pruebas
├── resultados/                 Ultima ejecucion (una carpeta por escenario) + informe .docx
│   └── <escenario>/            resumen.json, html_report.html, dashboard_resumen.png, salida.txt
├── package.json
└── .gitignore
```

## Requisitos

- [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/)
- Node.js (solo para el graficador de stages): `npm install`
- Python 3 con `python-docx` (solo para el informe): `pip install python-docx`
- Google Chrome (captura del dashboard en `ejecutar_pruebas.sh`)

Todos los comandos se ejecutan desde la raiz del repo.

## Uso

| Objetivo | Comando |
|---|---|
| Un script suelto | `k6 run scripts/individuales/users_get.js` |
| Un escenario mixto | `k6 run scripts/mixtos/users_mixed_load.js` |
| Escenarios con resultados y dashboard | `./herramientas/ejecutar_pruebas.sh [baseline\|load\|load2\|spike]` (sin argumentos corre los 4, con 5 min de pausa entre ellos) |
| Graficar stages | `npm run stages` (genera `stage_n.html` y `design_result_n.png` en `herramientas/stages_design/`) |
| Informe .docx | `npm run informe` (lee `resultados/*/resumen.json`) |

Los resultados se sobrescriben en cada ejecucion: `resultados/` siempre contiene la ultima corrida.

## Buenas practicas aplicadas

- **Separacion de responsabilidades:** carga (`lib/stages.js`), datos y URLs (`lib/utils.js`) y logica de prueba (`scripts/`) viven por separado.
- **Modelo por TPS:** `ramping-arrival-rate` controla las peticiones por segundo y no los usuarios virtuales.
- **Sin duplicacion:** la config comun esta en `configBase`; los scripts la reutilizan con `...configBase`.
- **Desglose por metodo:** `umbralesPorMetodo()` hace que k6 reporte metricas por GET/POST/PUT.
- **Resultados reproducibles:** cada escenario guarda metricas, dashboard HTML, captura y salida de consola.

## Para una prueba nueva

1. Cambiar `BASE_URL` y los payloads en `lib/utils.js`.
2. Definir los perfiles de carga en `lib/stages.js` y revisarlos con `npm run stages`.
3. Copiar un script de `scripts/mixtos/` y ajustar endpoints y proporciones.
4. Registrar el escenario en `herramientas/ejecutar_pruebas.sh` (y en `generar_informe.py` si se usa el informe).

## Autor

[Laura Ardila](https://github.com/laurajardilae)
