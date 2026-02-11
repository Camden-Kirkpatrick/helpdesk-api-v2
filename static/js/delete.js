const form = document.getElementById("form");

form.addEventListener("submit", async event => {
    event.preventDefault(); // prevent form from reloading

    const ticket_id = valid_ticket_id();
    if (!ticket_id)
        return;

    // ---------- Requests ----------
    try
    {
        // Update ticket
        await requestOrThrow(`/api/tickets/${ticket_id}`, {
            method: "DELETE"
        });

        window.location.href = "/api/tickets/";
    }
    catch (err)
    {
        console.error(err);
        alert(err?.message || "Unexpected error");
    }
});