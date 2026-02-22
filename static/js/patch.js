// patch.js

const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault(); // prevent form reload

    const ticket_id = valid_ticket_id();
    if (!ticket_id)
        return;

    const payload = {};

    if (form.title.value.trim() !== "")
    {
        payload.title = form.title.value.trim();
    }

    if (form.description.value.trim() !== "")
    {
        payload.description = form.description.value.trim();
    }

    const raw_priority = form.priority.value.trim();
    if (form.priority.value.trim() !== "")
    {
        const priority = validate_priority(raw_priority);
        if (priority === null) return;

        payload.priority = priority;
    }

    if (form.ticket_status.value !== "")
    {
        payload.status = form.ticket_status.value;
    }

    if (Object.keys(payload).length === 0)
    {
        alert("Enter at least one field to update");
        return;
    }

    // ---------- Requests ----------
    try
    {
        // Update ticket
       const updated = await requestOrThrow(`/api/tickets/${ticket_id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        // Success
        alert(`Ticket id=${updated.id} updated`);
        window.location.href = "/static/tickets.html";
    }
    catch (err)
    {
        console.error(err);
        alert(err?.message || "Unexpected error");
    }
});
