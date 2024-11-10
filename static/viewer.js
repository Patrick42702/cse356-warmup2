// Video list - this should match the format you defined on the server
let videoList = []; // Will be populated with data from m1.json
let currentIndex = 0; // Index of the currently playing video

// Fetch video list on load
async function loadVideoList() {
    const response = await fetch('/api/videos', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({count: 100})
    });
    const data = await response.json();
    videoList = data.videos.map((video) => {
        return { id: video.id, metadata: video };
    });

    // Find initial video based on URL and play it
    const videoId = window.location.pathname.split('/').pop();
    currentIndex = videoList.findIndex(video => video.id === videoId) || 0;
    await playVideo(currentIndex);
}

async function loadMoreVideos() {
    console.log("Loading more videos");
    const response = await fetch('/api/videos', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({count: 100})
    });
    const data = await response.json();
    const newVideos = data.videos.map(video => ({ id: video.id, metadata: video }));
    videoList = [...videoList.slice(currentIndex+1, videoList.length), ...newVideos];
    currentIndex = 0;
}


// Function to play the video at the given index
async function playVideo(index) {
    if (index < 0 || index >= videoList.length) return; // Check bounds

    const video = videoList[index];
    const response = await fetch("/api/view", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({id: video.id})
    });
    console.log('Viewed: ' + response)
    const videoPlayer = document.getElementById('videoPlayer');

    // Destroy any previous player instance to clear buffers
    if (window.player) {
        window.player.reset();
    }

    // Create a new Dash.js player instance
    window.player = dashjs.MediaPlayer().create();
    window.player.initialize(videoPlayer, `../static/media/${video.id}/${video.id}.mpd`, true);
    const resolutionSelect = document.getElementById('resolutionSelect');
    const quality = parseInt(resolutionSelect.value);
    player.setQualityFor('video', quality);
    document.getElementById('playPauseBtnButton').innerText = 'Pause';

    // Update the URL without reloading the page
    window.history.pushState({}, '', `/play/${video.id}`);
}

// Handle scroll event for infinite scroll navigation
// function handleScroll(event) {
//     const scrollY = window.scrollY || document.documentElement.scrollTop;
//
//     if (scrollY > 0) {  // Scroll down
//         if (currentIndex < videoList.length - 1) {
//             currentIndex++;
//             playVideo(currentIndex);
//         }
//     } else if (scrollY < 0) {  // Scroll up
//         if (currentIndex > 0) {
//             currentIndex--;
//             playVideo(currentIndex);
//         }
//     }
//
//     // Reset scroll position to avoid cumulative scroll effect
//     window.scrollTo(0, 0);
// }

function handleScrollWheel(event) {
    event.preventDefault();
    if (event.deltaY > 0) { // Scroll down
        if (currentIndex < videoList.length - 5) {
            currentIndex++;
            playVideo(currentIndex);
        } else if (currentIndex >= videoList.length - 10) {
            loadMoreVideos();
            currentIndex++;
            playVideo(currentIndex);
        }
    } else if (event.deltaY < 0) { // Scroll up
        if (currentIndex > 0) {
            currentIndex--;
            playVideo(currentIndex);
        }
    }
}


// Load video list and set up initial video
document.addEventListener('DOMContentLoaded', async () => {
    await loadVideoList();
    window.addEventListener('wheel', handleScrollWheel, { passive: false });
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
player.initialize(videoPlayer, `../static/media/${video_id}/${video_id}.mpd`, false);

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

// Like/Dislike Button
const likeBtn = document.getElementById("like");
const dislikeBtn = document.getElementById("dislike");
likeBtn.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/like", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({id: video_id, value: true})
        });
        console.log(response);
    } catch (error) {
        console.error(error);
    }
})
dislikeBtn.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/like", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({id: video_id, value: false})
        });
        console.log(response);
    } catch (error) {
        console.error(error);
    }
})

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