// ================= ROLE =================
function getRole(){
    return document.getElementById("role").value;
}

// ================= LOGIN =================
function login(){

    fetch("/auth/login",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            email:document.getElementById("loginEmail").value,
            password:document.getElementById("loginPassword").value
        })
    })

    .then(res=>res.json())
    .then(data=>{

        if(data.success){

            alert("Login successful");

            if(data.role==="student") location.href="/student_dashboard";
            if(data.role==="faculty") location.href="/faculty_dashboard";
            if(data.role==="admin") location.href="/admin_dashboard";

        }else{
            alert(data.message);
        }

    })
}

// ================= REGISTER =================
function register(){

    let role = getRole()

    let body = {

        name:document.getElementById("regName").value,
        email:document.getElementById("regEmail").value,
        password:document.getElementById("regPassword").value,
        role:role,

        roll:document.getElementById("regRoll")?.value,
        department:document.getElementById("regDept")?.value,

        emp_id:document.getElementById("regEmpId")?.value,
        subject:document.getElementById("regSubject")?.value,

        admin_key:document.getElementById("regAdminKey")?.value,

        face_image:document.getElementById("faceImage")?.value
    }

    if(role==="student" && !body.face_image){
        alert("Please capture face before registering")
        return
    }

    fetch("/auth/register",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(body)
    })

    .then(res=>res.json())
    .then(data=>{

        if(data.success){

            alert("Registration successful")
            showLogin()

        }else{
            alert(data.message)
        }

    })

}

// ================= FORM SWITCH =================
function showRegister(){

    document.getElementById("loginForm").style.display="none"
    document.getElementById("registerForm").style.display="block"

}

function showLogin(){

    document.getElementById("registerForm").style.display="none"
    document.getElementById("loginForm").style.display="block"

}

// ================= CAMERA =================
let video=document.getElementById("video")

function startCamera(){

    navigator.mediaDevices.getUserMedia({video:true})

    .then(stream=>{
        video.srcObject=stream
    })

    .catch(err=>{
        console.log(err)
    })
}

function captureFace(){

    let canvas=document.getElementById("canvas")
    let ctx=canvas.getContext("2d")

    canvas.width=video.videoWidth
    canvas.height=video.videoHeight

    ctx.drawImage(video,0,0)

    let image=canvas.toDataURL("image/png")

    document.getElementById("faceImage").value=image

    alert("Face captured")
}

// ================= ROLE CHANGE =================
document.getElementById("role").addEventListener("change",function(){

    let role=this.value

    document.getElementById("studentFields").style.display=role==="student"?"block":"none"
    document.getElementById("facultyFields").style.display=role==="faculty"?"block":"none"
    document.getElementById("adminFields").style.display=role==="admin"?"block":"none"

    if(role==="student") startCamera()

})