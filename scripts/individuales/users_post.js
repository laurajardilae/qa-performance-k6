import http from 'k6/http';
import { sleep } from 'k6';
import { baseLine } from '../../lib/stages.js';
import { BASE_URL, JSON_PARAMS, payloadCrearUsuario } from '../../lib/utils.js';

export const options = {
    stages: baseLine
};

export default function () {
    http.post(`${BASE_URL}/users`, payloadCrearUsuario(), JSON_PARAMS);
    sleep(1);
}
