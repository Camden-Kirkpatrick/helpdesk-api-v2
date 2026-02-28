const form = document.getElementById("form");

form.addEventListener("submit", async event => {
    event.preventDefault();

    // Check to see if the ticket_id valid
    const ticket_id = valid_ticket_id();
    if (!ticket_id)
        return;

    try
    {
        // Make the API request
       const deleted =  await requestOrThrow(`/api/tickets/${ticket_id}`, {
            method: "DELETE"
        });

        // Success
        alert(`Ticket id=${deleted.id} deleted`);
        window.location.href = "/static/tickets.html";
    }
    // Print the error if the request failed
    catch (err)
    {
        console.error(err);
        alert(err?.message || "Unexpected error");
    }
});