// Path to the JSON file with video data
const jsonPath = "/static/m1.json";

// Function to generate the video list
async function generateVideoList() {
    const videoListContainer = document.getElementById("video-list");

    try {
        // Fetch video data from JSON file
        const response = await fetch(jsonPath);
        const videoData = await response.json();

        // Loop through each video entry in the JSON
        for (const [filename, description] of Object.entries(videoData).slice(0,10)) {
            // Extract video ID from filename
            const videoId = filename.split('-')[0];

            // Create link element for the video
            const videoLink = document.createElement("a");
            videoLink.href = `/play/${videoId}`;
            videoLink.className = "video-link";

            // Create image element for the thumbnail
            const thumbnail = document.createElement("img");
            thumbnail.src = `/static/media/thumbnail_${videoId}.jpg`;
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