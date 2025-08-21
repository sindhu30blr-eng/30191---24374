import psycopg2

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(
            dbname='24374',
            user='postgres',
            password='sindhubhat',
            host='localhost',
            port='5432'
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# User Profile CRUD
def create_user(name, email, weight):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, weight) VALUES (%s, %s, %s) RETURNING user_id;",
                (name, email, weight)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            return user_id
    return None

def read_user(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
            return cur.fetchone()
    return None

def update_user(user_id, name, email, weight):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET name = %s, email = %s, weight = %s WHERE user_id = %s;",
                (name, email, weight, user_id)
            )
            conn.commit()
            return cur.rowcount > 0
    return False

def delete_user(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE user_id = %s;", (user_id,))
            conn.commit()
            return cur.rowcount > 0
    return False

# Workout and Progress Tracking CRUD
def create_workout(user_id, workout_date, duration_minutes, exercises):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO workouts (user_id, workout_date, duration_minutes) VALUES (%s, %s, %s) RETURNING workout_id;",
                (user_id, workout_date, duration_minutes)
            )
            workout_id = cur.fetchone()[0]
            
            for exercise in exercises:
                cur.execute(
                    "INSERT INTO exercises (workout_id, exercise_name, sets, reps, weight_lifted) VALUES (%s, %s, %s, %s, %s);",
                    (workout_id, exercise['name'], exercise['sets'], exercise['reps'], exercise['weight'])
                )
            conn.commit()
            return workout_id
    return None

def read_workouts(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM workouts WHERE user_id = %s ORDER BY workout_date DESC;", (user_id,))
            workouts = cur.fetchall()
            full_data = []
            for workout in workouts:
                workout_id, user_id, workout_date, duration = workout
                cur.execute("SELECT * FROM exercises WHERE workout_id = %s;", (workout_id,))
                exercises = cur.fetchall()
                full_data.append({
                    'workout_id': workout_id,
                    'date': workout_date,
                    'duration': duration,
                    'exercises': exercises
                })
            return full_data
    return []

def delete_workout(workout_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM workouts WHERE workout_id = %s;", (workout_id,))
            conn.commit()
            return cur.rowcount > 0
    return False

# Friend Management CRUD
def add_friend(user_id, friend_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s);", (user_id, friend_id))
            conn.commit()
            return True
    return False

def remove_friend(user_id, friend_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM friends WHERE user_id = %s AND friend_id = %s;", (user_id, friend_id))
            conn.commit()
            return cur.rowcount > 0
    return False

def get_friends(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.user_id, u.name, u.email
                FROM friends f
                JOIN users u ON f.friend_id = u.user_id
                WHERE f.user_id = %s;
            """, (user_id,))
            return cur.fetchall()
    return []

# Goal Setting CRUD
def create_goal(user_id, goal_description):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO goals (user_id, goal_description) VALUES (%s, %s);", (user_id, goal_description))
            conn.commit()
            return True
    return False

def read_goals(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT goal_id, goal_description, is_completed FROM goals WHERE user_id = %s;", (user_id,))
            return cur.fetchall()
    return []

def update_goal_status(goal_id, is_completed):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE goals SET is_completed = %s WHERE goal_id = %s;", (is_completed, goal_id))
            conn.commit()
            return cur.rowcount > 0
    return False

def delete_goal(goal_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM goals WHERE goal_id = %s;", (goal_id,))
            conn.commit()
            return cur.rowcount > 0
    return False

# Business Insights & Leaderboard
def get_leaderboard(metric):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            if metric == 'total_workouts':
                cur.execute("""
                    SELECT u.name, COUNT(w.workout_id) as total_workouts
                    FROM users u
                    LEFT JOIN workouts w ON u.user_id = w.user_id
                    GROUP BY u.name
                    ORDER BY total_workouts DESC;
                """)
            elif metric == 'total_minutes':
                cur.execute("""
                    SELECT u.name, SUM(w.duration_minutes) as total_minutes
                    FROM users u
                    LEFT JOIN workouts w ON u.user_id = w.user_id
                    GROUP BY u.name
                    ORDER BY total_minutes DESC;
                """)
            return cur.fetchall()
    return []

def get_user_insights(user_id):
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(w.workout_id) AS total_workouts,
                    SUM(w.duration_minutes) AS total_minutes,
                    AVG(w.duration_minutes) AS avg_duration,
                    MIN(w.duration_minutes) AS min_duration,
                    MAX(w.duration_minutes) AS max_duration
                FROM workouts w
                WHERE w.user_id = %s;
            """, (user_id,))
            return cur.fetchone()
    return None