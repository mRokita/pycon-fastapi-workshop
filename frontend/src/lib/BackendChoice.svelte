<script>

import {TextInput} from "carbon-components-svelte";
import axios from "axios";
import {apiUrl, authHeaders} from "./stores.js";
import {onMount} from "svelte";
let valid = false;
let apiUrlCandidate = $apiUrl;

const checkBackendUrl = (backendUrl) => {
    return axios.get(`${backendUrl}/openapi.json`).then((res) => {
        if(!res.data.info.title.startsWith("PyCon")) {
            return Promise.reject();
        }
        return Promise.resolve(backendUrl);
    }).catch((e) => {return Promise.reject(e)});
}

let checking = false;

onMount(async () => {
    checking = true;
    try{
        await axios.get(`${$apiUrl}/openapi.json`);
        valid = true;
        checking = false;
    } catch (e) {
        for (const url of ["/api", "http://localhost:8000"]) {
            try {
                await checkBackendUrl(url);
                valid = true;
                apiUrl.set(url);
                checking = false;
                break;
            } catch (e) {
            }
        }
        checking = false;
    }
});

$: {
    apiUrlCandidate = $apiUrl;
}

let timeout;
$: {
    checking = true;
    if(timeout) clearTimeout(timeout);
    timeout =setTimeout(
        () => {
        checkBackendUrl(apiUrlCandidate).then(() => {valid = true; checking = false;}).catch(() => {valid = false;  checking=false;})
    },
    500);
}

</script>

<div class="backend-choice" class:valid-choice={valid && !checking} style="max-width: 30rem;align-content: center;margin:auto;">
    <TextInput invalid={!valid && !checking} variant={"light"} labelText="API URL" placeholder="Enter API URI..." bind:value={$apiUrl} helperText={checking ? `Verifying ${$apiUrl}...` : null}/>
</div>


<style>
    .backend-choice.valid-choice :global(.bx--text-input) {
        color: lightgreen !important;
    }
    .backend-choice :global(.bx--text-input) {
        color: #e32828 !important;
    }
</style>