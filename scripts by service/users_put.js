import http from 'k6/http';
import {sleep} from 'k6';
import {baseLine} from '../stages.js';
import {randomString} from '../utils.js';


export const options = {
    stages: baseLine
};

export default function(){
    const username = `user_${randomString(8)}_updated`;
    const email = `${randomString(10)}.updated@test.com`;

    const payload = JSON.stringify({
        username: username,
        email: email
    });

    const params = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    let response = http.put('https://fakestoreapi.com/users/1', payload, params);
    sleep(1);
}
