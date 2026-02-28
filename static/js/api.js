// This is the key for the token
const TOKEN_KEY = "access_token";

// Functions dealing with the access_token
function set_token(token)
{
    sessionStorage.setItem(TOKEN_KEY, token);
}

function get_token()
{
    return sessionStorage.getItem(TOKEN_KEY);
}

function logout()
{
    sessionStorage.removeItem(TOKEN_KEY);
    window.location.reload();
}



// Parses the response body as JSON and returns a JS object
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

// Return the error message from the response
function extract_error_message(data)
{
     // No FastAPI error info
    if (!data || data.detail == null) return "";

    // Pydantic validation errors (detail is an array)
    if (Array.isArray(data.detail))
        return data.detail.map(e => e.msg).join(", ");

    // Custom FastAPI errors (detail is a string)
    return String(data.detail);
}

// Send a request to the API
async function requestOrThrow(url, options = {})
{
    const headers = new Headers(options.headers || {});
    const token = get_token();

    // Check to see if we need to set authorization using the token
    if (token && !url.startsWith("/auth"))
    {
        headers.set("Authorization", `Bearer ${token}`);
    }

    options.headers = headers

    // API request
    const res = await fetch(url, options);
    // JavaScript object returned from request
    const data = await safeJson(res);

    // Ensure that the response is ok
    if (!res.ok)
    {
        const msg = extract_error_message(data);
        throw new Error(msg || `Request failed (${res.status})`);
    }

    return data
}


// Ensure that the ticket_id the user entered is valid
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


// Ensure that the priority the user entered is valid
function validate_priority(raw_priority)
{
    const priority = Number(raw_priority);

    if (!Number.isInteger(priority) || priority < 1 || priority > 5)
    {
        alert("priority must be an integer between 1 and 5");
        return null;
    }

    return priority;
}

// Ensure that the status the user selected is valid
function valid_status(status)
{
    const allowed_statuses = ["in_progress", "open", "closed"]

    if (!allowed_statuses.includes(status))
    {
        alert("Status must be: open, in progress, or closed.");
        return null
    }

    return status;
}


// Toggle to view or hide the password entered by the user
const password_button = document.getElementById("view_pass");
if (password_button != null)
{
    password_button.addEventListener("click", () => {
        const pass_input = document.getElementById("password");

        if (pass_input.type === "password")
            pass_input.type = "text";
        else
            pass_input.type = "password";
    });
}



// Logged in message in the top right of the webpage
async function update_auth_ui()
{
    const user_el = document.getElementById("nav-user");
    const logout_el = document.getElementById("nav-logout");

    const login_el = document.querySelector("a.login-btn");
    const register_el = document.querySelector("a.register-btn");

    // Ensure all elements exist
    if (!user_el || !logout_el || !login_el || !register_el)
        return;

    // Succeeds if the user is logged in
    try
    {
        const me = await requestOrThrow("/user", {method: "GET"});

        user_el.style.display = "inline";
        user_el.textContent =  `Logged in as: ${me.username}`;

        logout_el.style.display = "inline";

        login_el.style.display = "none";
        register_el.style.display = "none";
    }
    // The user is not logged in
    catch
    {
        user_el.style.display = "none";
        logout_el.style.display = "none";

        login_el.style.display = "inline";
        register_el.style.display = "inline";
    }

    logout_el.onclick = (e) => {
        e.preventDefault();
        logout();
    };
}