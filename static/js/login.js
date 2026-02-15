const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    const username = form.username.value.trim()
    const password = form.password.value

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
        const data = await requestOrThrow("/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
         
        alert(`Logged in as: ${payload.username}`);
        
        set_token(data.access_token);

        window.location.href = "/static/index.html";
    }
    catch (err)
    {
        alert(err?.message || "Login failed");
    }
});
