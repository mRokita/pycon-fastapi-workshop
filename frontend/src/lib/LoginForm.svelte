<script>

    import {
        Button, ButtonSet,
        FluidForm,
        Form,
        FormGroup,
        InlineNotification,
        Modal,
        PasswordInput,
        TextInput
    } from "carbon-components-svelte";

    import axios from "axios";
    import {apiUrl, user} from "./stores.js";

    let loginError = null;
    let username;
    let password;
</script>

    {#if loginError}
        <InlineNotification
                hideCloseButton
                kind="error"
                title={loginError}
        />
    {/if}

    <FluidForm on:submit={async (e) => {
               e.preventDefault();
               try {
                    let res = await axios.get(`${$apiUrl}/users/me`, {headers: {"Authorization": "Basic " + btoa(username + ":" + password)}})
                    $user = res.data;
                    $user.password = password
                    loginError = null;
               } catch (e) {
                    console.log(e);
                    loginError = e.response ? JSON.stringify(e.response.data.detail) : JSON.stringify(e);
               }

           }}>
        <FormGroup>
            <TextInput labelText="Login" placeholder="Enter login..." bind:value={username}/>
            <PasswordInput labelText="Password" placeholder="Enter password..." bind:value={password}/>
        </FormGroup>

<Button type="submit"
>Login</Button>
    </FluidForm>
