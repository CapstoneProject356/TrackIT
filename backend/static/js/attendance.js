// Global variables
let gpsVerified = false;
let qrVerified = false;
let faceVerified = false;

let faceStream = null;
let qrScanner = null;


// ----------------- GPS Verification -----------------
function verifyGPS() {

    if (!navigator.geolocation) {
        showToast("Geolocation not supported", "warning");
        return;
    }

    navigator.geolocation.getCurrentPosition(async (position) => {

        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        const res = await fetch("/gps/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat, lon })
        });

        const data = await res.json();

        gpsVerified = data.within_geofence;

        document.getElementById("gpsStatus").innerText =
            gpsVerified ? "GPS verified ✅" : "Outside allowed area ❌";

        showToast(
            gpsVerified ? "GPS verified!" : "Outside geo-fence!",
            gpsVerified ? "success" : "danger"
        );

    }, (err) => {

        console.error(err);
        showToast("Failed to get GPS location", "danger");

    });

}


// ----------------- QR Scanner -----------------

function startQRScanner() {

    if (qrScanner) return;

    qrScanner = new Html5QrcodeScanner(
        "qr-reader",
        { fps: 10, qrbox: 250 }
    );

    qrScanner.render(onScanSuccess);

}


function onScanSuccess(decodedText) {

    document.getElementById("qrStatus").innerText = "QR detected. Verifying...";

    // Extract token if QR contains full URL
    let token = decodedText;

    if (decodedText.includes("token=")) {
        token = decodedText.split("token=")[1].trim();
    }

    fetch("/qr/verify", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            token: token
        })
    })
    .then(res => res.json())
    .then(data => {

        qrVerified = data.valid;

        if (data.valid) {

            document.getElementById("qrStatus").innerText = "QR verified ✅";

            showToast("QR verified!", "success");

            // Stop QR scanner
            qrScanner.clear();
            qrScanner = null;

            // Start face camera after small delay
            setTimeout(() => {
                startFaceCamera();
            }, 500);

        } else {

            document.getElementById("qrStatus").innerText = "QR expired ❌";
            showToast("Invalid QR", "danger");

        }

    });

}


// ----------------- Face Camera -----------------

async function startFaceCamera() {

    const video = document.getElementById("video");

    try {

        if (faceStream) {
            faceStream.getTracks().forEach(track => track.stop());
        }

        faceStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "user",
                width: { ideal: 640 },
                height: { ideal: 480 }
            },
            audio: false
        });

        video.srcObject = faceStream;

        video.onloadedmetadata = () => {
            video.play();
        };

    }
    catch (err) {

        console.error(err);
        showToast("Unable to access camera", "danger");

    }

}


// ----------------- Capture Face -----------------

function captureFace() {

    const video = document.getElementById("video");

    if (video.readyState !== 4) {

        showToast("Camera still loading. Please wait.", "warning");
        return;

    }

    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const img = document.createElement("img");
    img.src = canvas.toDataURL("image/png");
    img.width = 200;

    const container = document.getElementById("capturedFaceContainer");

    container.innerHTML = "";
    container.appendChild(img);


    canvas.toBlob(async (blob) => {

        const formData = new FormData();

        formData.append("image", blob);
        formData.append("user_id", localStorage.getItem("user_id"));

        const res = await fetch("/face/verify", {
            method: "POST",
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

async function markAttendance() {

    if (!gpsVerified || !qrVerified || !faceVerified) {

        showToast("Complete all steps first", "warning");
        return;

    }

    const video = document.getElementById("video");

    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const blob = await new Promise(resolve =>
        canvas.toBlob(resolve, "image/png")
    );

    const formData = new FormData();

    formData.append("image", blob);
    formData.append("user_id", localStorage.getItem("user_id"));

    const res = await fetch("/attendance/mark", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    if (data.success) {

        showToast("Attendance marked successfully", "success");

    } else {

        showToast(data.error, "danger");

    }

}


// ----------------- Toast Helper -----------------

function showToast(message, type = "primary") {

    const toastEl = document.getElementById("liveToast");
    const toastMsg = document.getElementById("toastMsg");

    toastEl.className =
        `toast align-items-center text-white bg-${type} border-0`;

    toastMsg.innerText = message;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();

}