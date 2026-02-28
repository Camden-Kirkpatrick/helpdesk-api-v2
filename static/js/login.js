const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    // Get the form data
    const username = form.username.value.trim()
    const password = form.password.value

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
    const payload = {username, password}

    try
    {
        // Make API request
        const data = await requestOrThrow("/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
         
        // Success
        alert(`Logged in as: ${payload.username}`);
        // Put the token in session storage
        set_token(data.access_token);
        window.location.href = "/static/index.html";
    }
    // Print the error if the request failed
    catch (err)
    {
        alert(err?.message || "Login failed");
    }
});
