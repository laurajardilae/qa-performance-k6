import http from 'k6/http';
import { sleep } from 'k6';
import { baseLine } from '../../lib/stages.js';
import { BASE_URL } from '../../lib/utils.js';

export const options = {
    stages: baseLine
};

export default function () {
    http.get(`${BASE_URL}/users`);
    sleep(1);
}
