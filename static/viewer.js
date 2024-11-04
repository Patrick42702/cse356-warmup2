// Video list - this should match the format you defined on the server
let videoList = []; // Will be populated with data from m1.json
let currentIndex = 0; // Index of the currently playing video

// Fetch video list on load
async function loadVideoList() {
    const response = await fetch('/static/m1.json');
    const data = await response.json();
    videoList = Object.entries(data).map(([title, description]) => {
        return { id: title.split('-')[0], metadata: { title, description } };
    });

    // Find initial video based on URL and play it
    const videoId = window.location.pathname.split('/').pop();
    currentIndex = videoList.findIndex(video => video.id === videoId) || 0;
    playVideo(currentIndex);
}

// Function to play the video at the given index
function playVideo(index) {
    if (index < 0 || index >= videoList.length) return; // Check bounds

    const video = videoList[index];
    const videoPlayer = document.getElementById('videoPlayer');
    const player = dashjs.MediaPlayer().create();
    player.initialize(videoPlayer, `../static/media/${video.id}.mpd`, true);

    // Update the URL without reloading the page
    window.history.pushState({}, '', `/play/${video.id}`);
}

// Handle scroll event for infinite scroll navigation
function handleScroll(event) {
    const scrollY = window.scrollY || document.documentElement.scrollTop;

    if (scrollY > 0) {  // Scroll down
        if (currentIndex < videoList.length - 1) {
            currentIndex++;
            playVideo(currentIndex);
        }
    } else if (scrollY < 0) {  // Scroll up
        if (currentIndex > 0) {
            currentIndex--;
            playVideo(currentIndex);
        }
    }

    // Reset scroll position to avoid cumulative scroll effect
    window.scrollTo(0, 0);
}

// Load video list and set up initial video
document.addEventListener('DOMContentLoaded', async () => {
    await loadVideoList();
    window.addEventListener('scroll', handleScroll);
});


document.getElementById('logout-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const response = await fetch('/api/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${document.cookie.split('=')[1]}`  // Fetch JWT token from cookie
        }
    });
    const result = await response.json();
    console.log(`Logout response: ${result}`);
    document.getElementById('message').innerText = result.message;
    location.href = "/";
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
const video_id = window.location.pathname.split('/')[2]
player.initialize(videoPlayer, `../static/media/${video_id}.mpd`, false);

// Play/Pause button
const playPauseBtn = document.getElementById('playPauseBtnButton');
const playPauseBtnDiv = document.getElementById('playPauseBtn');
playPauseBtnDiv.addEventListener('click', () => {
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
        option.text = `${bitrate.width}x${bitrate.height}\t${bitrate.bitrate/1000}kbps`;
        resolutionSelect.appendChild(option);
    });
    resolutionSelect.value = bitrates.length - 1;
});