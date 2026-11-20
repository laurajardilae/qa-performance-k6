// ============================================================================
// UTILIDADES CENTRALIZADAS
// ----------------------------------------------------------------------------
// Funciones y constantes compartidas por todos los scripts de prueba.
// Cualquier funcion auxiliar nueva (generadores de datos, headers, etc.)
// debe agregarse aqui y no dentro de cada script.
// ============================================================================

export const BASE_URL = 'https://fakestoreapi.com';

export const JSON_PARAMS = { headers: { 'Content-Type': 'application/json' } };

const CARACTERES = 'abcdefghijklmnopqrstuvwxyz0123456789';

// Cadena alfanumerica aleatoria de la longitud indicada
export function randomString(length) {
    let result = '';
    for (let i = 0; i < length; i++) {
        result += CARACTERES.charAt(Math.floor(Math.random() * CARACTERES.length));
    }
    return result;
}

// Payload aleatorio para POST /users
export function payloadCrearUsuario() {
    return JSON.stringify({
        username: `user_${randomString(8)}`,
        email: `${randomString(10)}@test.com`,
        password: randomString(12)
    });
}

// Payload aleatorio para PUT /users/{id}
export function payloadActualizarUsuario() {
    return JSON.stringify({
        username: `user_${randomString(8)}_updated`,
        email: `${randomString(10)}.updated@test.com`
    });
}

// ----------------------------------------------------------------------------
// Desglose por metodo HTTP
// k6 solo exporta en el resumen (y en el dashboard) las sub-metricas que tienen
// un threshold declarado. Estos thresholds "informativos" no validan nada (siempre
// se cumplen): unicamente hacen que k6 reporte peticiones, tiempos y errores
// separados por GET / POST / PUT.
// ----------------------------------------------------------------------------
export function umbralesPorMetodo(metodos = ['GET', 'POST', 'PUT']) {
    const umbrales = {};
    metodos.forEach(m => {
        umbrales[`http_reqs{method:${m}}`] = ['count>=0'];
        umbrales[`http_req_duration{method:${m}}`] = ['max>=0'];
        umbrales[`http_req_failed{method:${m}}`] = ['rate>=0'];
    });
    return umbrales;
}
