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

    const payload = {username, password};

    try
    {
        const data = await requestOrThrow("/auth", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        alert("Account created");

        window.location.href = "/static/login.html";
    }
    catch (err)
    {
        alert(err?.message || "Registration failed");
    }
});
