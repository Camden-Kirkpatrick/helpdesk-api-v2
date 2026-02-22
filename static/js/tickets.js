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
        li.innerHTML = `<strong>Ticket id=${t.id}</strong>
                        <ul>
                            <li>Title: ${t.title}</li>
                            <li>Description: ${t.description}</li>
                            <li>Priority: ${t.priority}</li>
                            <li>Status: ${t.status}</li>
                        </ul>`;
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
    const description = document.getElementById("q-desc").value.trim();
    const raw_priority = document.getElementById("q-priority").value.trim();
    const status = document.getElementById("q-status").value.trim();

    const params = new URLSearchParams();

    if (title) params.set("title", title);
    if (description) params.set("description", desrciption);

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



async function search_by_id(ticket_id)
{
    const statusEl = document.getElementById("status");
    statusEl.textContent = "Loading ticket...";

    const list = document.getElementById("tickets");
    list.textContent = "";

    try
    {
        const ticket = await requestOrThrow(`/api/tickets/${ticket_id}`, {method: "GET"});

        statusEl.textContent = "";

        render_tickets([ticket]);
    }
    catch (err)
    {
        statusEl.textContent = err?.message || "Search failed";
    }
}



window.addEventListener("load", () => {
    load_all_tickets();

    document.getElementById("search-form").addEventListener("submit", (e) => {
        e.preventDefault();
        search_tickets();
    });

    document.getElementById("find-by-id").addEventListener("click", (e) => {
        e.preventDefault();
        const ticket_id = valid_ticket_id();
        if (!ticket_id) return;

        search_by_id(ticket_id);
    });

    document.getElementById("clear-btn").addEventListener("click", () => {
        document.getElementById("q-title").value =  "";
        document.getElementById("q-desc").value =  "";
        document.getElementById("q-priority").value =  "";
        document.getElementById("q-status").value =  "";
        document.getElementById("ticket_id").value = "";
        load_all_tickets();
    });
});