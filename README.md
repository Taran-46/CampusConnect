# 🎓 CampusConnect — Campus Issue Reporting & Tracking Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Native%20Driver-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Vanilla Web](https://img.shields.io/badge/Frontend-Vanilla%20HTML5%20%7C%20CSS3%20%7C%20ES6+-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A clean, production-ready, full-stack web application designed for college students to report, track, and resolve common facilities and campus issues collaboratively. Built with high readability, modular architecture, zero bloated dependencies, and production-grade security.

---

## 📌 Table of Contents
1. [Project Overview & Key Features](#-project-overview--key-features)
2. [Technology Stack](#-technology-stack)
3. [Repository File Structure](#-repository-file-structure)
4. [Step-by-Step Setup & Execution](#-step-by-step-setup--execution)
   - [Backend Setup (FastAPI & SQLite)](#1-backend-setup)
   - [Frontend Setup](#2-frontend-setup)
5. [API Documentation & Endpoints](#-api-documentation--endpoints)
6. [Security & Validation Standards](#-security--validation-standards)
7. [GitHub Team Collaboration Workflow](#-github-team-collaboration-workflow)
   - [Branching Strategy](#branching-strategy)
   - [Pull Request (PR) Guidelines & Review Rules](#pull-request-pr-guidelines--review-rules)
   - [Commit Message Conventions](#commit-message-conventions)
8. [Team Member Roles & Responsibilities](#-team-member-roles--responsibilities)

---

## 🚀 Project Overview & Key Features

Campus life often encounters unresolved friction: flickering classroom projectors, broken water coolers, spotty Wi-Fi in the library, or misplaced notebooks. **CampusConnect** provides a transparent, centralized board where students can report and track real-time issue statuses across four pre-populated categories:

* 🏫 **Classroom**: Projector problems, broken fans, lighting faults, lab PC issues.
* 🌿 **Campus**: Cleanliness, water cooler leaks, washroom sanitation, campus Wi-Fi.
* 🔍 **Lost & Found**: Lost ID cards, misplaced water bottles, found notebooks.
* 📌 **General**: Library access, sports equipment, hostel queries, general administration.

### Core Features:
- **Student Authentication**: Secure sign up with Department & Year, hashed passwords, and JWT session handling.
- **Dynamic Issue Lifecycle**: Auto-assigned `Open` status on submission, with transitions to `In Progress` and `Resolved`.
- **Real-Time Issue Filtering**: Search issues by keywords, filter dynamically by Category or Status.
- **Comprehensive Issue Detail**: View complete description, submitter name, department, timestamps, and interactive status updater.
- **Personalized Profile View**: Displays student info and an archive of all issues submitted by that student.
- **Zero Frontend Tooling Overhead**: Built entirely with pure Vanilla HTML5, CSS3, and modern ES6+ JavaScript—no bundlers, Webpack, or Node.js required.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ & FastAPI | Async REST API, Pydantic v2 data validation, CORS middleware |
| **Authentication** | JWT & Bcrypt | JSON Web Tokens (`PyJWT` / `python-jose`), Bcrypt password hashing |
| **Database** | SQLite3 | Native Python `sqlite3` driver with parameterized queries & WAL mode |
| **Server** | Uvicorn | High-performance ASGI web server |
| **Frontend** | Vanilla HTML5, CSS3, JS (ES6+) | Semantic HTML, CSS variables, Fetch API, XSS-safe DOM rendering |

---

## 📁 Repository File Structure

```text
CampusConnect/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py           # Application package initializer
│   │   ├── main.py               # FastAPI server entry point, CORS & REST endpoints
│   │   ├── database.py           # Native SQLite connection manager & table init
│   │   ├── models.py             # Pydantic validation schemas (requests & responses)
│   │   └── auth.py               # Password hashing (bcrypt) & JWT auth dependencies
│   └── requirements.txt          # Backend dependencies
│
├── frontend/
│   ├── css/
│   │   └── style.css             # Unified modern CSS system with responsive design
│   ├── js/
│   │   ├── api.js                # Fetch API wrapper with auth headers & error toasts
│   │   ├── auth.js               # Sign in / Register state & session management
│   │   ├── dashboard.js          # Metrics counters & issue card rendering
│   │   └── create_issue.js       # Issue submission validation & handler
│   ├── index.html                # Sign In / Register toggle portal
│   ├── dashboard.html            # Campus issues board with filters & metric summary
│   ├── create-issue.html         # Form to submit a new campus issue
│   ├── issue-detail.html         # Single issue view & status update workflow
│   └── profile.html              # Student profile & authored issues view
│
├── README.md                     # Comprehensive project documentation
└── .gitignore                    # Git ignore file for Python, caches, & databases
```

---

## 💻 Step-by-Step Setup & Execution

### 1. Backend Setup

Ensure you have **Python 3.10 or higher** installed on your system.

```bash
# 1. Navigate to the backend directory
cd CampusConnect/backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On macOS / Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> **Note**: On server startup, `database.py` automatically initializes `campus_connect.db` with all tables, indexes, and demo sample data. No manual SQL scripts are required!

Interactive API documentation will be available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 2. Frontend Setup

Because the frontend is built using standard Vanilla HTML, CSS, and JavaScript, **no build tools or Node.js are needed**.

You can run the frontend in any of the following convenient ways:

#### Option A: Served directly by FastAPI (Easiest)
With the backend running, open your web browser and visit:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

#### Option B: VS Code Live Server
1. Open the `CampusConnect/frontend` folder in VS Code.
2. Right-click `index.html` and select **"Open with Live Server"**.

#### Option C: Python Simple HTTP Server
```bash
cd CampusConnect/frontend
python -m http.server 3000
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

### 🔑 Demo Account Credentials
If you'd like to test the application immediately without registering:
- **Email**: `aarav.sharma@campus.edu`
- **Password**: `password123`

---

## 📡 API Documentation & Endpoints

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/register` | No | Register a new student account (`full_name`, `email`, `password`, `department`) |
| `POST` | `/api/login` | No | Authenticate student credentials and receive JWT access token |
| `GET` | `/api/me` | Yes | Get the current authenticated student's profile information |
| `GET` | `/api/issues` | No | List all issues (supports `?category=`, `?status=`, `?search=`, `?user_id=`) |
| `POST` | `/api/issues` | Yes | Submit a new issue (`title`, `description`, `category`) |
| `GET` | `/api/issues/{id}` | No | Retrieve single issue details with submitter information |
| `PATCH` | `/api/issues/{id}/status` | Yes | Update issue status (`Open`, `In Progress`, `Resolved`) |

---

## 🛡️ Security & Validation Standards

1. **SQL Injection Prevention**: All queries in `database.py` and `main.py` utilize parameterized SQL placeholders (`?`), preventing SQL injection attacks.
2. **Cross-Site Scripting (XSS) Mitigation**: Dynamic user-generated text is rendered into the DOM using `textContent` and strict character escaping (`escapeHTML()`).
3. **Password Security**: Passwords are never stored in plain text. They are hashed using `bcrypt` with automatic salting before persistence.
4. **JWT Session Protection**: All state-modifying requests require a valid Bearer token validated by FastAPI dependencies.
5. **CORS Hardening**: FastAPI `CORSMiddleware` is configured to allow development origins while guarding headers.

---

## 🤝 GitHub Team Collaboration Workflow

To ensure smooth collaboration across the development team, all members follow this Git workflow.

### Branching Strategy
Never commit directly to `main`. All work must be conducted on dedicated feature branches branched off `main`:

```text
main (production-ready code)
  │
  ├── feature/auth-jwt          (Student login & registration)
  ├── feature/issue-dashboard   (Issue filtering & cards)
  ├── feature/issue-detail      (Status update workflow)
  ├── feature/user-profile      (Profile page & submissions)
  └── bugfix/cors-handling      (Targeted bug fixes)
```

#### Branch Naming Guidelines:
- `feature/<short-description>`: For new features (e.g., `feature/login`, `feature/issue-form`)
- `bugfix/<short-description>`: For bug fixes (e.g., `bugfix/token-expiry`)
- `docs/<short-description>`: For documentation updates (e.g., `docs/api-guide`)

```bash
# Example: Creating and switching to a new feature branch
git checkout -b feature/issue-form
git push -u origin feature/issue-form
```

---

### Pull Request (PR) Guidelines & Review Rules

1. **Self-Review Checklist Before Opening PR**:
   - [ ] Backend starts without errors (`uvicorn app.main:app --reload`).
   - [ ] No temporary debug code or `console.log()` statements left behind.
   - [ ] No hardcoded database credentials or personal secrets.
   - [ ] Frontend responsive layout tested on both desktop and mobile viewports.
2. **PR Description**: Include a summary of changes, screenshots of UI updates (if applicable), and steps to test.
3. **Peer Review Requirement**: Every PR requires at least **one approved review** from another team member before merging.
4. **Merge Method**: Use **"Squash and merge"** or **"Rebase and merge"** to maintain a clean linear commit history on `main`.

---

### Commit Message Conventions
We follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```text
<type>(<scope>): <short description>
```

- `feat`: A new feature (e.g., `feat(auth): implement JWT token verification`)
- `fix`: A bug fix (e.g., `fix(database): enforce foreign keys on connection`)
- `style`: UI styling or formatting changes (e.g., `style(css): update status badge colors`)
- `docs`: Documentation updates (e.g., `docs(readme): add setup instructions for windows`)
- `refactor`: Code reorganization without functional changes (e.g., `refactor(api): modularize fetch helpers`)

---

## 👥 Team Member Roles & Responsibilities

| Name | Role | Primary Responsibilities |
| :--- | :--- | :--- |
| **Team Lead / Architect** | Full-Stack Lead | Architecture design, code review enforcement, deployment coordination |
| **Backend Developer** | Backend Specialist | FastAPI routes, database schema, SQLite queries, JWT authentication |
| **Frontend Developer 1** | UI / UX Specialist | HTML templates, CSS design system, responsive layouts, accessibility |
| **Frontend Developer 2** | Client Logic Specialist | Vanilla JS API integration, form validation, DOM manipulation, state handling |
| **QA & Documentation** | Quality Assurance | End-to-end testing, error handling verification, API documentation & README |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
