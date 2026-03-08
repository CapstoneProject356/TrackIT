let stream = null;

// Start camera
async function startCamera() {

    const video = document.getElementById("video");

    if (!video) {
        console.log("Video element not found");
        return;
    }

    try {

        // Stop old camera if running
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "user",
                width: { ideal: 640 },
                height: { ideal: 480 }
            },
            audio: false
        });

        video.srcObject = stream;
        video.setAttribute("playsinline", true); // Important for mobile
        await video.play();

    } catch (err) {
        console.error("Camera error:", err);
        alert("Unable to start camera. Please allow camera permission.");
    }
}


// Capture face
function captureFace() {

    const video = document.getElementById("video");

    if (video.readyState !== 4) {
        alert("Camera still loading. Please wait.");
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL("image/png");

    document.getElementById("faceImage").value = imageData;

    // Preview captured face
    const container = document.getElementById("capturedFaceContainer");
    container.innerHTML = "";

    const img = document.createElement("img");
    img.src = imageData;
    img.width = 320;
    img.className = "border rounded";

    container.appendChild(img);

    document.getElementById("faceStatus").innerText = "Face captured successfully!";

    verifyFace(canvas);
}


// Verify face with backend
function verifyFace(canvas) {

    canvas.toBlob(async function(blob) {

        const formData = new FormData();
        formData.append("user_id", localStorage.getItem("user_id"));
        formData.append("image", blob, "face.jpg");

        try {

            const response = await fetch("/face/verify", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            console.log("Face verification:", data);

            if (data.face_verified) {
                document.getElementById("faceStatus").innerText = "Face Verified ✅";
            } else {
                document.getElementById("faceStatus").innerText = "Face Not Verified ❌";
            }

        } catch (error) {
            console.error("Verification error:", error);
            document.getElementById("faceStatus").innerText = "Verification failed.";
        }

    }, "image/jpeg");
}


// Stop camera (important for mobile)
function stopCamera() {

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}


// Start camera when page loads
window.addEventListener("load", startCamera);