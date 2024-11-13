let videoList = []; // Holds all loaded videos
let currentIndex = 0; // Tracks the current video index
let playerInstances = []; // Stores Dash.js player instances for each video
const resolutionSelect = document.getElementById("resolutionSelect");
const playPauseBtn = document.getElementById("playPauseBtn");
const seekBar = document.getElementById("seekBar");
const num_fetch_videos = 20;

// Extract Video ID from URL
function getVideoIdFromUrl() {
    const pathSegments = window.location.pathname.split('/');
    return pathSegments[pathSegments.length - 1];
}

// Initialize Dash.js player with resolution selection
function initializeDashPlayer(videoElement, videoId) {
    const player = dashjs.MediaPlayer().create();
    player.initialize(videoElement, `../static/media/${videoId}/${videoId}.mpd`, false);

    // Add resolution selection
    player.updateSettings({ streaming: { abr: { autoSwitchBitrate: false } } });

    player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, function () {
        const availableQualities = player.getBitrateInfoListFor("video");
        resolutionSelect.innerHTML = ''; // Clear existing options

        availableQualities.forEach((quality, index) => {
            const option = document.createElement("option");
            option.value = index;
            option.textContent = `${quality.height}p`;
            resolutionSelect.appendChild(option);
        });
    });

    // Event listener for resolution selection
    resolutionSelect.addEventListener("change", () => {
        const selectedQualityIndex = parseInt(resolutionSelect.value, 10);
        playerInstances[currentIndex].setQualityFor("video", selectedQualityIndex);
    });

    return player;
}

// Populate videos div with initialized Dash.js video players, keeping them paused initially and hidden
function populateVideos(videos) {
    const videosDiv = document.getElementById("videos");

    videos.forEach((video, index) => {
        const videoElement = document.createElement("video");
        videoElement.setAttribute("data-index", index + videoList.length - num_fetch_videos);
        videoElement.controls = true;
        videoElement.muted = true;
        // videoElement.pause();
        videoElement.style.display = "none"; // Hide video initially
        videosDiv.appendChild(videoElement);

        // Initialize the Dash.js player and store it in playerInstances
        const playerInstance = initializeDashPlayer(videoElement, video.id);
        playerInstance.pause();
        playerInstances.push(playerInstance);
    });
}

// Fetch initial list of videos on load
async function loadVideoList() {
    const response = await fetch('/api/videos', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: num_fetch_videos })
    });
    const data = await response.json();
    videoList = data.videos.map(video => ({ id: video.id, metadata: video }));
    populateVideos(videoList);

    const initialVideoId = getVideoIdFromUrl();
    if (initialVideoId) {
        const initialIndex = videoList.findIndex(video => video.id === initialVideoId);
        if (initialIndex !== -1) {
            playVideoAtIndex(initialIndex);
        }
    } else {
        playVideoAtIndex(0); // Play the first video by default if no ID is in the URL
    }
}

// Fetch and add more videos when near the end of the list
async function loadMoreVideos() {
    const response = await fetch('/api/videos', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: num_fetch_videos })
    });
    const data = await response.json();
    const newVideos = data.videos.map(video => ({ id: video.id, metadata: video }));
    videoList = [...videoList, ...newVideos];
    populateVideos(newVideos);
}

// Play the video at the given index, pause others, update the URL, and control visibility
function playVideoAtIndex(index) {
    const videosDiv = document.getElementById("videos");
    const currentVideo = videosDiv.querySelector(`[data-index="${currentIndex}"]`);
    const newVideo = videosDiv.querySelector(`[data-index="${index}"]`);

    if (currentVideo) {
        currentVideo.style.display = "none"; // Hide previous video
    }

    if (newVideo) {
        // playerInstances[index].play();
        newVideo.style.display = "block"; // Show and play new video
        currentIndex = index;
        window.history.pushState({}, '', `/play/${videoList[currentIndex].id}`);

         playerInstances[currentIndex].on(dashjs.MediaPlayer.events.PLAYBACK_METADATA_LOADED, () => {
            seekBar.max = playerInstances[currentIndex].duration();
         });
    }
}

// Handle scroll event to navigate through videos
function handleScroll(event) {
    event.preventDefault();

    const currentPlayer = playerInstances[currentIndex];
    if (!currentPlayer.isPaused()) {
        playPauseBtn.click();
    }

    if (event.deltaY > 0) { // Scroll down
        if (currentIndex < videoList.length - 1) {
            playVideoAtIndex(currentIndex + 1);
        }
        if (currentIndex >= videoList.length - 5) {
            loadMoreVideos(); // Fetch more videos when near the end of the list
        }
    } else if (event.deltaY < 0 && currentIndex > 0) { // Scroll up
        playVideoAtIndex(currentIndex - 1);
    }
}

function clickPlayPauseBtn() {
    const currentPlayer = playerInstances[currentIndex];
    if (currentPlayer.isPaused()) {
        playPauseBtn.textContent = "Pause";
        currentPlayer.play();
    } else {
        playPauseBtn.textContent = "Play";
        currentPlayer.pause();
    }
}

// Seek bar functionality
seekBar.addEventListener("input", () => {
    const currentPlayer = playerInstances[currentIndex];
    currentPlayer.seek(seekBar.value);
});

// Update seek bar as video plays
function updateSeekBar() {
    const currentPlayer = playerInstances[currentIndex];
    if (currentPlayer) {
        seekBar.value = currentPlayer.time();
        requestAnimationFrame(updateSeekBar);
    }
}

// Initialize video list and set up scroll event
document.addEventListener("DOMContentLoaded", async () => {
    await loadVideoList();
    window.addEventListener("wheel", handleScroll, { passive: false });
    updateSeekBar();
    playPauseBtn.addEventListener("click", () => clickPlayPauseBtn());
});

// Like/Dislike Button
const likeBtn = document.getElementById("like");
const dislikeBtn = document.getElementById("dislike");
likeBtn.addEventListener("click", async () => {
    try {
        const response = await fetch("/api/like", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({id: getVideoIdFromUrl(), value: true})
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
            body: JSON.stringify({id: getVideoIdFromUrl(), value: false})
        });
        console.log(response);
    } catch (error) {
        console.error(error);
    }
})

