// Display the tickets from the API request
function render_tickets(tickets)
{
    const list = document.getElementById("tickets");
    list.innerHTML = "";

    // The user might not have any tickets
    if (!tickets || tickets.length === 0)
    {
        const li = document.createElement("li");
        li.textContent = "No tickets found"
        list.appendChild(li)
        return;
    }

    // Create a list of the user's tickets
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


// Make an API request to view all the users tickets
async function load_all_tickets()
{
    const statusEl = document.getElementById("status");

    try
    {
        // Make API request
        const tickets = await requestOrThrow("/api/tickets/", {method: "GET"});
        statusEl.textContent = "";
        render_tickets(tickets);
    }
    // Print the error if the request failed
    catch (err)
    {
        statusEl.textContent = err?.message || "Failed to load tickets";
    }
}


// Create the url with the search parameters from the form inputs
function build_search_url()
{
    // Get the data from all the input fields
    const title = document.getElementById("q-title").value.trim();
    const description = document.getElementById("q-desc").value.trim();
    const raw_priority = document.getElementById("q-priority").value.trim();
    const raw_status = document.getElementById("q-status").value.trim();
    const raw_limit = document.getElementById("q-limit").value.trim();
    const raw_offset = document.getElementById("q-offset").value.trim();

    const params = new URLSearchParams();

    // Add query parameters if the input fields are not empty
    // and validate the form data

    if (title) params.set("title", title);

    if (description) params.set("description", description);

    if (raw_priority)
    { 
        const priority = validate_priority(raw_priority);

        if (priority === null) return;
        params.set("priority", priority);
    }

    if (raw_status)
    {
        const status = valid_status(raw_status);
        if (status === null) return; 
        params.set("status", status);
    }

    if (raw_limit)
    {
        const limit = Number(raw_limit);

        if (!Number.isInteger(limit) || limit < 1 || limit > 100)
        {
            alert("the limit for number of tickets viewed must be an integer between 1 and 100")
            return;
        }

        params.set("limit", limit);
    }

    if (raw_offset)
    {
        const offset = Number(raw_offset);

        if (!Number.isInteger(offset) || offset < 0)
        {
            alert("the number of tickets offset by must be 0 or greater")
            return;
        }

        params.set("offset", offset);
    }

    const qs = params.toString();
    // Construct the url using the search parameters
    return "/api/tickets/search" + (qs ? `?${qs}` : "");
}


// Search for the ticket(s) using the form data as query parameters
async function search_tickets()
{
    const statusEl = document.getElementById("status");

    try
    {
        const url = build_search_url();
        if (!url) return;
        // Make API request
        const tickets = await requestOrThrow(url, {method: "GET"});

        // Success
        statusEl.textContent = "";
        render_tickets(tickets);
    }
    // Print the error if the request failed
    catch (err)
    {
        statusEl.textContent = err?.message || "Search failed"
    }
}


// Search for a ticket using its id
async function search_by_id(ticket_id)
{
    const statusEl = document.getElementById("status");
    const list = document.getElementById("tickets");
    list.textContent = "";

    try
    {
        // Make the API request
        const ticket = await requestOrThrow(`/api/tickets/${ticket_id}`, {method: "GET"});
        // Success
        statusEl.textContent = "";
        render_tickets([ticket]);
    }
    // Print the error if the request failed
    catch (err)
    {
        statusEl.textContent = err?.message || "Search failed";
    }
}



// Run this code once the entire page has finished loading
window.addEventListener("load", () => {
    load_all_tickets();

    // Search using query parameters
    document.getElementById("search-form").addEventListener("submit", (e) => {
        e.preventDefault();
        search_tickets();
    });

    // Search using the ticket's id
    document.getElementById("find-by-id").addEventListener("click", (e) => {
        e.preventDefault();
        const ticket_id = valid_ticket_id();
        if (!ticket_id) return;

        search_by_id(ticket_id);
    });

    // Clear all search inputs, reset the form fields, and reload all tickets
    document.getElementById("clear-btn").addEventListener("click", () => {
        document.getElementById("q-title").value =  "";
        document.getElementById("q-desc").value =  "";
        document.getElementById("q-priority").value =  "";
        document.getElementById("q-status").value =  "";
        document.getElementById("q-limit").value =  "";
        document.getElementById("q-offset").value =  "";
        document.getElementById("ticket_id").value = "";
        load_all_tickets();
    });
});