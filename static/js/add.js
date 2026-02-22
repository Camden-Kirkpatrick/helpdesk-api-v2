const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    // Get the form data
    const title = form.title.value.trim();
    const description = form.description.value.trim();
    const raw_priority = form.priority.value.trim();

    // Validate the form data
    if (title === "")
    {
        alert("title is required");
        return;
    }

    if (description === "")
    {
        alert("description is required");
        return;
    }

    const priority = validate_priority(raw_priority);
    if (priority === null) return;

    // Create the payload if the form data is valid
   const payload = {title, description, priority};

    try
    {
        // Make the API request
        const created = await requestOrThrow("/api/tickets/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        alert(`Ticket id=${created.id} created`);
        // View the ticket the user just created
        // window.location.href = "/api/tickets/" + created.id;
        window.location.href = "/static/tickets.html";
    }
    // Print the error if the request failed
    catch (err)
    {
        alert(err.message);
    }
});
