async function signup(event) {
    event.preventDefault();  // Prevent form from submitting normally

    let email = document.getElementById("email").value.trim();
    let password = document.getElementById("password").value.trim();
    let errorMessage = document.getElementById("error-message");
    let loader = document.getElementById("loader");

    // Clear previous messages
    errorMessage.textContent = "";
    errorMessage.classList.remove("success");
    errorMessage.classList.remove("error");

    // Input validation
    if (!email || !password) {
        errorMessage.textContent = "Please enter both email and password.";
        errorMessage.classList.add("error");
        return;
    }

    // Show loading spinner
    loader.style.display = "block";

    try {
        let response = await fetch("/auth/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        let data = await response.json();
        loader.style.display = "none";  // Hide loader after response

        if (response.ok) {
            errorMessage.textContent = data.message;
            errorMessage.classList.add("success");

            // Redirect to OTP verification after 2 seconds
            setTimeout(() => {
                window.location.href = "/verify_otp_page";
            }, 2000);
        } else {
            errorMessage.textContent = data.message || "Signup failed. Try again.";
            errorMessage.classList.add("error");
        }
    } catch (error) {
        loader.style.display = "none";
        errorMessage.textContent = "Network error. Please try again.";
        errorMessage.classList.add("error");
    }
}
