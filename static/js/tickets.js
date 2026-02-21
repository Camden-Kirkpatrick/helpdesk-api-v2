function render_tickets(tickets)
{
    const list = document.getElementById("tickets");
    list.innerHTML = "";

    if (!tickets || tickets.length === 0)
    {
        const li = document.createElement("li");
        li.textContent = "No tickets found"
        list.appendChild(li)
        return;
    }

    for (const t of tickets)
    {
        const li = document.createElement("li");
        li.innerHTML = `<strong>Ticket #${t.id}</strong> <ul><li>Title: ${t.title}</li> <li>Description: ${t.description}</li> <li>Priority: ${t.priority}</li> <li>Status: ${t.status}</li></ul>`;
        list.appendChild(li);
    }
}



async function load_all_tickets()
{
    const status = document.getElementById("status");

    try
    {
        const tickets = await requestOrThrow("/api/tickets/", {method: "GET"});
        status.textContent = "";
        render_tickets(tickets);
    }
    catch (err)
    {
        status.textContent = err?.message || "Failed to load tickets";
    }
}



function build_search_url()
{
    const title = document.getElementById("q-title").value.trim();
    const desciption = document.getElementById("q-desc").value.trim();
    const raw_priority = document.getElementById("q-priority").value.trim();
    const status = document.getElementById("q-status").value.trim();

    const params = new URLSearchParams();

    if (title) params.set("title", title);
    if (desciption) params.set("description", desciption);

    if (raw_priority !== "")
    {
        const priority = validate_priority(raw_priority);
        if (priority === null) return;

        params.set("priority", priority);
    }

    if (status) params.set("status", status);

    const qs = params.toString();
    return "/api/tickets/search" + (qs ? `?${qs}` : "");
}



async function search_tickets()
{
    const statusEl = document.getElementById("status");
    statusEl.textContent = "Searching...";

    try
    {
        const url = build_search_url();
        if (!url) return;
        const tickets = await requestOrThrow(url, {method: "GET"});

        statusEl.textContent = "";
        render_tickets(tickets);
    }
    catch (err)
    {
        statusEl.textContent = err?.message || "Search failed"
    }
}



window.addEventListener("load", () => {
    load_all_tickets();

    const form = document.getElementById("search-form");
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        search_tickets();
    });

    document.getElementById("clear-btn").addEventListener("click", () => {
        document.getElementById("q-title").value =  "";
        document.getElementById("q-desc").value =  "";
        document.getElementById("q-priority").value =  "";
        document.getElementById("q-status").value =  "";
        load_all_tickets();
    });
});