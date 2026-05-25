"""
High School Management System API

A super simple FastAPI application that allows students and staff to view,
sign up for, and manage extracurricular activities at Mergington High School.
"""

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from pathlib import Path
import hashlib
import json
import os
import secrets
from typing import Optional

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing, signing up, and managing extracurricular activities"
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(current_dir, "static")),
    name="static",
)

USERS_FILE = current_dir / "users.json"
session_tokens = {}

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StatusUpdate(BaseModel):
    status: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def save_users(users_data: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as handle:
        json.dump(users_data, handle, indent=2)


def load_users() -> dict:
    if not USERS_FILE.exists():
        save_users(
            {
                "users": [
                    {
                        "email": "admin@mergington.edu",
                        "name": "School Admin",
                        "role": "admin",
                        "status": "active",
                        "password": hash_password("adminpass"),
                    }
                ]
            }
        )
    with open(USERS_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def find_user(email: str) -> Optional[dict]:
    users = load_users()["users"]
    return next((user for user in users if user["email"] == email), None)


def authenticate_user(email: str, password: str) -> dict:
    user = find_user(email)
    if not user or user["password"] != hash_password(password):
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    if user["status"] != "active":
        raise HTTPException(
            status_code=403,
            detail="Your account is not active. Please wait for approval.",
        )
    return user


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authentication token")
    token = authorization.split(" ", 1)[1]
    email = session_tokens.get(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    user = find_user(email)
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user")
    return user


def require_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["status"] != "active":
        raise HTTPException(status_code=403, detail="Account is not active")
    return current_user


def require_admin(current_user: dict = Depends(require_active_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/users/register")
def register_user(request: UserCreate):
    users_data = load_users()
    if find_user(request.email):
        raise HTTPException(status_code=400, detail="A user with that email already exists")

    users_data["users"].append(
        {
            "email": request.email,
            "name": request.name,
            "role": "student",
            "status": "pending",
            "password": hash_password(request.password),
        }
    )
    save_users(users_data)
    return {
        "message": "Registration received. Please ask an admin to approve your account.",
        "status": "pending",
    }


@app.post("/users/login")
def login(request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    token = secrets.token_urlsafe(32)
    session_tokens[token] = user["email"]
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "status": user["status"],
        },
    }


@app.post("/users/logout")
def logout(current_user: dict = Depends(get_current_user), authorization: Optional[str] = Header(None)):
    token = authorization.split(" ", 1)[1]
    session_tokens.pop(token, None)
    return {"message": "Logged out successfully"}


@app.get("/users/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "email": current_user["email"],
        "name": current_user["name"],
        "role": current_user["role"],
        "status": current_user["status"],
    }


@app.get("/users")
def list_users(admin_user: dict = Depends(require_admin)):
    return load_users()["users"]


@app.put("/users/{email}/status")
def update_user_status(email: str, request: StatusUpdate, admin_user: dict = Depends(require_admin)):
    users_data = load_users()
    user = find_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.status not in {"pending", "active", "disabled"}:
        raise HTTPException(status_code=400, detail="Invalid status value")

    for stored_user in users_data["users"]:
        if stored_user["email"] == email:
            stored_user["status"] = request.status
            break

    save_users(users_data)
    return {"message": f"Updated status for {email} to {request.status}"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: EmailStr,
    current_user: dict = Depends(get_current_user),
):
    """Sign up a student for an activity"""
    if current_user["status"] != "active":
        raise HTTPException(status_code=403, detail="Only active users may sign up")

    if current_user["role"] == "student" and current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Students may only sign up themselves")

    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    email: EmailStr,
    current_user: dict = Depends(get_current_user),
):
    """Unregister a student from an activity"""
    if current_user["status"] != "active":
        raise HTTPException(status_code=403, detail="Only active users may unregister")

    if current_user["role"] == "student" and current_user["email"] != email:
        raise HTTPException(status_code=403, detail="Students may only unregister themselves")

    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
