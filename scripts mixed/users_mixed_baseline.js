// ============================================================================
// ESCENARIO 1: LINEA BASE (baseLine)
// ----------------------------------------------------------------------------
// TPS objetivo: 5 TPS
// Perfil: 30s rampa ascendente + 240s carga constante + 30s rampa descendente
// Duracion total: 300s (5 min) | Peticiones proyectadas: ~1.350
// Criterios de aceptacion: p95 <= 2s | error <= 1%
// ----------------------------------------------------------------------------
// Ejecutar:
//   k6 run --summary-export=../resultados/resultados_baseline.json users_mixed_baseline.js
// ============================================================================

import http from 'k6/http';
import { BASE_URL, JSON_PARAMS, payloadCrearUsuario, payloadActualizarUsuario, umbralesPorMetodo } from '../utils.js';
import { configBase, baseLine } from '../stages.js';

export const options = {
    scenarios: {
        baseline: {
            // Config transversal (executor, startRate, timeUnit) centralizada en stages.js
            ...configBase,
            // VUs reservados para poder alcanzar el TPS objetivo (propio del escenario)
            preAllocatedVUs: 50,
            // Techo de VUs si k6 necesita mas para sostener el TPS (propio del escenario)
            maxVUs: 100,
            // Los targets de cada stage representan TPS (iteraciones/seg)
            stages: baseLine
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
