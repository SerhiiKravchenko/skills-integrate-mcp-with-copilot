# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity (requires login)                            |
| DELETE | `/activities/{activity_name}/unregister?email=...`                | Unregister a student from an activity (requires login)             |
| POST   | `/users/register`                                                 | Register a new student account                                      |
| POST   | `/users/login`                                                    | Authenticate and receive a bearer token                             |
| POST   | `/users/logout`                                                   | Log out the current session                                          |
| GET    | `/users/me`                                                       | Get the logged-in user's profile                                    |
| PUT    | `/users/{email}/status`                                           | Update a user's account status (admin only)                         |
| GET    | `/users`                                                          | List all users (admin only)                                         |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
