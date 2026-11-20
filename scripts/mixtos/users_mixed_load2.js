// ============================================================================
// ESCENARIO 3: PRUEBA DE CARGA MAXIMA (load2)
// ----------------------------------------------------------------------------
// TPS objetivo: 30 TPS (TPS maximo declarado en el requisito del cliente)
// Perfil: 90s rampa ascendente + 600s carga constante + 90s rampa descendente
// Duracion total: 780s (13 min) | Peticiones proyectadas: ~20.700
// Criterios de aceptacion: p95 <= 5s | error <= 5%
// ----------------------------------------------------------------------------
// Ejecutar:
//   (desde la raiz del repo) k6 run --summary-export=resultados/carga_maxima/resumen.json scripts/mixtos/users_mixed_load2.js
// ============================================================================

import http from 'k6/http';
import { BASE_URL, JSON_PARAMS, payloadCrearUsuario, payloadActualizarUsuario, umbralesPorMetodo } from '../../lib/utils.js';
import { configBase, load2 } from '../../lib/stages.js';

export const options = {
    scenarios: {
        carga_maxima: {
            // Config transversal (executor, startRate, timeUnit) centralizada en stages.js
            ...configBase,
            // VUs reservados para poder alcanzar el TPS objetivo (propio del escenario)
            preAllocatedVUs: 50,
            // Techo de VUs si k6 necesita mas para sostener el TPS (propio del escenario)
            maxVUs: 100,
            // Los targets de cada stage representan TPS (iteraciones/seg)
            stages: load2
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
