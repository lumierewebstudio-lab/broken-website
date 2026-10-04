from pathlib import Path
import json
import secrets
from datetime import datetime, timezone
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOADS_DIR = BASE_DIR / "uploads"

ENQUIRIES_FILE = (
    UPLOADS_DIR / "enquiries.json"
)

PROJECTS_FILE = (
    UPLOADS_DIR / "projects.json"
)

ENV_FILE = BASE_DIR / ".env"


UPLOADS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


load_dotenv(
    ENV_FILE
)


ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    ""
)


app = FastAPI(
    title="ƁƦƠҠЄƝ",
    description="ƁƦƠҠЄƝ — Digital Experiences",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        )
    ),
    name="static",
)


class ContactEnquiry(BaseModel):

    name: str

    email: str

    project: str = ""

    budget: str = ""

    message: str


class AdminLogin(BaseModel):

    password: str


class ProjectCreate(BaseModel):

    title: str

    category: str = ""

    description: str = ""

    link: str = ""


def admin_cookie_is_valid(
    request: Request
) -> bool:

    token = request.cookies.get(
        "broken_admin"
    )

    expected = os.getenv(
        "ADMIN_PASSWORD",
        ""
    )

    if not token or not expected:

        return False

    return secrets.compare_digest(
        token,
        expected
    )


def load_projects():

    if not PROJECTS_FILE.exists():

        return []


    try:

        with PROJECTS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            projects = json.load(
                file
            )


        if not isinstance(
            projects,
            list
        ):

            return []


        return projects


    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_projects(
    projects
):

    try:

        with PROJECTS_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                projects,
                file,
                indent=2,
                ensure_ascii=False
            )

    except OSError:

        raise HTTPException(
            status_code=500,
            detail="Unable to save projects."
        )


@app.get("/")
async def home():

    return FileResponse(
        BASE_DIR / "index.html"
    )


@app.get("/admin")
async def admin():

    return FileResponse(
        BASE_DIR / "admin.html"
    )


@app.get("/admin-login")
async def admin_login_page():

    return FileResponse(
        BASE_DIR / "admin-login.html"
    )


@app.get("/pages/{page_name}.html")
async def public_page(
    page_name: str
):

    allowed_pages = {
        "work",
        "about",
        "process",
        "contact",
        "project",
        "pivo",
    }

    if page_name not in allowed_pages:

        raise HTTPException(
            status_code=404,
            detail="Page not found"
        )


    page_file = (
        BASE_DIR
        / "pages"
        / f"{page_name}.html"
    )


    if not page_file.exists():

        raise HTTPException(
            status_code=404,
            detail="Page not found"
        )


    return FileResponse(
        page_file
    )


@app.post("/api/contact")
async def submit_contact(
    enquiry: ContactEnquiry
):

    name = enquiry.name.strip()

    email = enquiry.email.strip()

    message = enquiry.message.strip()


    if not name:

        raise HTTPException(
            status_code=400,
            detail="Name is required."
        )


    if not email:

        raise HTTPException(
            status_code=400,
            detail="Email is required."
        )


    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message is required."
        )


    try:

        existing = []


        if ENQUIRIES_FILE.exists():

            with ENQUIRIES_FILE.open(
                "r",
                encoding="utf-8"
            ) as file:

                existing = json.load(
                    file
                )


                if not isinstance(
                    existing,
                    list
                ):

                    existing = []


    except (
        json.JSONDecodeError,
        OSError
    ):

        existing = []


    enquiry_record = {

        "id":
            len(existing) + 1,

        "name":
            name,

        "email":
            email,

        "project":
            enquiry.project.strip(),

        "budget":
            enquiry.budget.strip(),

        "message":
            message,

        "submitted_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

    }


    existing.append(
        enquiry_record
    )


    try:

        with ENQUIRIES_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                existing,
                file,
                indent=2,
                ensure_ascii=False
            )


    except OSError:

        raise HTTPException(
            status_code=500,
            detail="Unable to save enquiry."
        )


    return {

        "success": True,

        "message":
            "Your enquiry has been received."

    }


@app.post("/api/admin/login")
async def admin_login(
    login: AdminLogin
):

    if not ADMIN_PASSWORD:

        raise HTTPException(
            status_code=500,
            detail="Admin password is not configured."
        )


    if not secrets.compare_digest(
        login.password,
        ADMIN_PASSWORD
    ):

        raise HTTPException(
            status_code=401,
            detail="Incorrect password."
        )


    response = JSONResponse(
        {
            "success": True
        }
    )


    response.set_cookie(
        key="broken_admin",
        value=ADMIN_PASSWORD,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 8
    )


    return response


@app.post("/api/admin/logout")
async def admin_logout():

    response = JSONResponse(
        {
            "success": True
        }
    )


    response.delete_cookie(
        "broken_admin"
    )


    return response


@app.get("/api/admin/enquiries")
async def get_enquiries(
    request: Request
):

    if not admin_cookie_is_valid(
        request
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )


    if not ENQUIRIES_FILE.exists():

        return []


    try:

        with ENQUIRIES_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            enquiries = json.load(
                file
            )


        if not isinstance(
            enquiries,
            list
        ):

            return []


        return enquiries


    except (
        json.JSONDecodeError,
        OSError
    ):

        raise HTTPException(
            status_code=500,
            detail="Unable to read enquiries."
        )


@app.get("/api/admin/projects")
async def get_admin_projects(
    request: Request
):

    if not admin_cookie_is_valid(
        request
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )


    return load_projects()


@app.post("/api/admin/projects")
async def add_project(
    request: Request,
    project: ProjectCreate
):

    if not admin_cookie_is_valid(
        request
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )


    title = project.title.strip()

    category = project.category.strip()

    description = project.description.strip()

    link = project.link.strip()


    if not title:

        raise HTTPException(
            status_code=400,
            detail="Project title is required."
        )


    projects = load_projects()


    next_id = 1


    if projects:

        ids = [
            item.get("id", 0)
            for item in projects
            if isinstance(
                item.get("id", 0),
                int
            )
        ]

        if ids:

            next_id = max(ids) + 1


    project_record = {

        "id":
            next_id,

        "title":
            title,

        "category":
            category,

        "description":
            description,

        "link":
            link,

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

    }


    projects.append(
        project_record
    )


    save_projects(
        projects
    )


    return {
        "success": True,
        "project":
            project_record
    }


@app.delete(
    "/api/admin/projects/{project_id}"
)
async def delete_project(
    project_id: int,
    request: Request
):

    if not admin_cookie_is_valid(
        request
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )


    projects = load_projects()


    remaining = [

        project

        for project in projects

        if project.get("id")
        != project_id

    ]


    if len(remaining) == len(
        projects
    ):

        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )


    save_projects(
        remaining
    )


    return {

        "success": True,

        "message":
            "Project deleted."

    }
