from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import hashlib
import os
from dotenv import load_dotenv

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "https://focuszone-backend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class RegisterUser(BaseModel):
    name: str
    email: str
    password: str


class LoginUser(BaseModel):
    email: str
    password: str

class FeedbackRequest(BaseModel):
    user_id: int
    message: str
class SaveApps(BaseModel):
    user_id: int
    apps: list[str]

class FocusStart(BaseModel):
    user_id: int
    duration_minutes: int = 30

class FocusSession(BaseModel):
    user_id: int
    duration_minutes: int = 30

class TaskCreate(BaseModel):
    task_name: str
    priority: str
    user_id: int


class LocationCreate(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    radius: int = 100
    user_id: int


class BlockedAppCreate(BaseModel):
    app_name: str
    user_id: int   

class AppSelection(BaseModel):
    user_id: int
    apps: list[str]


import os
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")


def get_connection():
    if os.getenv("RENDER"):
        ssl_ca = "/etc/secrets/ca.pem"
    else:
        ssl_ca = str(BASE_DIR / "ca.pem")

    return mysql.connector.connect(
        host=os.getenv("mysql-3bb599d1-alluvamsi99999-1b93.b.aivencloud.com"),
        user=os.getenv("avnadmin"),
        password=os.getenv("AVNS_1Gqe367vYoO6ahtuSIB"),
        database=os.getenv("defaultdb"),
        port=int(os.getenv("20954")),
        ssl_ca=ssl_ca
    )


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

@app.get("/logo.jpg")
def logo():
    return FileResponse(BASE_DIR / "logo.jpg")

@app.get("/")
def home():
     return FileResponse(BASE_DIR / "Login1Page.html")

@app.get("/create-account")
def create_account():
    return FileResponse(BASE_DIR / "CreateAccount.html")

@app.get("/home")
def home_page():
    return FileResponse(BASE_DIR / "Home2Page.html")

@app.get("/blocked")
def blocked_page():
    return FileResponse(BASE_DIR / "Blocked3apps.html")


@app.get("/location")
def location_page():
    return FileResponse(BASE_DIR / "Location4.html")


@app.get("/focus")
def focus_page():
    return FileResponse(BASE_DIR / "Focus5.html")


@app.get("/statistics")
def statistics_page():
    return FileResponse(BASE_DIR / "Statistics6.html")


@app.get("/settings")
def settings_page():
    return FileResponse(BASE_DIR / "Settings7.html")


@app.get("/tasks")
def tasks_page():
    return FileResponse(BASE_DIR / "Task8.html")



@app.post("/register")
def register(user: RegisterUser):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (user.email,)
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        password_hash = hash_password(user.password)

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (
                user.name,
                user.email,
                password_hash
            )
        )

        connection.commit()

        return {
            "message": "Account created successfully"
        }

    finally:
        cursor.close()
        connection.close()


@app.post("/login")
def login(user: LoginUser):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (user.email,)
        )

        db_user = cursor.fetchone()

        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        entered_hash = hash_password(user.password)

        if entered_hash != db_user["password_hash"]:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        cursor.execute(
            """
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (db_user["id"],)
        )

        connection.commit()

        return {
            "message": "Login successful",
            "user_id": db_user["id"],
            "name": db_user["name"],
            "email": db_user["email"]
        }

    finally:
        cursor.close()
        connection.close()



@app.post("/save-task")
def save_task(task: TaskCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO tasks
            (user_id, task_name, priority)
            VALUES (%s, %s, %s)
            """,
            (
                task.user_id,
                task.task_name,
                task.priority
            )
        )

        connection.commit()

        return {
            "message": "Task saved successfully"
        }

    finally:
        cursor.close()
        connection.close()

