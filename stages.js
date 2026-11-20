export const baseLine = [
    { duration: '30s', target: 5 },   // Rampa ascendente
    { duration: '240s', target: 5 },   // Carga constante
    { duration: '30s', target: 0 }     // Rampa descendente
];

export const load = [
    { duration: '60s', target: 20 },   // Rampa ascendente
    { duration: '480s', target: 20 },   // Carga constante
    { duration: '60s', target: 0 }      // Rampa descendente
];

export const load2 = [
    { duration: '90s', target: 30 },   // Rampa ascendente
    { duration: '600s', target: 30 },   // Carga constante
    { duration: '90s', target: 0 }      // Rampa descendente
];

export const spike = [
    { duration: '30s', target: 20 },   // Rampa ascendente a carga base
    // Pico 1
    { duration: '80s', target: 20 },   // Carga base
    { duration: '5s', target: 30 },    // Subida a pico
    { duration: '20s', target: 30 },   // Pico sostenido
    { duration: '5s', target: 20 },    // Bajada a carga base
    // Pico 2
    { duration: '80s', target: 20 },   // Carga base
    { duration: '5s', target: 30 },    // Subida a pico
    { duration: '20s', target: 30 },   // Pico sostenido
    { duration: '5s', target: 20 },    // Bajada a carga base
    // Pico 3
    { duration: '80s', target: 20 },   // Carga base
    { duration: '5s', target: 30 },    // Subida a pico
    { duration: '20s', target: 30 },   // Pico sostenido
    { duration: '5s', target: 20 },    // Bajada a carga base
    // Pico 4
    { duration: '80s', target: 20 },   // Carga base
    { duration: '5s', target: 30 },    // Subida a pico
    { duration: '20s', target: 30 },   // Pico sostenido
    { duration: '5s', target: 20 },    // Bajada a carga base
    // Pico 5
    { duration: '80s', target: 20 },   // Carga base
    { duration: '5s', target: 30 },    // Subida a pico
    { duration: '20s', target: 30 },   // Pico sostenido
    { duration: '5s', target: 20 },    // Bajada a carga base
    { duration: '30s', target: 0 }     // Rampa descendente
];

// ============================================================================
// CONFIGURACION TRANSVERSAL
// ----------------------------------------------------------------------------
// Parametros identicos en los 4 escenarios (definen COMO mide k6, no CUANTO).
// Se centralizan aqui para no repetirlos; cada script los reutiliza con "...".
// ============================================================================
export const configBase = {
    executor: 'ramping-arrival-rate',  // Control por TPS (no por VUs)
    startRate: 0,                       // TPS al iniciar (arranca desde 0)
    timeUnit: '1s'                      // Los targets se interpretan como TPS (por segundo)
};
