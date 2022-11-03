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
    import {apiUrl} from "./stores.js";

    export let moveToLogin = null;
    let registerError = null;
    let username;
    let password;
    let showSuccessInfo = false;

    const registerUser = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`${$apiUrl}/users`,
                {username: username, password: password}
            )
            registerError = null;
            showSuccessInfo = true;
        } catch (e) {
            registerError = e.response ? JSON.stringify(e.response.data.detail) : e;
        }
    }

</script>

{#if registerError}
    <InlineNotification
            hideCloseButton
            kind="error"
            title={registerError}
    />
{/if}

{#if showSuccessInfo}
        <h4>Congratulations, you can log in now!</h4>
        <br/>
        <Button type="submit" on:click={moveToLogin}>Go to log in</Button>
{:else}
    <FluidForm on:submit={registerUser}>
        <FormGroup>
            <TextInput labelText="Login" placeholder="Enter login..." bind:value={username}/>
            <PasswordInput labelText="Password" placeholder="Enter password..." bind:value={password}/>

        </FormGroup>
        <Button type="submit">Register</Button>
    </FluidForm>
{/if}
