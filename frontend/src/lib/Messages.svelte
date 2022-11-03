<script>
    import User from "carbon-icons-svelte/lib/User.svelte";
    import {apiUrl, authHeaders, user} from "./stores.js";
    import {afterUpdate, tick} from "svelte";

    export let channel;
    let messages = [];
    let socket;
    let messagesContainer;

    const scrollToBottom = async (node) => {
        node.scroll({ top: node.scrollHeight, behavior: 'smooth' });
    };

    function onMessage(message) {
        messages = [...messages, JSON.parse(message.data)]

    }

    afterUpdate(() => {
        if (messages && messagesContainer){
            tick();
            scrollToBottom(messagesContainer);
        }
    })

    function onOpen() {
        messages = []
        socket.send(JSON.stringify($authHeaders))
    }

    $: {
        if (socket) {
            socket.close();
        }
        let wsUrl = new URL(`${$apiUrl}/channels/${channel.slug}/messages_ws`, window.location.href);
        wsUrl.protocol = wsUrl.protocol.replace("http", "ws");
        socket = new WebSocket(wsUrl.href)
        socket.addEventListener("open", onOpen)
        socket.addEventListener("message", onMessage)
    }
</script>

<div id="messages" bind:this={messagesContainer}>
    {#each messages as message}

        <div class="message-wrapper{message.sender_username === $user.username ? ' right' : ''}">
            <div class="message">
                <div class="message-author">
                    <User size={15}/>
                    {message.sender_username}
                </div>
                <div class="message-body">
                    {message.body.text}
                </div>
            </div>
        </div>
    {/each}
</div>
<style>

    .message {
        direction: ltr;
        font-size: 20px;
        background-color: var(--cds-active-01);
        max-width: 90%;
        border-radius: 10px;
        padding: 10px;
        display: inline-block;
        min-width: 20vw;
    }

    .right > .message {
        background-color: cornflowerblue;
        color: white;
    }

    .message-author {
        font-weight: bold;
        margin-bottom: 8px;
    }

    .message-body {

    }

    .right {
        direction: rtl;
    }

    .message-wrapper {
        padding-top: 20px;
    }


    #messages {
        overflow-y: auto;
        min-height: calc(100vh - 8rem);
        max-height: calc(100vh - 8rem);
    }

</style>