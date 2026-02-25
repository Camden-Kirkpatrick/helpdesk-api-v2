const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    const title = form.title.value.trim();
    const description = form.description.value.trim();
    const raw_priority = form.priority.value.trim();
    const raw_status = form.ticket_status.value.trim();

    // ticket_id must be entered in order to update
    const ticket_id = valid_ticket_id();
    if (!ticket_id)
        return;

    const payload = {};

    // Get the data the user wants to update
    
    if (title)
        payload.title = title;

    
    if (description)
        payload.description = description;

    if (raw_priority)
    {
        const priority = validate_priority(raw_priority);
        if (priority === null) return;
        payload.priority = priority;
    }

    if (raw_status)
    {
        const status = valid_status(raw_status);
        if (status === null) return;
        payload.status = status;
    }

    // At least one field must be updated
    if (Object.keys(payload).length === 0)
    {
        alert("Enter at least one field to update");
        return;
    }

    try
    {
        // Make API request
       const updated = await requestOrThrow(`/api/tickets/${ticket_id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        // Success
        alert(`Ticket id=${updated.id} updated`);
        window.location.href = "/static/tickets.html";
    }
    // Failure
    catch (err)
    {
        console.error(err);
        alert(err?.message || "Unexpected error");
    }
});
