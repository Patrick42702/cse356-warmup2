document.addEventListener('DOMContentLoaded', function() {
    // Get the submit button by its ID or another selector
    const submitButton = document.getElementById('submit-button');

    // Add click event listener to the button
    submitButton.addEventListener('click', function() {
        document.getElementById('upload-form').submit();
        location.href = "/";
    });
});