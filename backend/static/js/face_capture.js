const video = document.getElementById("video");

// Start camera when page loads
async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });
        video.srcObject = stream;
    } catch (error) {
        document.getElementById("faceStatus").innerText =
            "Camera access denied or not available";
    }
}

// Capture face image
function captureFace() {
    const video = document.getElementById('video');

    // Make sure video is ready
    if (video.readyState < 2) { // HAVE_CURRENT_DATA
        alert("Video not ready yet. Please wait a moment.");
        return;
    }

    // Create canvas to grab frame
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 320; // fallback width
    canvas.height = video.videoHeight || 240; // fallback height
    const ctx = canvas.getContext('2d');

    // Draw the video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to image
    const imageData = canvas.toDataURL('image/png');

    // Show captured image
    const container = document.getElementById('capturedFaceContainer');
    container.innerHTML = ''; // clear previous
    const img = document.createElement('img');
    img.src = imageData;
    img.width = 320; 
    img.height = 240;
    img.className = 'border rounded';
    container.appendChild(img);

    // Update status
    document.getElementById('faceStatus').innerText = "Face captured successfully!";
}



// Auto start camera
window.onload = startCamera;
