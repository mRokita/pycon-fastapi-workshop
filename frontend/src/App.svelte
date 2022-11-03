<script>
    import "carbon-components-svelte/css/all.css";
    import {
        Tab, TabContent, Tabs,
    } from "carbon-components-svelte";
    import LoginForm from "./lib/LoginForm.svelte";
    import {onMount} from "svelte";
    import Chat from "./lib/Chat.svelte";
    import {user} from "./lib/stores.js";
    import RegisterForm from "./lib/RegisterForm.svelte";
    import BackendChoice from "./lib/BackendChoice.svelte";

    let selected = 0;
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    let theme = darkModeQuery.matches ? "g100" : "white";

    onMount(() => document.documentElement.setAttribute("theme", theme));
</script>

{#if !$user}
    <h1 class="login-header">PyCon PL Chat</h1>
    <BackendChoice/>
    <div class="tabs">
        <Tabs type="container" bind:selected>
            <Tab label="Login"/>
            <Tab label="Register"/>
            <svelte:fragment slot="content">
                <TabContent>
                    {#if selected === 0}
                    <LoginForm />
                    {/if}
                </TabContent>
                <TabContent>
                    {#if selected === 1}
                    <RegisterForm moveToLogin={() => selected = 0}/>
                    {/if}
                </TabContent>
            </svelte:fragment>
        </Tabs>
    </div>
{:else}
    <Chat>

    </Chat>
{/if}

<style>
    .login-header {
        font-weight: bold;
        text-align: center;
        padding-top: 100px;
        padding-bottom: 40px;
    }

    .tabs {
        margin: 20px;
        border: 1px solid var(--cds-field-hover);
    }

</style>
