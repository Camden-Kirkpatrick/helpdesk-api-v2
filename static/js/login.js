const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    // Get the data from the form
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
        // Redirect the user to the home page
        window.location.href = "/static/index.html";
    }
    // Failure
    catch (err)
    {
        alert(err?.message || "Login failed");
    }
});