@app.get("/user-tasks/{user_id}")
def get_user_tasks(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                task_name,
                priority,
                completed,
                created_at
            FROM tasks
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        tasks = cursor.fetchall()

        return tasks

    finally:
        cursor.close()
        connection.close()

@app.post("/save-location")
def save_location(location: LocationCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO locations
            (
                user_id,
                location_name,
                latitude,
                longitude,
                radius
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                location.user_id,
                location.location_name,
                location.latitude,
                location.longitude,
                location.radius
            )
        )

        connection.commit()

        return {
            "message": "Location saved successfully"
        }

    finally:

        cursor.close()
        connection.close()

@app.get("/user-locations/{user_id}")
def get_user_locations(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
    """
    SELECT
        id,
        location_name,
        latitude,
        longitude,
        radius,
        created_at
    FROM locations
    WHERE user_id = %s
    ORDER BY created_at DESC
    """,
    (user_id,)
)

        locations = cursor.fetchall()

        return locations

    finally:
        cursor.close()
        connection.close()

@app.post("/save-blocked-app")
def save_blocked_app(app_data: BlockedAppCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO blocked_apps
            (user_id, app_name)
            VALUES (%s, %s)
            """,
            (
                app_data.user_id,
                app_data.app_name
            )
        )

        connection.commit()

        return {
            "message": "Blocked app saved successfully"
        }

    finally:
        cursor.close()
        connection.close()

@app.get("/user-blocked-apps/{user_id}")
def get_user_blocked_apps(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                id,
                app_name,
                is_blocked,
                created_at
            FROM blocked_apps
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        apps = cursor.fetchall()

        return apps

    finally:
        cursor.close()
        connection.close()

@app.get("/user-blocked-apps/{user_id}")
def get_blocked_apps(user_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT app_name
            FROM blocked_apps
            WHERE user_id = %s
            """,
            (user_id,)
        )

        apps = cursor.fetchall()

        return [
            {
                "app_name": app[0]
            }
            for app in apps
        ]

    finally:

        cursor.close()
        connection.close()

@app.delete("/delete-task/{task_id}")
def delete_task(task_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM tasks
            WHERE id = %s
            """,
            (task_id,)
        )
        
        

        connection.commit()

        return {
            "message": "Task deleted successfully"
        }

    finally:

        cursor.close()
        connection.close()

class TaskComplete(BaseModel):
    completed: bool


@app.put("/complete-task/{task_id}")
def complete_task(task_id: int, data: TaskComplete):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            UPDATE tasks
            SET completed = %s
            WHERE id = %s
            """,
            (
                1 if data.completed else 0,
                task_id
            )
        )

        connection.commit()

        return {
            "message": "Task status updated"
        }

    finally:

        cursor.close()
        connection.close()

@app.post("/focus-session")
def save_focus_session(session: FocusSession):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # =========================================
        # 1. SAVE COMPLETED FOCUS SESSION
        # =========================================

        cursor.execute(
            """
            INSERT INTO focus_sessions
            (
                user_id,
                start_time,
                end_time,
                duration_minutes,
                completed
            )
            VALUES
            (
                %s,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                %s,
                TRUE
            )
            """,
            (
                session.user_id,
                session.duration_minutes
            )
        )


        # =========================================
        # 2. GET USER'S CURRENT STREAK DATA
        # =========================================

        cursor.execute(
            """
            SELECT
                current_streak,
                last_streak_date
            FROM users
            WHERE id = %s
            """,
            (session.user_id,)
        )

        user = cursor.fetchone()


        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )


        current_streak = (
            user["current_streak"] or 0
        )

        last_streak_date = (
            user["last_streak_date"]
        )


        # =========================================
        # 3. GET TODAY'S DATE
        # =========================================

        today = datetime.now().date()


        # =========================================
        # 4. STREAK LOGIC
        # =========================================

        if last_streak_date is None:

            # First ever completed session
            new_streak = 1


        elif last_streak_date == today:

            # Already completed a session today
            # Do not increase again
            new_streak = current_streak


        elif last_streak_date == (
            today - timedelta(days=1)
        ):

            # Completed yesterday
            # Continue streak
            new_streak = current_streak + 1


        else:

            # Missed one or more days
            # Old streak ends
            new_streak = 1


        # =========================================
        # 5. UPDATE USER STREAK
        # =========================================

        cursor.execute(
            """
            UPDATE users
            SET
                current_streak = %s,
                last_streak_date = %s
            WHERE id = %s
            """,
            (
                new_streak,
                today,
                session.user_id
            )
        )


        # =========================================
        # 6. COMMIT EVERYTHING
        # =========================================

        connection.commit()


        return {
            "message": "Focus session saved successfully",
            "current_streak": new_streak
        }


    finally:

        cursor.close()
        connection.close()

