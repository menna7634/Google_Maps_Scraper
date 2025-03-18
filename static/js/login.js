async function login(event) {
    event.preventDefault(); 

    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();
    let errorMessage = document.getElementById("error-message");
    let loader = document.getElementById("loader");
    errorMessage.textContent = "";

    if (!email || !password) {
        errorMessage.textContent = "Please enter both email and password.";
        return;
    }

    loader.style.display = "block";

    try {
        let response = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",  
            body: JSON.stringify({ email, password })
        });

        let data = await response.json();
        loader.style.display = "none"; 

        if (response.ok) {
            window.location.href = data.redirect; 
        } else {
            errorMessage.textContent = data.message || "Login failed. Try again.";
        }
    } catch (error) {
        loader.style.display = "none";
        errorMessage.textContent = "Network error. Please try again.";
    }
}
