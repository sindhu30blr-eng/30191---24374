CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    weight NUMERIC(5, 2)
);

CREATE TABLE workouts (
    workout_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    workout_date DATE NOT NULL,
    duration_minutes INT
);

CREATE TABLE exercises (
    exercise_id SERIAL PRIMARY KEY,
    workout_id INT REFERENCES workouts(workout_id) ON DELETE CASCADE,
    exercise_name VARCHAR(255) NOT NULL,
    sets INT,
    reps INT,
    weight_lifted NUMERIC(10, 2)
);

CREATE TABLE friends (
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    friend_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, friend_id)
);

CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    goal_description VARCHAR(255) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE
);