// ---------------- GLOBAL VARIABLES ----------------
let gpsVerified = false;
let qrVerified = false;
let faceVerified = false;

let latitude = null;
let longitude = null;
let sessionId = null;

let faceStream = null;
let qrScanner = null;

// ---------------- GPS VERIFICATION ----------------
function verifyGPS() {
    if (!navigator.geolocation) {
        showToast("Geolocation not supported", "warning");
        return;
    }

    navigator.geolocation.getCurrentPosition(async (position) => {
        latitude = position.coords.latitude;
        longitude = position.coords.longitude;

        const res = await fetch("/gps/verify", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({ lat: latitude, lon: longitude })
        });

        const data = await res.json();

        gpsVerified = data.within_geofence;

        document.getElementById("gpsStatus").innerText =
            gpsVerified ? "GPS verified ✅" : "Outside allowed area ❌";

        showToast(
            gpsVerified ? "GPS verified!" : "Outside geo-fence!",
            gpsVerified ? "success" : "danger"
        );
    });
}

// ---------------- QR SCANNER (Camera) ----------------
function startQRScanner() {
    if(qrVerified) return;

    qrScanner = new Html5Qrcode("qr-reader");

    Html5Qrcode.getCameras().then(devices => {
        if (!devices.length) {
            showToast("No camera found","danger");
            return;
        }

        // Prefer back camera
        let backCamera = devices.find(cam => cam.label.toLowerCase().includes("back"));
        const cameraId = backCamera ? backCamera.id : devices[0].id;

        qrScanner.start(
            cameraId,
            { fps: 10, qrbox: { width: 250, height: 250 } },
            onQRScanned
        );
    }).catch(err => {
        console.log("Camera error:", err);
        showToast("Camera access denied","danger");
    });
}

// ---------------- QR SCANNER (File Upload) ----------------
async function scanQRFile(fileInput) {
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async () => {
        const base64Image = reader.result.split(',')[1]; // Remove data prefix

        const res = await fetch('/qr/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image })
        });

        const data = await res.json();
        if(data.valid){
            qrVerified = true;
            sessionId = data.session_id;
            document.getElementById("qrStatus").innerText = "QR verified ✅";
            showToast("QR verified!", "success");

            // Stop camera if active
            if(qrScanner) qrScanner.stop();

            startFaceCamera();
        } else {
            document.getElementById("qrStatus").innerText = "Invalid or expired QR ❌";
            showToast("Invalid or expired QR", "danger");
        }
    };
    reader.readAsDataURL(file);
}

// ---------------- QR SUCCESS HANDLER ----------------
function onQRScanned(decodedText) {
    if(qrVerified) return;

    let token = decodedText;
    if(decodedText.includes("token=")) token = decodedText.trim();

    fetch("/qr/verify", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ token })
    })
    .then(res => res.json())
    .then(data => {
        if (data.valid) {
            qrVerified = true;
            sessionId = data.session_id;
            document.getElementById("qrStatus").innerText = "QR verified ✅";
            showToast("QR verified!", "success");

            if(qrScanner) qrScanner.stop();
            startFaceCamera();
        } else {
            document.getElementById("qrStatus").innerText = "QR expired ❌";
            showToast("Invalid or expired QR", "danger");
        }
    });
}

// ---------------- FACE CAMERA ----------------
async function startFaceCamera() {
    const video = document.getElementById("video");
    try {
        if (faceStream) faceStream.getTracks().forEach(t => t.stop());

        faceStream = await navigator.mediaDevices.getUserMedia({ video:{ facingMode:"user" }, audio:false });
        video.srcObject = faceStream;
        video.onloadedmetadata = () => video.play();
    } catch(err){
        console.error(err);
        showToast("Unable to access camera","danger");
    }
}

// ---------------- FACE VERIFY ----------------
async function captureFace() {
    const video = document.getElementById("video");
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video,0,0);

    const blob = await new Promise(resolve => canvas.toBlob(resolve,"image/png"));
    const formData = new FormData();
    formData.append("image", blob);
    formData.append("user_id", localStorage.getItem("user_id"));

    const res = await fetch("/face/verify",{ method:"POST", body:formData });
    const data = await res.json();

    faceVerified = data.face_verified;
    document.getElementById("faceStatus").innerText =
        faceVerified ? "Face verified ✅" : "Face failed ❌";

    showToast(faceVerified ? "Face verified!" : "Face failed", faceVerified ? "success" : "danger");
}

// ---------------- MARK ATTENDANCE ----------------
async function markAttendance(){
    if(!gpsVerified || !qrVerified || !faceVerified){
        showToast("Complete all steps first","warning");
        return;
    }

    const video = document.getElementById("video");
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video,0,0);

    const blob = await new Promise(resolve => canvas.toBlob(resolve,"image/png"));
    const formData = new FormData();
    formData.append("student_id", localStorage.getItem("user_id"));
    formData.append("session_id", sessionId);
    formData.append("latitude", latitude);
    formData.append("longitude", longitude);
    formData.append("face_image", blob);

    const res = await fetch("/attendance/mark",{ method:"POST", body: formData });
    const data = await res.json();

    if(data.success){
        showToast("Attendance marked successfully","success");
    } else {
        showToast(data.error,"danger");
    }
}

// ---------------- TOAST ----------------
function showToast(message,type="primary"){
    const toastEl = document.getElementById("liveToast");
    const toastMsg = document.getElementById("toastMsg");
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastMsg.innerText = message;
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// ---------------- PAGE LOAD ----------------
window.addEventListener("load",()=>{ verifyGPS(); });