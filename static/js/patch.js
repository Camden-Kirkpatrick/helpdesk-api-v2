const form = document.getElementById("form");

form.addEventListener("submit", async event => {
    event.preventDefault(); // prevent form from reloading

    const ticket_id = document.getElementById("ticket_id").value;

    console.log(ticket_id);
    
    const payload = {};

    if (form.title.value.trim() !== "")
    {
        payload.title = form.title.value;
    }

    if (form.description.value.trim() !== "")
    {
        payload.description = form.description.value;
    }

    if (form.priority.value !== "")
    {
        payload.priority = Number(form.priority.value);
    } 

    if (form.ticket_status.value !== "")
    {
        payload.status = form.ticket_status.value;
    }

    // If the user didn't enter any form data
    if (Object.keys(payload).length === 0)
    {
        alert("Enter at least one field to update");
        return;
    }

    const exists = await fetch(`/api/tickets/${ticket_id}`, {method: "GET"});
    
    if (!exists.ok)
    {
        alert(`Error: Ticket with ticket_id=${ticket_id} not found`);
        return;
    }

    fetch(`/api/tickets/${ticket_id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(async res => {
        const data = await res.json();

        if (!res.ok)
        {
            const errors = data.detail || [];
            let messages = "";

            for (const e of errors)
            {
                messages += e.msg + "\n";
            }

            alert(messages || "Request failed");
            return;
        }
        
        window.location.href = "/api/tickets/" + ticket_id;
    })
});