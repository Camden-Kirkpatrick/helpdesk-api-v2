const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    const title = form.title.value.trim();
    const description = form.description.value.trim();
    const raw_priority = form.priority.value.trim();

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

   const payload = {title, description, priority}

    try
    {
        const created = await requestOrThrow("/api/tickets/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (created && created.id != null)
        {
            window.location.href = "/api/tickets/" + created.id;
            return;
        }

        window.location.href = "/api/tickets/";
    }
    catch (err)
    {
        alert(err?.message || "Unexpected error");
    }
});
