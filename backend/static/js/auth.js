function getRole() {
    return document.getElementById("role").value;
}

// LOGIN
function login() {
    fetch("/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: document.getElementById("loginEmail").value,
            password: document.getElementById("loginPassword").value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast("Login successful", "bg-success");

            setTimeout(() => {
                if (data.role === "student") location.href = "/student_dashboard";
                if (data.role === "faculty") location.href = "/faculty_dashboard";
                if (data.role === "admin") location.href = "/admin_dashboard";
            }, 1000);
        } else {
            showToast(data.message, "bg-danger");
        }
    });
}

// REGISTER
function register() {
    fetch("/auth/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: document.getElementById("regName").value,
            email: document.getElementById("regEmail").value,
            password: document.getElementById("regPassword").value,
            role: getRole()
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast("Registration successful! Login now.", "bg-success");
            showLogin();
        } else {
            showToast(data.message, "bg-danger");
        }
    });
}

// TOAST
function showToast(message, bg) {
    const toastEl = document.getElementById("liveToast");
    const toastMsg = document.getElementById("toastMsg");

    toastEl.className = `toast align-items-center text-white ${bg} border-0`;
    toastMsg.innerText = message;

    new bootstrap.Toast(toastEl).show();
}

// FORM SWITCH
function showRegister() {
    document.getElementById("loginForm").style.display = "none";
    document.getElementById("registerForm").style.display = "block";
}

function showLogin() {
    document.getElementById("registerForm").style.display = "none";
    document.getElementById("loginForm").style.display = "block";
}
