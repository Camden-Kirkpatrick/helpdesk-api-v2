// This is the key for the token
const TOKEN_KEY = "access_token";

function set_token(token)
{
    sessionStorage.setItem(TOKEN_KEY, token);
}

function get_token()
{
    return sessionStorage.getItem(TOKEN_KEY);
}

function clear_token()
{
    sessionStorage.removeItem(TOKEN_KEY);
}

function logout()
{
    sessionStorage.removeItem("access_token");
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
function extractErrorMessage(data)
{
    if (!data || data.detail == null)
        return "";

    return data.detail;
}

// Send a request to the API
async function requestOrThrow(url, options = {})
{
    const headers = new Headers(options.headers || {});
    const token = get_token();
    const isAuthRoute = url.startsWith("/auth");

    // Check to see if we need to set authorization using the token
    if (token && !headers.has("Authorization") && !isAuthRoute)
    {
        headers.set("Authorization", `Bearer ${token}`);
    }

    options.headers = headers

    // API request
    const res = await fetch(url, options);
    // JavaScript object returned from request
    const data = await safeJson(res);

    // Ensure that the response is good
    if (!res.ok)
    {
        const msg = extractErrorMessage(data);
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

    try
    {
        const me = await requestOrThrow("/user", {method: "GET"});

        if (user_el)
        {
            user_el.style.display = "inline";
            user_el.textContent =  `Logged in as: ${me.username}`;
        }

        if (logout_el)
            logout_el.style.display = "inline";

        if (login_el)
            login_el.style.display = "none";

        if (register_el)
            register_el.style.display = "none";
    }

    catch
    {
        if (user_el) user_el.style.display = "none";
        if (logout_el) logout_el.style.display = "none";

        if (login_el) login_el.style.display = "inline";
        if (register_el) register_el.style.display = "inline";
    }

    if (logout_el)
    {
        logout_el.onclick = (e) => {
            e.preventDefault();
            logout();
        };
    }
}