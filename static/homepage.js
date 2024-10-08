document.getElementById('logout-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const response = await fetch('/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${document.cookie.split('=')[1]}`  // Fetch JWT token from cookie
        }
    });
    const result = await response.json();
    console.log(`Logout response: ${result}`);
    document.getElementById('message').innerText = result.message;
    location.reload();
});

// Dash.js setup for MPEG-DASH playback
const videoPlayer = document.getElementById('videoPlayer');
const player = dashjs.MediaPlayer().create();

player.updateSettings({
    streaming: {
        abr: { autoSwitchBitrate: { audio: true, video: false } }, buffer: { fastSwitchEnabled: true }
    }
});

// Initialize the Dash.js player
player.initialize(videoPlayer, '../static/media/output.mpd', false);

// Play/Pause button
const playPauseBtn = document.getElementById('playPauseBtnButton');
playPauseBtn.addEventListener('click', () => {
    if (videoPlayer.paused) {
        videoPlayer.play();
        playPauseBtn.innerText = 'Pause';
    } else {
        videoPlayer.pause();
        playPauseBtn.innerText = 'Play';
    }
});

const playPauseBtnDiv = document.getElementById('playPauseBtn');
playPauseBtnDiv.addEventListener('click', () => {
    if (videoPlayer.paused) {
        videoPlayer.play();
    } else {
        videoPlayer.pause();
    }
});

// Seek bar
const seekBar = document.getElementById('seekBar');
videoPlayer.addEventListener('timeupdate', () => {
    seekBar.value = (videoPlayer.currentTime / videoPlayer.duration) * 100;
});

seekBar.addEventListener('input', () => {
    const seekTime = (seekBar.value / 100) * videoPlayer.duration;
    videoPlayer.currentTime = seekTime;
});

// Resolution change
const resolutionSelect = document.getElementById('resolutionSelect');
resolutionSelect.addEventListener('change', () => {
    const quality = parseInt(resolutionSelect.value);
    console.log(`Change to quality ${quality}`);
    player.setQualityFor('video', quality);
});

// Populate resolution options dynamically once the stream is initialized
player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, () => {
    const bitrates = player.getBitrateInfoListFor('video');
    resolutionSelect.innerHTML = '';
    console.log(bitrates);
    bitrates.forEach((bitrate, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.text = `${bitrate.width}x${bitrate.height}\t${bitrate.bitrate/1000}kbps`;
        resolutionSelect.appendChild(option);
    });
    resolutionSelect.value = bitrates.length - 1;
});