@app.get("/focus-summary/{user_id}")
def focus_summary(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                COUNT(*) AS sessions,
                COALESCE(
                    SUM(duration_minutes),
                    0
                ) AS total_minutes
            FROM focus_sessions
            WHERE user_id = %s
            AND DATE(start_time) = CURDATE()
            AND completed = TRUE
            """,
            (user_id,)
        )

        result = cursor.fetchone()

        return result

    finally:

        cursor.close()
        connection.close()

@app.get("/focus-week/{user_id}")
def focus_week(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                DAYOFWEEK(start_time) AS day_number,
                COALESCE(SUM(duration_minutes), 0)
                AS total_minutes

            FROM focus_sessions

            WHERE user_id = %s
              AND completed = TRUE

              AND start_time >=
                  DATE_SUB(
                      CURDATE(),
                      INTERVAL (DAYOFWEEK(CURDATE()) - 1) DAY
                  )

              AND start_time <
                  DATE_ADD(
                      DATE_SUB(
                          CURDATE(),
                          INTERVAL (DAYOFWEEK(CURDATE()) - 1) DAY
                      ),
                      INTERVAL 7 DAY
                  )

            GROUP BY DAYOFWEEK(start_time)

            ORDER BY DAYOFWEEK(start_time)
            """,
            (user_id,)
        )

        rows = cursor.fetchall()


        week = {
            1: 0,  # Sun
            2: 0,  # Mon
            3: 0,  # Tue
            4: 0,  # Wed
            5: 0,  # Thu
            6: 0,  # Fri
            7: 0   # Sat
        }


        for row in rows:

            week[
                int(row["day_number"])
            ] = int(
                row["total_minutes"]
            )


        return {

            "days": [

                {
                    "day": "Sun",
                    "minutes": week[1]
                },

                {
                    "day": "Mon",
                    "minutes": week[2]
                },

                {
                    "day": "Tue",
                    "minutes": week[3]
                },

                {
                    "day": "Wed",
                    "minutes": week[4]
                },

                {
                    "day": "Thu",
                    "minutes": week[5]
                },

                {
                    "day": "Fri",
                    "minutes": week[6]
                },

                {
                    "day": "Sat",
                    "minutes": week[7]
                }

            ]

        }


    finally:

        cursor.close()
        connection.close()

@app.get("/user-location/{user_id}")
def get_user_location(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id,
                location_name,
                latitude,
                longitude,
                created_at
            FROM locations
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,)
        )

        location = cursor.fetchone()

        if not location:
            return {}

        return location

    finally:

        cursor.close()
        connection.close()



@app.post("/user-apps")
def save_apps(data: AppSelection):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Delete previous apps of this user
        cursor.execute(
            """
            DELETE FROM blocked_apps
            WHERE user_id = %s
            """,
            (data.user_id,)
        )


        # Insert latest selected apps
        for app in data.apps:

            cursor.execute(
                """
                INSERT INTO blocked_apps
                (user_id, app_name)
                VALUES (%s, %s)
                """,
                (
                    data.user_id,
                    app
                )
            )


        connection.commit()


        return {
            "message": "Blocked apps updated successfully"
        }


    finally:

        cursor.close()
        connection.close()
@app.get("/user-apps/{user_id}")
def get_user_apps(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT id, user_id, app_name
            FROM blocked_apps
            WHERE user_id = %s
            ORDER BY id ASC
            """,
            (user_id,)
        )

        apps = cursor.fetchall()

        # ALWAYS return an array
        return apps if apps else []

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        cursor.close()
        connection.close()

@app.get("/focus-streak/{user_id}")
def get_focus_streak(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT DISTINCT
                DATE(start_time) AS focus_date
            FROM focus_sessions
            WHERE user_id = %s
              AND completed = TRUE
            ORDER BY focus_date DESC
            """,
            (user_id,)
        )

        rows = cursor.fetchall()

        if not rows:
            return {
                "streak": 0
            }

        dates = [
            row["focus_date"]
            for row in rows
        ]

        streak = 0
        current_date = dates[0]

        for date in dates:

            if date == current_date:

                streak += 1
                current_date -= timedelta(days=1)

            else:

                break

        return {
            "streak": streak
        }

    finally:

        cursor.close()
        connection.close()

