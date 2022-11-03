<script>

    import {RadioTile, TileGroup} from "carbon-components-svelte";
import axios from "axios";
import {apiUrl, authHeaders} from "./stores.js";
import {onDestroy, onMount} from "svelte";
import CreateChannelButton from "./CreateChannelButton.svelte";

export let currentChannel;
let channels = [];
let channelsMap;
$: channelsMap = new Map(channels.map(c => [c.slug, c]))
let getChannel = (slug) => channelsMap.get(slug);
$: currentChannel = getChannel(currentChannelSlug)
let currentChannelSlug = null;
const loadChannels = async () => {
    let res = await axios.get(`${$apiUrl}/channels`, {
        headers: $authHeaders
    })
    if (res.status === 200) {
        channels = res.data;
    }
    if (channels && !currentChannel)
        currentChannelSlug = channels[0].slug;
}
let loadChannelsInterval;
onMount(() =>{
    loadChannels()
    if(loadChannelsInterval)
        clearInterval(loadChannelsInterval)
    loadChannelsInterval = setInterval(loadChannels, 8000);
})
onDestroy(() => clearInterval(loadChannelsInterval))
</script>
<div id="channel-list" class="full-height">

    <TileGroup bind:selected={currentChannelSlug}>
        {#each channels as channel (channel.slug)}
            <RadioTile value={channel.slug}>
                <h4>{channel.name}</h4>
                <span>{channel.slug}</span>
            </RadioTile>
        {/each}
    </TileGroup>
</div>
<CreateChannelButton on:created={loadChannels}/>