const video = document.getElementById("video");

// Start camera when page loads
function startCamera(){

    const video = document.getElementById("video")

    if(!video){
        console.log("Video element not found")
        return
    }

    navigator.mediaDevices.getUserMedia({
    video: {
        width: 640,
        height: 480,
        facingMode: "user"
    }
})
    .then(stream => {
        video.srcObject = stream
        video.play()
    })
    .catch(err => {
        alert("Camera access denied or not available")
        console.error(err)
    })
}


// Capture face image
function captureFace() {

    const video = document.getElementById('video');

    if (video.readyState < 2) {
        alert("Video not ready yet. Please wait a moment.");
        return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/png');

    document.getElementById("faceImage").value = imageData;

    const container = document.getElementById('capturedFaceContainer');
    container.innerHTML = '';

    const img = document.createElement('img');
    img.src = imageData;
    img.width = 320;
    img.height = 240;
    img.className = 'border rounded';
    container.appendChild(img);

    document.getElementById('faceStatus').innerText = "Face captured successfully!";

    // Send image for verification
    verifyFace(canvas);
}


// Send captured image to backend
function verifyFace(canvas){

    canvas.toBlob(async function(blob){

        const formData = new FormData();
        formData.append("user_id", localStorage.getItem("user_id"));   // replace with logged-in user id
        formData.append("image", blob, "face.jpg");

        const response = await fetch("/face/verify", {
             method: "POST",
            body: formData
        });

        const data = await response.json();

        console.log("Face verification:", data);

        if(data.face_verified){
            document.getElementById("faceStatus").innerText = "Face Verified ✅";
        }else{
            document.getElementById("faceStatus").innerText = "Face Not Verified ❌";
        }

    }, "image/jpeg");
}


// Auto start camera
window.onload = startCamera;