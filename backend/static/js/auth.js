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

    let role = document.getElementById("role").value

    // check face for student
    if(role === "student" && !document.getElementById("faceImage").value){
        alert("Please capture your face before registering")
        return
    }

    fetch("/auth/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({

            name: document.getElementById("regName").value,
            email: document.getElementById("regEmail").value,
            password: document.getElementById("regPassword").value,
            role: role,

            roll: document.getElementById("regRoll")?.value,
            department: document.getElementById("regDept")?.value,

            emp_id: document.getElementById("regEmpId")?.value,
            subject: document.getElementById("regSubject")?.value,

            admin_key: document.getElementById("regAdminKey")?.value,

            face_image: document.getElementById("faceImage").value
        })
    })

    .then(res => res.json())

    .then(data => {

        if(data.success){

            alert("Registration successful")

            showLogin()

        }else{

            alert(data.message || "Registration failed")

        }

    })

    .catch(error => {
        console.error(error)
        alert("Error connecting to server")
    })

}

// TOAST
function toggleRoleFields(){

    let role = document.getElementById("role").value

    document.getElementById("studentFields").style.display = role==="student" ? "block" : "none"
    document.getElementById("facultyFields").style.display = role==="faculty" ? "block" : "none"
    document.getElementById("adminFields").style.display = role==="admin" ? "block" : "none"

    if(role === "student"){
        startCamera()
    }
}

// FORM SWITCH
function showRegister(){

    document.getElementById("loginForm").style.display="none"
    document.getElementById("registerForm").style.display="block"

    let role = document.getElementById("role").value

    if(role === "student"){
        startCamera()
    }
}

function showLogin() {
    document.getElementById("registerForm").style.display = "none";
    document.getElementById("loginForm").style.display = "block";
}
