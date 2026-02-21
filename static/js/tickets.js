async function load_tickets()
{
    const status = document.getElementById("status");
    const output = document.getElementById("output");

    console.log("origin:", window.location.origin);
    console.log("token:", get_token());

    try
    {
        const data = await requestOrThrow("/api/tickets/", {method: "GET"});

        output.textContent = JSON.stringify(data, null, 2);
    }
    catch (err)
    {
        status.textContent = err?.message || "failed to load tickets";
    }
}

window.addEventListener("load", () => {
    load_tickets();
})