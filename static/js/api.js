async function safeJson(res)
{
    try
    {
        return await res.json();
    }
    catch
    {
        return null;
    }
}

function extractErrorMessage(data)
{
    if (!data || data.detail == null)
        return "";

    const detail = data.detail;

    if (Array.isArray(detail))

        return detail.map(e => e.msg).join("\n");

    if (typeof detail === "string")
        return detail;

    return "";
}

async function requestOrThrow(url, options)
{
    const res = await fetch(url, options);
    const data = await safeJson(res);

    if (!res.ok)
    {
        const msg = extractErrorMessage(data);
        throw new Error(msg || `Request failed (${res.status})`);
    }
}

function valid_ticket_id()
{
    const raw = document.getElementById("ticket_id").value.trim();

    if (raw === "")
    {
        alert("ticket_id is required");
        return null;
    }

    const ticket_id = Number(raw);

    if (!Number.isInteger(ticket_id) || ticket_id <= 0)
    {
        alert("ticket_id must be a positive integer");
        return null;
    }

    return ticket_id;
}
