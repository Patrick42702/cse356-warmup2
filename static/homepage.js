// Path to the JSON file with video data
const jsonPath = "/static/m1.json";

// Function to generate the video list
async function generateVideoList() {
    const videoListContainer = document.getElementById("video-list");

    try {
        const response = await fetch('/api/videos', {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({count: 10})
        });
        const videoData = await response.json();
        const videos = videoData.videos;

        // Loop through each video entry in the JSON
        for (const video of videos) {
            // Extract video ID from filename
            const videoId = video.id;
            const description = video.description;

            // Create link element for the video
            const videoLink = document.createElement("a");
            videoLink.href = `/play/${videoId}`;
            videoLink.className = "video-link";

            // Create image element for the thumbnail
            const thumbnail = document.createElement("img");
            thumbnail.src = `/static/media/${videoId}/thumbnail_${videoId}.jpg`;
            thumbnail.alt = `Thumbnail for video ${videoId}`;
            thumbnail.className = "thumbnail";

            // Create description element
            const descriptionText = document.createElement("p");
            descriptionText.textContent = description;
            descriptionText.className = "description";

            // Append thumbnail and description to the link, and link to the container
            videoLink.appendChild(thumbnail);
            videoLink.appendChild(descriptionText);
            videoListContainer.appendChild(videoLink);
        }
    } catch (error) {
        console.error("Error fetching video data:", error);
    }
}

// Run the function when the page loads
window.addEventListener("DOMContentLoaded", generateVideoList);

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    
    if (uploadForm) {
        uploadForm.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Clicked!");
            window.location.href = '/upload';
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const logoutform = document.getElementById('logout-form');
    
    if (logoutform) {
        logoutform.addEventListener('click', async function(e) {
            e.preventDefault();
            console.log("Clicked!");
            const response = await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${document.cookie.split('=')[1]}`  // Fetch JWT token from cookie
                }
            });
            const result = await response.json();
            console.log(`Logout response: ${result}`);
            location.href = "/";
        });
    }
});