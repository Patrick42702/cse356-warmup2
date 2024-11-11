let videoList = []; // Holds all loaded videos
let currentIndex = 0; // Tracks the current video index

// Extract video ID from URL
function getVideoIdFromUrl() {
    const pathSegments = window.location.pathname.split('/');
    return pathSegments[pathSegments.length - 1];
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
        } else {
        playVideoAtIndex(0); // Play the first video by default if ID is not found
    }
    } else {
        playVideoAtIndex(0); // Play the first video by default if no ID is in the URL
    }
}

// Populate videos div with video elements, keeping them paused initially
function populateVideos(videos) {
    const videosDiv = document.getElementById("videos");

    videos.forEach((video, index) => {
        const videoElement = document.createElement("video");
        videoElement.setAttribute("data-index", index);
        videoElement.src = `../static/media/${video.id}/${video.id}.mpd`;
        videoElement.controls = true;
        // videoElement.muted = true;
        videoElement.pause();
        videoElement.style.display = "none";
        videosDiv.appendChild(videoElement);
    });
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

// Play the video at the given index and update the URL
function playVideoAtIndex(index) {
    const videosDiv = document.getElementById("videos");
    const currentVideo = videosDiv.querySelector(`[data-index="${currentIndex}"]`);
    const newVideo = videosDiv.querySelector(`[data-index="${index}"]`);

    if (currentVideo) {
        currentVideo.pause();
        currentVideo.style.display = "none";
    }

    if (newVideo) {
        newVideo.play();
        newVideo.style.display = "block";
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
