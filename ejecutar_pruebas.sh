#!/usr/bin/env bash
# Ejecuta los 4 escenarios mixtos y deja, por cada uno, en resultados/<carpeta>/:
#   resumen.json          -> metricas exactas (incluye desglose GET/POST/PUT)
#   html_report.html      -> dashboard web nativo de k6 (graficas reales)
#   dashboard_resumen.png -> captura de las graficas (la usa generar_informe.py)
#   salida.txt            -> salida de consola
# Uso: ./ejecutar_pruebas.sh [baseline|load|load2|spike ...]   (sin argumentos: los 4)
set -uo pipefail
cd "$(dirname "$0")"

if [ $# -eq 0 ]; then set -- baseline load load2 spike; fi
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
export K6_WEB_DASHBOARD="true"
total=$#; n=0
for e in "$@"; do
  n=$((n+1))
  case "$e" in
    baseline) script=users_mixed_baseline; dir=resultados/baseline ;;
    load)     script=users_mixed_load;     dir=resultados/carga ;;
    load2)    script=users_mixed_load2;    dir=resultados/carga_maxima ;;
    spike)    script=users_mixed_spike;    dir=resultados/pico ;;
    *) echo "Escenario desconocido: $e"; exit 1 ;;
  esac
  mkdir -p "$dir"
  echo ">>> Ejecutando $script ..."
  K6_WEB_DASHBOARD_EXPORT="$dir/html_report.html" \
    k6 run --summary-export="$dir/resumen.json" "scripts mixed/$script.js" > "$dir/salida.txt" 2>&1
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=1400,1650 \
    --virtual-time-budget=10000 --screenshot="$dir/dashboard_resumen.png" \
    "file://$PWD/$dir/html_report.html" >/dev/null 2>&1 || echo "(no se pudo generar la captura)"
  echo ">>> $script terminado"
  if [ "$n" -lt "$total" ]; then echo ">>> Pausa de 5 min"; sleep 300; fi
done
echo ">>> TODOS LOS ESCENARIOS TERMINADOS"
