let videoList = []; // Holds all loaded videos
let currentIndex = 0; // Tracks the current video index
let playerInstances = []; // Stores Dash.js player instances for each video

// Extract Video ID from URL
function getVideoIdFromUrl() {
    const pathSegments = window.location.pathname.split('/');
    return pathSegments[pathSegments.length - 1];
}

// Initialize Dash.js player with resolution selection
function initializeDashPlayer(videoElement, videoId) {
    const player = dashjs.MediaPlayer().create();
    player.initialize(videoElement, `../static/media/${videoId}/${videoId}.mpd`, true);

    // Add resolution selection
    player.updateSettings({ streaming: { abr: { autoSwitchBitrate: false } } });

    // Create a dropdown for manual resolution selection
    const qualitySelect = document.createElement("select");
    qualitySelect.addEventListener("change", () => {
        const selectedQualityIndex = parseInt(qualitySelect.value, 10);
        player.setQualityFor("video", selectedQualityIndex);
    });

    // Populate the resolution dropdown
    player.on(dashjs.MediaPlayer.events.STREAM_INITIALIZED, function() {
        const availableQualities = player.getBitrateInfoListFor("video");
        availableQualities.forEach((quality, index) => {
            const option = document.createElement("option");
            option.value = index;
            option.textContent = `${quality.height}p`;
            qualitySelect.appendChild(option);
        });
    });

    videoElement.parentNode.insertBefore(qualitySelect, videoElement.nextSibling); // Place it below the video
    return player;
}

// Populate videos div with initialized Dash.js video players, keeping them paused initially and hidden
function populateVideos(videos) {
    const videosDiv = document.getElementById("videos");

    videos.forEach((video, index) => {
        const videoElement = document.createElement("video");
        videoElement.setAttribute("data-index", index);
        videoElement.controls = true;
        videoElement.muted = true;
        videoElement.pause();
        videoElement.style.display = "none"; // Hide video initially
        videosDiv.appendChild(videoElement);

        // Initialize the Dash.js player and store it in playerInstances
        const playerInstance = initializeDashPlayer(videoElement, video.id);
        playerInstances.push(playerInstance);
    });
}

// Fetch initial list of videos on load
async function loadVideoList() {
    const response = await fetch('/api/videos', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: 20 })
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
        body: JSON.stringify({ count: 20 })
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
        playerInstances[currentIndex].pause();
        currentVideo.style.display = "none"; // Hide previous video
    }

    if (newVideo) {
        playerInstances[index].play();
        newVideo.style.display = "block"; // Show and play new video
        currentIndex = index;
        window.history.pushState({}, '', `/play/${videoList[currentIndex].id}`);
    }
}

// Handle scroll event to navigate through videos
function handleScroll(event) {
    event.preventDefault();

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

// Initialize video list and set up scroll event
document.addEventListener("DOMContentLoaded", async () => {
    await loadVideoList();
    window.addEventListener("wheel", handleScroll, { passive: false });
});
