async function verifyGPS() {
    if (!navigator.geolocation) {
        alert("Geolocation not supported by your browser");
        return false;
    }

    return new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            const response = await fetch('/gps/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat: lat, lon: lon })
            });

            const data = await response.json();
            const statusMsg = data.within_geofence ? "GPS within campus ✅" : "GPS outside campus ❌";
            document.getElementById('status').innerText = statusMsg;
            resolve(data.within_geofence);
        });
    });
}
