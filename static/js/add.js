const form = document.getElementById("form");

form.addEventListener("submit", async (event) =>
{
    event.preventDefault();

    const title = form.title.value.trim();
    const description = form.description.value.trim();
    const rawPriority = form.priority.value.trim();

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

    const priority = Number(rawPriority);

    if (!Number.isInteger(priority) || priority < 1 || priority > 5)
    {
        alert("priority must be an integer between 1 and 5");
        return;
    }

    try
    {
        const fd = new FormData(form);

        const created = await requestOrThrow("/api/tickets/", {
            method: "POST",
            body: fd
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
