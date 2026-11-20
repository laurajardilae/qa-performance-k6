import http from 'k6/http';
import {sleep} from 'k6';
import {baseLine} from '../stages.js';
import {randomString} from '../utils.js';


export const options = {
    stages: baseLine
};

export default function(){
    const username = `user_${randomString(8)}`;
    const email = `${randomString(10)}@test.com`;
    const password = randomString(12);

    const payload = JSON.stringify({
        username: username,
        email: email,
        password: password
    });

    const params = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    let response = http.post('https://fakestoreapi.com/users', payload, params);
    sleep(1);
}
