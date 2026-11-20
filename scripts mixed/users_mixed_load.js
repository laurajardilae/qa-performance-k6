// ============================================================================
// ESCENARIO 2: PRUEBA DE CARGA (load)
// ----------------------------------------------------------------------------
// TPS objetivo: 20 TPS (carga solicitada en el requisito)
// Perfil: 60s rampa ascendente + 480s carga constante + 60s rampa descendente
// Duracion total: 600s (10 min) | Peticiones proyectadas: ~10.800
// Criterios de aceptacion: p95 <= 3s | error <= 1%
// ----------------------------------------------------------------------------
// Ejecutar:
//   k6 run --summary-export=../resultados/resultados_carga.json users_mixed_load.js
// ============================================================================

import http from 'k6/http';
import { BASE_URL, JSON_PARAMS, payloadCrearUsuario, payloadActualizarUsuario, umbralesPorMetodo } from '../utils.js';
import { configBase, load } from '../stages.js';

export const options = {
    scenarios: {
        carga: {
            // Config transversal (executor, startRate, timeUnit) centralizada en stages.js
            ...configBase,
            // VUs reservados para poder alcanzar el TPS objetivo (propio del escenario)
            preAllocatedVUs: 50,
            // Techo de VUs si k6 necesita mas para sostener el TPS (propio del escenario)
            maxVUs: 100,
            // Los targets de cada stage representan TPS (iteraciones/seg)
            stages: load
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
