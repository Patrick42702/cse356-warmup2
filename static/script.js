document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const email = document.getElementById('register-email').value;

    const response = await fetch('/adduser', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password, email })
    });
    const result = await response.json();
    document.getElementById('message').innerText = result.message;
});

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    if (true || response.ok) {
        document.getElementById('message').innerText = 'Login successful';
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('logout-section').style.display = 'block';
        document.getElementById('media-player-section').style.display = 'block';
    } else {
        const result = await response.json();
        document.getElementById('message').innerText = result.message;
    }
});

document.getElementById('logout-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const response = await fetch('/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${document.cookie.split('=')[1]}`  // Fetch JWT token from cookie
        }
    });

    if (response.ok) {
        document.getElementById('message').innerText = 'Logout successful';
        document.getElementById('register-section').style.display = 'block';
        document.getElementById('login-section').style.display = 'block';
        document.getElementById('logout-section').style.display = 'none';
        document.getElementById('media-player-section').style.display = 'none';
    } else {
        document.getElementById('message').innerText = 'Failed to logout';
    }
});

// Dash.js setup for MPEG-DASH playback
const videoPlayer = document.getElementById('videoPlayer');
const player = dashjs.MediaPlayer().create();

player.updateSettings({
    streaming: {
        abr: { autoSwitchBitrate: { audio: true, video: false }, fastSwitchEnabled: true }
    }
});

// Initialize the Dash.js player
player.initialize(videoPlayer, 'https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd', false);

// Play/Pause button
const playPauseBtn = document.getElementById('playPauseBtn');
playPauseBtn.addEventListener('click', () => {
    if (videoPlayer.paused) {
        videoPlayer.play();
        playPauseBtn.innerText = 'Pause';
    } else {
        videoPlayer.pause();
        playPauseBtn.innerText = 'Play';
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
        option.text = `${bitrate.width}x${bitrate.height}\t${bitrate.bitrate}kbps`;
        resolutionSelect.appendChild(option);
    });
    resolutionSelect.value = bitrates.length - 1;
});
