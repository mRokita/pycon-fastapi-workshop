<script>

    import {
        Column,
        Grid,
        RadioTile,
        Row,
        TextInput,
        TileGroup
    } from "carbon-components-svelte";

    import Light from "carbon-icons-svelte/lib/Light.svelte";
    import Moon from "carbon-icons-svelte/lib/Moon.svelte";
    import Exit from "carbon-icons-svelte/lib/Exit.svelte";
    import Messages from "./Messages.svelte";

    import {apiUrl, authHeaders, user} from "./stores.js";
    import axios from "axios";
    import ChannelList from "./ChannelList.svelte";

    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    let theme = darkModeQuery.matches ? "g100" : "white"; // "white" | "g10" | "g80" | "g90" | "g100"
    $: document.documentElement.setAttribute("theme", theme);
    let currentChannel;
    let message;
    let messageError;
</script>

<nav>
    {#if theme !== "white"}
        <span on:keyup={() => {}} on:click={() => theme = "white"} style="margin-right:10px;">
            <Light size={24} style="cursor:pointer;"/>
        </span>
    {:else}
        <span on:keyup={() => {}} on:click={() => theme = "g100"} style="margin-right:10px;">
            <Moon size={24} style="cursor:pointer;" on:click={() => theme = "g100"}/>
        </span>
    {/if}
    <h4 class="navbar-brand">PyConPL Chat</h4>

    <h4 class="navbar-user">
        {$user.username}
    </h4>
    <span on:keyup={() => {}} on:click={() => $user = null}>
        <Exit size={24} style="cursor:pointer;" on:click={() => theme = "g100"}/>
    </span>
</nav>

<div class="app">
    <Grid noGutter fullWidth>
        <Row>
            <Column md={2} lg={4} sm={2} xs={2}>
                <ChannelList bind:currentChannel={currentChannel}/>
            </Column>

            <Column md={6} lg={12} sm={2} xs={2}>
                <div class="full-height" style="padding-right:30px;">
                    {#if currentChannel}
                        <Messages channel={currentChannel}/>
                        <div style="position: relative;bottom:-20px;width:100%;">
                        <TextInput bind:value={message} on:keydown={async (e) => {
                            if(e.key === 'Enter' && message) {
                                try {
                                    await axios.post(`${$apiUrl}/channels/${currentChannel.slug}/messages`,
                                        {
                                          body: {
                                            text: message
                                          }
                                        }, {
                                        headers: $authHeaders
                                    });
                                    message = "";
                                } catch(e) {e
                                    messageError = e.response ? JSON.stringify(e.response.data.detail) : JSON.stringify(e);
                                }
                            }
                        }}></TextInput>
                    </div>
                    {:else}
                        Please create a channel
                    {/if}


                </div>
            </Column>
        </Row>
    </Grid>
</div>


<style>
    .app {
        margin-top: 2px;
    }

    .full-height {
        min-height: calc(100vh - 3rem - 3px);
        max-height: calc(100vh - 3rem - 3px);
    }


    .navbar-brand {
        font-weight: bold;
        flex-grow: 1;
    }

    .navbar-user {
        font-weight: bold;
        padding-right: 10px;
    }

    nav {
        padding-left: 2.2rem;
        padding-right: 2.2rem;
        display: flex;
        align-items: center;
        height: 3rem;
        border-bottom: 1px transparent var(--cds-text-01);
        box-shadow: 0 1px 2px 0 var(--cds-text-01);
    }


</style>