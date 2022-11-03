<script>
    import {Button, FormGroup, InlineNotification, Modal, PasswordInput, TextInput} from "carbon-components-svelte";
    import axios from "axios";
    import {apiUrl, authHeaders} from "./stores.js";
    import {createEventDispatcher} from "svelte";
    const dispatch = createEventDispatcher();
    let open = false;
    let channelSlug = "";
    let channelName = "";
    let saveError = null
    $: {
        channelSlug = encodeURIComponent(channelName).replace(/%(?:\d|[A-F]){2}/g, "-");
    }
</script>

<Button on:click={() => open = true}
        style="position:absolute;left:10px;bottom:10px;max-width: 10vw;">
    Add channel
</Button>
<Modal
  bind:open
  modalHeading="Create channel"
  primaryButtonText="Save channel"
  secondaryButtonText="Cancel"
  on:click:button--secondary={() => (open = false)}
  on:open
  on:close
  on:submit={async () => {
        try {
            await axios.post(`${$apiUrl}/channels`,
                {
                  slug: channelSlug,
                  name: channelName
                }, {
                headers: $authHeaders
            });
            saveError = null;
            open = false;
            dispatch("created")
        } catch (e) {
            console.log(e);
            saveError = e.response ? JSON.stringify(e.response.data.detail) : JSON.stringify(e);
        }
    }}
>
    {#if saveError}
        <InlineNotification
                hideCloseButton
                kind="error"
                title={saveError}
        />
    {/if}
    <FormGroup>
            <TextInput labelText="Channel name" placeholder="Enter channel name..." bind:value={channelName}/>
            <TextInput labelText="Channel slug" placeholder="Enter channel slug..." bind:value={channelSlug}/>
    </FormGroup>
</Modal>
