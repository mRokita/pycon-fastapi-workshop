import {writable as writableLocalStorage} from "svelte-local-storage-store";
import axios from "axios";
import {writable} from "svelte/store";

export const user = writable( null);
export const authHeaders = writable( null)
export const apiUrl = writable( null);

user.subscribe((user) => {
    if(user){
        authHeaders.set({"Authorization": "Basic " + btoa(user.username + ":" + user.password)})
    } else {
        authHeaders.set(null);
    }
})

axios.interceptors.response.use((response) => response, (error) => {
    if(error.response && error.response.status === 401){
        user.set(null);
    }
    return Promise.reject(error);
})