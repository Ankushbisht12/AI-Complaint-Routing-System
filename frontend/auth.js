loginBtn.addEventListener("click", async function () {

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8001/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                username: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", data.access_token);
            window.location.href = "dashboard.html";
        } else {
            alert(data.detail || "Login failed");
        }

    } catch (error) {
        alert("Server error. Make sure backend is running.");
    }
});