import http from 'k6/http';
import { sleep } from 'k6';
import { baseLine } from '../../lib/stages.js';
import { BASE_URL, JSON_PARAMS, payloadActualizarUsuario } from '../../lib/utils.js';

export const options = {
    stages: baseLine
};

export default function () {
    http.put(`${BASE_URL}/users/1`, payloadActualizarUsuario(), JSON_PARAMS);
    sleep(1);
}
