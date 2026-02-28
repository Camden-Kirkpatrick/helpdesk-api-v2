# 🛠 Helpdesk API

A full-stack Helpdesk Ticket system built with **FastAPI**, **SQLModel**, **SQLite**, and **vanilla HTML/CSS/JavaScript**.

This project demonstrates:

- RESTful CRUD API design
- JWT-based authentication
- Dependency injection with FastAPI
- Secure per-user ownership enforcement
- Query filtering & pagination
- Clean frontend ↔ backend integration
- Automated testing with pytest

---

## 🚀 Features

### 🔐 Authentication (JWT)

- User registration with unique username enforcement
- Password hashing using `bcrypt`
- Login returns a signed JWT access token
- Token expiration support
- Protected routes require `Authorization: Bearer <token>`
- Signature + expiration validation
- Secure ticket ownership enforcement

---

### 🎫 Ticket Management (CRUD)

Authenticated users can:

- Create tickets
- View all their tickets
- Search tickets with query parameters
- Update tickets (partial PATCH)
- Delete tickets

All ticket queries enforce:

- Ticket must exist
- Ticket must belong to the authenticated user

---

### 🔎 Search & Pagination

Supports filtering by:

- `title` (partial match)
- `description` (partial match)
- `priority` (1–5)
- `status` (`open | in_progress | closed`)
- `offset`
- `limit` (max 100)

Example: /api/tickets/search?title=printer&priority=3&limit=5


---

### 🧠 Secure PATCH Handling

PATCH requests:

- Only update explicitly provided fields
- Ignore `null` values
- Reject empty update payloads

Prevents accidental overwriting of required database fields.

---

### 💾 Database Layer

- SQLite
- SQLModel ORM
- Dependency-injected sessions
- Automatic table creation on startup
- Unique constraint on usernames

---

### 🧪 Testing

Includes pytest tests covering:

- Ticket creation
- Ownership enforcement
- Update & delete behavior
- Authentication requirements

---

## 🏗 Tech Stack

**Backend**
- FastAPI
- SQLModel
- SQLite
- Passlib (bcrypt)
- python-jose (JWT)

**Frontend**
- HTML
- CSS
- Vanilla JavaScript
- `fetch()` API
- Session storage for JWT

**Testing**
- pytest
- TestClient

---

## 📦 Project Structure

```
helpdesk-api/
│
├── app/
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── auth.py
│   └── tickets.py
│
├── static/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── tickets.html
│   ├── add_ticket.html
│   ├── update_ticket.html
│   ├── delete_ticket.html
│   ├── login.html
│   └── register.html
│
├── tests/
│   ├── conftest.py
│   └── test_tickets.py
│
├── requirements.txt
├── .env
├── .gitignore
└── database.db
```


---

## 🔐 Authentication Flow

1. User registers → password hashed with bcrypt
2. User logs in → server returns JWT
3. JWT stored in `sessionStorage`
4. `fetch()` helper automatically attaches `Authorization` header
5. Backend dependency validates:
   - Token exists
   - Signature is valid
   - Token is not expired
   - Payload contains required claims

---

## 🧩 Frontend Architecture

- Centralized API helper (`requestOrThrow`)
- Automatic JWT header injection
- Centralized error extraction
- Form validation before API calls
- Redirect flow after successful operations
- Dynamic auth UI (shows logged-in user)

---

## ▶️ Running the Project

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd helpdesk-api
```

### 2️⃣ Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create `.env`

Create a `.env` file in the project root:

```env
SECRET_KEY=your_super_secret_key_here
```

⚠️ The app will not start without `SECRET_KEY`.

### 5️⃣ Run the server

```bash
uvicorn app.main:app --reload
```

Visit:

- http://127.0.0.1:8000/

OpenAPI docs:

- http://127.0.0.1:8000/docs

---

## Using the Web UI

1. Go to the home page:

       http://127.0.0.1:8000/

2. Register a user:

   - `/static/register.html`

3. Login:

   - `/static/login.html`

4. Create / view / search / update / delete tickets from the navbar links.

The frontend uses a shared request helper to:
- attach your JWT automatically to API requests
- extract FastAPI error messages cleanly

---

## Notes on Security & Correctness

- **Passwords** are stored only as bcrypt hashes (never plaintext).
- **JWT tokens** are signed and validated on every protected request.
- **Ticket ownership** is enforced in database queries (user_id must match).
- **PATCH updates** ignore `null` values and reject empty payloads to prevent accidental overwrites.

---

## Running Tests

    pytest

---

## License

Educational / portfolio project.