// Global variables to store step status
let gpsVerified = false;
let qrVerified = false;
let faceVerified = false;
//let qrToken = null;

// ----------------- GPS Verification -----------------
function verifyGPS() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            const res = await fetch('/gps/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ lat, lon })
            });

            const data = await res.json();
            gpsVerified = data.within_geofence;

            document.getElementById("gpsStatus").innerText = gpsVerified 
                ? "GPS verified ✅"
                : "You are outside the allowed area ❌";

            showToast(gpsVerified ? "GPS verified!" : "Outside geo-fence!", gpsVerified ? "success" : "danger");
        }, (err) => {
            console.error(err);
            showToast("Failed to get GPS location", "danger");
        });
    } else {
        showToast("Geolocation not supported", "warning");
    }
}

// ----------------- QR Verification -----------------
function scanQR(input) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async function(e) {
        const base64Image = e.target.result;

        const res = await fetch('/qr/verify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ image: base64Image })
        });

        const data = await res.json();
        qrVerified = data.valid;
        qrToken = data.token;

        document.getElementById("qrStatus").innerText = qrVerified 
            ? "QR verified ✅" 
            : "Invalid or expired QR ❌";

        showToast(qrVerified ? "QR verified!" : "Invalid QR!", qrVerified ? "success" : "danger");
    };
    reader.readAsDataURL(file);
}

// ----------------- Face Capture -----------------
function captureFace() {

    const video = document.getElementById("video");

    if (video.videoWidth === 0) {
        showToast("Camera not ready yet. Try again.", "warning");
        return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    // Show captured image (for debugging)
    const img = document.createElement("img");
    img.src = canvas.toDataURL("image/png");
    img.width = 200;

    const container = document.getElementById("capturedFaceContainer");
    container.innerHTML = "";
    container.appendChild(img);

    canvas.toBlob(async (blob) => {

        const formData = new FormData();
        formData.append("image", blob);
        formData.append("user_id", localStorage.getItem("user_id"))

        const res = await fetch('/face/verify', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        faceVerified = data.face_verified;

        document.getElementById("faceStatus").innerText =
            faceVerified ? "Face verified ✅" : "Face verification failed ❌";

        showToast(
            faceVerified ? "Face verified!" : "Face verification failed",
            faceVerified ? "success" : "danger"
        );

    }, "image/png");
}
// ----------------- Mark Attendance -----------------
async function markAttendance(){

    if(!gpsVerified || !qrVerified || !faceVerified){
        showToast("Complete all steps first", "warning")
        return
    }

    const canvas = document.createElement("canvas")
    const video = document.getElementById("video")

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext("2d")
    ctx.drawImage(video,0,0)

    const blob = await new Promise(resolve =>
        canvas.toBlob(resolve,"image/png")
    )

    const formData = new FormData();

formData.append("image", blob);
formData.append("user_id", localStorage.getItem("user_id"));

const res = await fetch('/attendance/mark', {
    method: 'POST',
    body: formData
})

    const data = await res.json()

    if(data.success){
        showToast("Attendance marked successfully","success")
    }else{
        showToast(data.error,"danger")
    }

}

// ----------------- Toast Helper -----------------
function showToast(message, type = "primary") {
    const toastEl = document.getElementById("liveToast");
    const toastMsg = document.getElementById("toastMsg");

    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastMsg.innerText = message;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// ----------------- Initialize Video Stream -----------------
navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {

    const video = document.getElementById("video");
    video.srcObject = stream;

    video.onloadedmetadata = () => {
        video.play();
    };

})
.catch(err => {
    console.error(err);
    showToast("Camera not accessible", "danger");
});