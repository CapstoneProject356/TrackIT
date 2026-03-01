// Helper: show toast messages
function showToast(message, type = "primary") {
    const toastEl = document.getElementById("liveToast");
    const toastMsg = document.getElementById("toastMsg");

    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastMsg.innerText = message;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// ----------------- Load Daily Report -----------------
async function loadDailyReport() {
    try {
        const res = await fetch('/api/reports/daily');
        const data = await res.json();

        renderReportTable(data, "Daily Attendance Report");
        showToast("Daily report loaded!", "success");
    } catch (err) {
        console.error(err);
        showToast("Failed to load daily report", "danger");
    }
}

// ----------------- Load Monthly Report -----------------
async function loadMonthlyReport() {
    try {
        const res = await fetch('/api/reports/monthly');
        const data = await res.json();

        renderReportTable(data, "Monthly Attendance Report");
        showToast("Monthly report loaded!", "success");
    } catch (err) {
        console.error(err);
        showToast("Failed to load monthly report", "danger");
    }
}

// ----------------- Load Student-wise Report -----------------
async function loadStudentReport() {
    try {
        const res = await fetch('/api/reports/student');
        const data = await res.json();

        renderReportTable(data, "Student-wise Attendance Report");
        showToast("Student-wise report loaded!", "success");
    } catch (err) {
        console.error(err);
        showToast("Failed to load student report", "danger");
    }
}

// ----------------- Render Table -----------------
function renderReportTable(data, title) {
    const container = document.getElementById("reportTable");
    if (!data || data.length === 0) {
        container.innerHTML = `<p class="text-center mt-3">No records found for ${title}</p>`;
        return;
    }

    let html = `<h4 class="mb-3">${title}</h4>`;
    html += `<table class="table table-striped table-bordered">`;
    html += `<thead class="table-dark"><tr>`;

    // Table headers from keys of first object
    Object.keys(data[0]).forEach(key => {
        html += `<th>${key}</th>`;
    });
    html += `</tr></thead><tbody>`;

    data.forEach(row => {
        html += `<tr>`;
        Object.values(row).forEach(val => {
            html += `<td>${val}</td>`;
        });
        html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}
