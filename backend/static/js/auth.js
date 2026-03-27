// Wait until page loads
document.addEventListener("DOMContentLoaded", function () {

    // ================= ROLE =================
    function getRole(){
        return document.getElementById("role").value;
    }

    // ================= LOGIN =================
    window.login = function(){

        fetch("/auth/login",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                email:document.getElementById("loginEmail").value,
                password:document.getElementById("loginPassword").value,
            })
        })

        .then(res=>res.json())
        .then(data=>{

            if(data.success){

                alert("Login successful");
                localStorage.setItem("user_id", data.user_id)
                if(data.role==="student") location.href="/student_dashboard";
                if(data.role==="faculty") location.href="/faculty_dashboard";
                if(data.role==="admin") location.href="/admin_dashboard";

            }else{
                alert(data.message);
            }

        })
    }

    // ================= REGISTER =================
    window.register = function(){

    let name = document.getElementById("regName").value.trim()
    let email = document.getElementById("regEmail").value.trim()
    let password = document.getElementById("regPassword").value.trim()
    let role = getRole()

    let roll = document.getElementById("regRoll")?.value.trim()
    let dept = document.getElementById("regDept")?.value.trim()
    let student_class = document.getElementById("regClass")?.value
    let emp_id = document.getElementById("regEmpId")?.value.trim()
    let subject = document.getElementById("regSubject")?.value.trim()
    let admin_key = document.getElementById("regAdminKey")?.value.trim()
    let face_image = document.getElementById("faceImage")?.value


    // NAME VALIDATION
    if(name === ""){
        alert("Name is required")
        return
    }

    // EMAIL VALIDATION
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if(!emailPattern.test(email)){
        alert("Enter a valid email address")
        return
    }

    // PASSWORD VALIDATION
    const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/

    if(!passwordPattern.test(password)){
        alert("Password must be 8+ characters with letter, number, and symbol")
        return
    }

    // STUDENT VALIDATION
    if(role==="student"){

    if(roll==="" || dept==="" || student_class===""){
        alert("Please fill Roll Number, Department and Class")
        return
    }

    // ✅ INTEGER VALIDATION
    if(!/^\d+$/.test(roll)){
        alert("Roll Number must be a valid integer")
        return
    }

    if(!face_image){
        alert("Please capture face before registering")
        return
    }
}

    // FACULTY VALIDATION
if(role==="faculty"){

    if(emp_id==="" || subject===""){
        alert("Please fill Employee ID and Subject")
        return
    }

    // ✅ INTEGER VALIDATION
    if(!/^\d+$/.test(emp_id)){
        alert("Employee ID must be a valid integer")
        return
    }
}
    // ADMIN VALIDATION
    if(role==="admin"){

        if(admin_key===""){
            alert("Admin secret key required")
            return
        }

    }


    fetch("/auth/register",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            name:name,
            email:email,
            password:password,
            role:role,
            roll:roll,
            department:dept,
            student_class: student_class, 
            emp_id:emp_id,
            subject:subject,
            admin_key:admin_key,
            face_image:face_image
        })
    })

    .then(res=>res.json())
    .then(data=>{

        if(data.success){
            alert("Registration successful")
            showLogin()
        }
        else{
            alert(data.message)
        }

    })

}

    // ================= FORM SWITCH =================
    window.showRegister = function(){

        document.getElementById("loginForm").style.display="none"
        document.getElementById("registerForm").style.display="block"

        document.getElementById("formTitle").innerText="Register"

        let role=document.getElementById("role").value

        if(role==="student"){
            startCamera()
        }

    }

    window.showLogin = function(){

        document.getElementById("registerForm").style.display="none"
        document.getElementById("loginForm").style.display="block"

        document.getElementById("formTitle").innerText="Login"

        stopCamera()

    }

    // ================= CAMERA =================
    let video=document.getElementById("video")
    let stream=null

    function startCamera(){

        if(!video){
            console.log("Video element not found")
            return
        }

        navigator.mediaDevices.getUserMedia({video:true})

        .then(s=>{
            stream=s
            video.srcObject=stream
        })

        .catch(err=>{
            console.log(err)
        })
    }

    function stopCamera(){

        if(stream){
            stream.getTracks().forEach(track => track.stop())
        }

    }

    // ================= CAPTURE FACE =================
    window.captureFace = function(){

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
    let roleSelect = document.getElementById("role")

    if(roleSelect){

        roleSelect.addEventListener("change",function(){

            let role=this.value

            document.getElementById("studentFields").style.display=role==="student"?"block":"none"
            document.getElementById("facultyFields").style.display=role==="faculty"?"block":"none"
            document.getElementById("adminFields").style.display=role==="admin"?"block":"none"

        })

    }

})

