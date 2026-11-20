// ============================================================================
// ESCENARIO 4: PRUEBA PICO (spike)
// ----------------------------------------------------------------------------
// TPS objetivo: 20 TPS de carga base + 5 picos puntuales de 30 TPS (20s c/u)
// Perfil: 30s rampa a base + 5 ciclos de pico sobre 20 TPS + 30s rampa descendente
// Duracion total: ~610s (~10 min)
// Criterios de aceptacion: p95 <= 5s (durante el pico) | error <= 5%
// ----------------------------------------------------------------------------
// Ejecutar:
//   (desde la raiz del repo) k6 run --summary-export=resultados/pico/resumen.json scripts/mixtos/users_mixed_spike.js
// ============================================================================

import http from 'k6/http';
import { BASE_URL, JSON_PARAMS, payloadCrearUsuario, payloadActualizarUsuario, umbralesPorMetodo } from '../../lib/utils.js';
import { configBase, spike } from '../../lib/stages.js';

export const options = {
    scenarios: {
        pico: {
            // Config transversal (executor, startRate, timeUnit) centralizada en stages.js
            ...configBase,
            // VUs reservados para poder alcanzar el TPS objetivo (propio del escenario)
            preAllocatedVUs: 50,
            // Techo de VUs si k6 necesita mas para sostener el TPS (propio del escenario)
            maxVUs: 100,
            // Los targets de cada stage representan TPS (iteraciones/seg)
            stages: spike
        }
    },
    // Desglose informativo por metodo HTTP (no valida, solo hace que k6 lo reporte)
    thresholds: umbralesPorMetodo()
};

export default function () {
    const random = Math.random();

    if (random < 0.5) {
        // 50% - GET /users
        http.get(`${BASE_URL}/users`);

    } else if (random < 0.8) {
        // 30% - POST /users
        http.post(`${BASE_URL}/users`, payloadCrearUsuario(), JSON_PARAMS);

    } else {
        // 20% - PUT /users/{id}
        http.put(`${BASE_URL}/users/1`, payloadActualizarUsuario(), JSON_PARAMS);
    }
}
