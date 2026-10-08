import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import get_db, init_db
from app.models import (
    IssueCategory,
    IssueCreate,
    IssueResponse,
    IssueStatus,
    IssueStatusUpdate,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

# Paths for frontend static files
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database tables and sample data on server startup.
    """
    try:
        init_db()
    except Exception as exc:
        print(f"[CampusConnect Startup Error] Failed to initialize database: {exc}")
    yield


app = FastAPI(
    title="CampusConnect API",
    description="Full-stack campus issue reporting and tracking platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS Middleware for seamless local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def format_issue_row(row: sqlite3.Row) -> dict:
    """Transform an SQLite Row into a dictionary matching IssueResponse schema."""
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "category": row["category"],
        "status": row["status"],
        "user_id": row["user_id"],
        "submitted_by_name": row["submitted_by_name"] if "submitted_by_name" in row.keys() else None,
        "submitted_by_department": row["submitted_by_department"] if "submitted_by_department" in row.keys() else None,
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


def format_user_row(row: sqlite3.Row) -> dict:
    """Transform an SQLite Row into a dictionary matching UserResponse schema."""
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "department": row["department"],
        "created_at": str(row["created_at"]),
    }


# -------------------------------------------------------------
# Authentication Endpoints
# -------------------------------------------------------------
@app.post(
    "/api/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
def register_student(payload: UserRegister, conn: sqlite3.Connection = Depends(get_db)):
    """
    Register a new student user.
    Enforces unique email, hashes password with bcrypt, and returns an access token.
    """
    cursor = conn.cursor()

    # Check for existing user with this email
    cursor.execute("SELECT id FROM users WHERE email = ?;", (payload.email.lower(),))
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in instead.",
        )

    # Hash the password
    hashed_pwd = hash_password(payload.password)

    try:
        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash, department)
            VALUES (?, ?, ?, ?);
            """,
            (payload.full_name, payload.email.lower(), hashed_pwd, payload.department),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.Error as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during registration: {str(exc)}",
        ) from exc

    # Retrieve created user
    cursor.execute(
        "SELECT id, full_name, email, department, created_at FROM users WHERE id = ?;",
        (user_id,),
    )
    user_row = cursor.fetchone()
    user_dict = format_user_row(user_row)

    # Generate access token
    token = create_access_token({"sub": str(user_id), "email": user_dict["email"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_dict,
    }


@app.post(
    "/api/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate student and return token",
)
def login_student(payload: UserLogin, conn: sqlite3.Connection = Depends(get_db)):
    """
    Authenticate a student via email and password, returning an access token.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, full_name, email, password_hash, department, created_at FROM users WHERE email = ?;",
        (payload.email.lower(),),
    )
    user = cursor.fetchone()

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_dict = format_user_row(user)
    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_dict,
    }


@app.get(
    "/api/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get profile of currently authenticated student",
)
def get_current_user_profile(current_user: sqlite3.Row = Depends(get_current_user)):
    """
    Returns the user profile for the current bearer token holder.
    """
    return format_user_row(current_user)


# -------------------------------------------------------------
# Issue Management Endpoints
# -------------------------------------------------------------
@app.get(
    "/api/issues",
    response_model=List[IssueResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all issues with optional filtering",
)
def get_issues(
    category: Optional[str] = Query(None, description="Filter by category (Classroom, Campus, Lost & Found, General)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Open, In Progress, Resolved)"),
    user_id: Optional[int] = Query(None, description="Filter issues submitted by a specific student ID"),
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    conn: sqlite3.Connection = Depends(get_db),
):
    """
    Retrieve issues ordered by latest created, supporting category, status, and search filters.
    """
    query = """
        SELECT 
            i.id, i.title, i.description, i.category, i.status, i.user_id,
            i.created_at, i.updated_at,
            u.full_name AS submitted_by_name,
            u.department AS submitted_by_department
        FROM issues i
        JOIN users u ON i.user_id = u.id
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND i.category = ?"
        params.append(category)

    if status_filter:
        query += " AND i.status = ?"
        params.append(status_filter)

    if user_id:
        query += " AND i.user_id = ?"
        params.append(user_id)

    if search:
        search_term = f"%{search.strip()}%"
        query += " AND (i.title LIKE ? OR i.description LIKE ?)"
        params.extend([search_term, search_term])

    query += " ORDER BY i.created_at DESC;"

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    return [format_issue_row(row) for row in rows]


@app.post(
    "/api/issues",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new campus issue",
)
def create_issue(
    payload: IssueCreate,
    current_user: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """
    Create a new issue submitted by the authenticated student.
    Defaults status to 'Open'.
    """
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO issues (title, description, category, status, user_id)
            VALUES (?, ?, ?, 'Open', ?);
            """,
            (payload.title, payload.description, payload.category.value, current_user["id"]),
        )
        conn.commit()
        issue_id = cursor.lastrowid
    except sqlite3.Error as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating issue: {str(exc)}",
        ) from exc

    # Query the freshly created record with submitter details
    cursor.execute(
        """
        SELECT 
            i.id, i.title, i.description, i.category, i.status, i.user_id,
            i.created_at, i.updated_at,
            u.full_name AS submitted_by_name,
            u.department AS submitted_by_department
        FROM issues i
        JOIN users u ON i.user_id = u.id
        WHERE i.id = ?;
        """,
        (issue_id,),
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to retrieve created issue.")

    return format_issue_row(row)


@app.get(
    "/api/issues/{id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve single issue details",
)
def get_issue_by_id(id: int, conn: sqlite3.Connection = Depends(get_db)):
    """
    Retrieve full details for an issue by its ID.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            i.id, i.title, i.description, i.category, i.status, i.user_id,
            i.created_at, i.updated_at,
            u.full_name AS submitted_by_name,
            u.department AS submitted_by_department
        FROM issues i
        JOIN users u ON i.user_id = u.id
        WHERE i.id = ?;
        """,
        (id,),
    )
    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {id} was not found.",
        )

    return format_issue_row(row)


@app.patch(
    "/api/issues/{id}/status",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the status of an issue",
)
def update_issue_status(
    id: int,
    payload: IssueStatusUpdate,
    current_user: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """
    Update the status of an issue (Open -> In Progress -> Resolved).
    Any authenticated student can update the status.
    """
    cursor = conn.cursor()

    # Check if issue exists
    cursor.execute("SELECT id FROM issues WHERE id = ?;", (id,))
    if not cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot update: Issue with ID {id} does not exist.",
        )

    try:
        cursor.execute(
            """
            UPDATE issues
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """,
            (payload.status.value, id),
        )
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while updating issue status: {str(exc)}",
        ) from exc

    # Retrieve updated row
    cursor.execute(
        """
        SELECT 
            i.id, i.title, i.description, i.category, i.status, i.user_id,
            i.created_at, i.updated_at,
            u.full_name AS submitted_by_name,
            u.department AS submitted_by_department
        FROM issues i
        JOIN users u ON i.user_id = u.id
        WHERE i.id = ?;
        """,
        (id,),
    )
    row = cursor.fetchone()
    return format_issue_row(row)


# -------------------------------------------------------------
# Optional Static Frontend Serving from FastAPI
# -------------------------------------------------------------
if FRONTEND_DIR.exists() and FRONTEND_DIR.is_dir():
    # Mount frontend static files so opening http://localhost:8000 directly works seamlessly!
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "CampusConnect API is running."}

    @app.get("/{page_name}.html", include_in_schema=False)
    def serve_html_pages(page_name: str):
        target_file = FRONTEND_DIR / f"{page_name}.html"
        if target_file.exists():
            return FileResponse(str(target_file))
        raise HTTPException(status_code=404, detail="Page not found")