@app.post("/focus/start")
def start_focus(data: FocusStart):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # Check whether this user already has a running session
        cursor.execute(
            """
            SELECT id, start_time, duration_minutes
            FROM focus_sessions
            WHERE user_id = %s
              AND completed = FALSE
              AND end_time IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (data.user_id,)
        )

        existing = cursor.fetchone()

        if existing:
            return {
                "message": "Focus session already running",
                "session_id": existing["id"],
                "start_time": existing["start_time"].isoformat(),
                "duration_minutes": existing["duration_minutes"]
            }

        # Create new focus session
        cursor.execute(
            """
            INSERT INTO focus_sessions
            (
                user_id,
                start_time,
                end_time,
                duration_minutes,
                completed
            )
            VALUES (
                %s,
                NOW(),
                NULL,
                %s,
                FALSE
            )
            """,
            (
                data.user_id,
                data.duration_minutes
            )
        )

        connection.commit()

        session_id = cursor.lastrowid

        # Get exact database start time
        cursor.execute(
            """
            SELECT id, start_time, duration_minutes
            FROM focus_sessions
            WHERE id = %s
            """,
            (session_id,)
        )

        session = cursor.fetchone()

        return {
            "message": "Focus session started",
            "session_id": session["id"],
            "start_time": session["start_time"].isoformat(),
            "duration_minutes": session["duration_minutes"]
        }

    finally:

        cursor.close()
        connection.close()

@app.get("/focus/current/{user_id}")
def current_focus(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id,
                start_time,
                duration_minutes,
                completed
            FROM focus_sessions
            WHERE user_id = %s
              AND completed = FALSE
              AND end_time IS NULL
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        session = cursor.fetchone()

        if not session:

            return {
                "active": False
            }

        return {
            "active": True,
            "session_id": session["id"],
            "start_time": session["start_time"].isoformat(),
            "duration_minutes": session["duration_minutes"]
        }

    finally:

        cursor.close()
        connection.close()

@app.post("/focus/complete/{user_id}")
def complete_focus(user_id: int):

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # =====================================
        # 1. FIND CURRENT ACTIVE SESSION
        # =====================================

        cursor.execute(
            """
            SELECT id
            FROM focus_sessions
            WHERE user_id = %s
            AND completed = FALSE
            ORDER BY start_time DESC
            LIMIT 1
            """,
            (user_id,)
        )

        session = cursor.fetchone()


        if not session:

            raise HTTPException(
                status_code=404,
                detail="No active focus session found"
            )


        # =====================================
        # 2. COMPLETE FOCUS SESSION
        # =====================================

        cursor.execute(
            """
            UPDATE focus_sessions
            SET
                completed = TRUE,
                end_time = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (session["id"],)
        )


        # =====================================
        # 3. GET USER STREAK
        # =====================================

        cursor.execute(
            """
            SELECT
                current_streak,
                last_streak_date
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()


        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )


        current_streak = (
            user["current_streak"] or 0
        )

        last_streak_date = (
            user["last_streak_date"]
        )


        today = datetime.now().date()


        # =====================================
        # 4. STREAK LOGIC
        # =====================================

        if last_streak_date is None:

            # First completed session
            new_streak = 1


        elif last_streak_date == today:

            # Already completed session today
            new_streak = current_streak


        elif last_streak_date == (
            today - timedelta(days=1)
        ):

            # Completed yesterday
            new_streak = current_streak + 1


        else:

            # Missed one or more days
            new_streak = 1


        # =====================================
        # 5. UPDATE USER STREAK
        # =====================================

        cursor.execute(
            """
            UPDATE users
            SET
                current_streak = %s,
                last_streak_date = %s
            WHERE id = %s
            """,
            (
                new_streak,
                today,
                user_id
            )
        )


        connection.commit()


        return {
            "message":
                "Focus session completed successfully",

            "current_streak":
                new_streak
        }


    except HTTPException:

        connection.rollback()

        raise


    except Exception as error:

        connection.rollback()

        print(
            "Focus completion error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    finally:

        cursor.close()

        connection.close()

@app.post("/user-apps")
def save_apps(data: AppSelection):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Delete user's previous selection
        cursor.execute(
            """
            DELETE FROM blocked_apps
            WHERE user_id = %s
            """,
            (data.user_id,)
        )

        # Save latest selection
        for app in data.apps:

            cursor.execute(
                """
                INSERT INTO blocked_apps
                (user_id, app_name)
                VALUES (%s, %s)
                """,
                (data.user_id, app)
            )

        connection.commit()

        return {
            "message": "Blocked apps updated successfully"
        }

    finally:

        cursor.close()
        connection.close()   

@app.get("/focus-streak/{user_id}")
def get_focus_streak(user_id: int):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                current_streak,
                last_streak_date
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()


        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )


        current_streak = (
            user["current_streak"] or 0
        )

        last_streak_date = (
            user["last_streak_date"]
        )


        today = datetime.now().date()


        # If yesterday was missed,
        # streak should show as 0

        if (
            last_streak_date
            and last_streak_date
            < today - timedelta(days=1)
        ):

            current_streak = 0


        return {
            "streak": current_streak
        }


    finally:

        cursor.close()
        connection.close()

@app.post("/feedback")
def save_feedback(data: FeedbackRequest):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO feedback
            (user_id, message)
            VALUES (%s, %s)
            """,
            (
                data.user_id,
                data.message
            )
        )

        connection.commit()

        return {
            "message": "Feedback submitted successfully"
        }

    except Exception as error:

        connection.rollback()

        print("Feedback Error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to save feedback"
        )

    finally:

        cursor.close()
        connection.close()