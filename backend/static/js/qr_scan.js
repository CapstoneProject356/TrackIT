let qrToken = "";

async function scanQR(fileInput) {
    const file = fileInput.files[0];
    if (!file) return;

    // Convert image to Base64 to send to backend
    const reader = new FileReader();
    reader.onload = async () => {
        const base64Image = reader.result.split(',')[1]; // Remove data prefix

        // Send to backend to verify QR
        const res = await fetch('/qr/verify', { // You may need to create this endpoint
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image })
        });

        const data = await res.json();
        if (data.valid) {
            qrToken = data.token;
            document.getElementById('status').innerText = "QR Verified ✅";
        } else {
            document.getElementById('status').innerText = "Invalid or expired QR ❌";
        }
    };
    reader.readAsDataURL(file);
}
