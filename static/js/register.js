const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    // Get the form data
    const username = form.username.value.trim()
    const password = form.password.value.trim();

    // Validate the form data

    if (!username)
    {
        alert("username is required");
        return;
    }

    if (!password)
    {
        alert("password is required");
        return;
    }

    // Create the payload from the form data
    const payload = {username, password};

    try
    {
        // Make the API request
        const data = await requestOrThrow("/auth", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        // Success
        alert("Account created");
        window.location.href = "/static/login.html";
    }
    // Failure
    catch (err)
    {
        alert(err?.message || "Registration failed");
    }
});
