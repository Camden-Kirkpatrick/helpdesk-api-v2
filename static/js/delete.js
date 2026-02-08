const form = document.getElementById("form");

form.addEventListener("submit", async event => {
    event.preventDefault(); // prevent form from reloading

    const ticket_id = document.getElementById("ticket_id").value;

    console.log(ticket_id);

    const exists = await fetch(`/api/tickets/${ticket_id}`, {method: "GET"});
    
    if (!exists.ok)
    {
        alert("Error: Ticket not found");
        return;
    }

    fetch(`/api/tickets/${ticket_id}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
    })
    .then(res => {
        if (res.ok) {console.log("PATCH request successful");}
        else {console.log("PATCH request failed");}
        return res.json();
    })
    .then(data => {
        console.log(data);
        window.location.href = "/api/tickets";
    });
});