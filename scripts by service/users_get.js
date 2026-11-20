import http from 'k6/http';
import {sleep} from 'k6';
import {baseLine} from '../stages.js';


export const options={
    stages: baseLine
};


export default function(){
    let response = http.get('https://reqres.in/api/users');
    sleep(1); 
}
