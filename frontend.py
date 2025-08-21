import streamlit as st
import pandas as pd
from datetime import date
from backend import (
    create_user, read_user, update_user, delete_user,
    create_workout, read_workouts, delete_workout,
    add_friend, remove_friend, get_friends,
    create_goal, read_goals, update_goal_status, delete_goal,
    get_leaderboard, get_user_insights
)

# --- Session State Management for Current User ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# --- User Login/Creation UI ---
def user_login_ui():
    st.title("Fitness Tracker - User Login - 30191")
    with st.expander("Create a new user"):
        with st.form("new_user_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("Create User")
            if submitted and name and email:
                user_id = create_user(name, email, weight)
                if user_id:
                    st.success(f"User created with ID: {user_id}. Please use this ID to log in.")
                else:
                    st.error("Failed to create user.")

    st.header("Log in with an existing user ID")
    login_id = st.number_input("Enter your user ID", min_value=1, step=1)
    if st.button("Log In"):
        user = read_user(login_id)
        if user:
            st.session_state.user_id = login_id
            st.success(f"Logged in as {user[1]}.")
            st.rerun()
        else:
            st.error("Invalid User ID.")

# --- Main Application UI ---
def main_app():
    user_id = st.session_state.user_id
    user_data = read_user(user_id)
    if not user_data:
        st.session_state.user_id = None
        st.error("User not found. Please log in again.")
        st.rerun()
    
    st.sidebar.title(f"Welcome, {user_data[1]}!")
    st.sidebar.text(f"User ID: {user_id}")
    if st.sidebar.button("Log Out"):
        st.session_state.user_id = None
        st.rerun()

    st.title("Personal Fitness Tracker 🏋️‍♀️")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "🧍 Profile", 
        "🏃 Workouts", 
        "🤝 Friends & Leaderboard", 
        "🎯 Goals"
    ])

    # --- Tab 1: Dashboard & Insights ---
    with tab1:
        st.header("Your Fitness Dashboard")
        st.subheader("Business Insights")
        insights = get_user_insights(user_id)
        if insights:
            total_workouts, total_minutes, avg_duration, min_duration, max_duration = insights
            st.metric("Total Workouts", f"{total_workouts or 0}")
            st.metric("Total Workout Minutes", f"{total_minutes or 0}")
            st.metric("Average Workout Duration (min)", f"{avg_duration or 0:.2f}")
            st.metric("Min/Max Workout Duration (min)", f"{min_duration or 0} / {max_duration or 0}")
        else:
            st.info("Log a workout to see your insights!")

    # --- Tab 2: User Profile (CRUD) ---
    with tab2:
        st.header("Your Profile")
        with st.expander("Update Profile", expanded=True):
            st.subheader("Read User Info")
            st.write(f"**Name:** {user_data[1]}")
            st.write(f"**Email:** {user_data[2]}")
            st.write(f"**Weight:** {user_data[3]} kg")

            st.subheader("Update User Info")
            with st.form("update_user_form"):
                new_name = st.text_input("New Name", value=user_data[1])
                new_email = st.text_input("New Email", value=user_data[2])
                new_weight = st.number_input("New Weight (kg)", value=float(user_data[3]), min_value=0.0, format="%.2f")
                update_submitted = st.form_submit_button("Update Profile")
                if update_submitted:
                    if update_user(user_id, new_name, new_email, new_weight):
                        st.success("Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile.")

    # --- Tab 3: Workouts (CRUD) ---
    with tab3:
        st.header("Workout & Progress Tracking")
        with st.expander("Log a New Workout (Create)", expanded=False):
            with st.form("new_workout_form"):
                workout_date = st.date_input("Date", date.today())
                duration = st.number_input("Duration (minutes)", min_value=1, step=1)
                
                st.subheader("Exercises")
                num_exercises = st.number_input("Number of exercises", min_value=1, max_value=10, step=1)
                exercises = []
                for i in range(num_exercises):
                    st.markdown(f"**Exercise {i+1}**")
                    name = st.text_input("Exercise Name", key=f"ex_name_{i}")
                    sets = st.number_input("Sets", min_value=1, key=f"sets_{i}")
                    reps = st.number_input("Reps", min_value=1, key=f"reps_{i}")
                    weight = st.number_input("Weight Lifted (kg)", min_value=0.0, key=f"weight_{i}", format="%.2f")
                    exercises.append({'name': name, 'sets': sets, 'reps': reps, 'weight': weight})
                
                submitted = st.form_submit_button("Log Workout")
                if submitted:
                    if create_workout(user_id, workout_date, duration, exercises):
                        st.success("Workout logged successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to log workout.")

        st.subheader("Workout History (Read & Delete)")
        workouts = read_workouts(user_id)
        if workouts:
            for workout in workouts:
                with st.expander(f"Workout on {workout['date']} - {workout['duration']} mins"):
                    for i, exercise in enumerate(workout['exercises']):
                        st.write(f"**Exercise {i+1}:** {exercise[2]}")
                        st.write(f"Sets: {exercise[3]}, Reps: {exercise[4]}, Weight: {exercise[5]} kg")
                    if st.button("Delete Workout", key=f"del_{workout['workout_id']}"):
                        if delete_workout(workout['workout_id']):
                            st.success("Workout deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete workout.")
        else:
            st.info("No workouts logged yet.")

    # --- Tab 4: Social & Leaderboard (CRUD & Insights) ---
    with tab4:
        st.header("Friends & Leaderboard")
        
        st.subheader("Manage Friends")
        friends = get_friends(user_id)
        if friends:
            st.write("Your current friends:")
            friends_df = pd.DataFrame(friends, columns=['ID', 'Name', 'Email'])
            st.dataframe(friends_df)
        else:
            st.info("You don't have any friends yet.")
            
        col1, col2 = st.columns(2)
        with col1:
            with st.form("add_friend_form"):
                friend_id = st.number_input("Friend's User ID to add", min_value=1, step=1)
                if st.form_submit_button("Add Friend"):
                    if add_friend(user_id, friend_id):
                        st.success("Friend added!")
                        st.rerun()
                    else:
                        st.error("Failed to add friend.")
        with col2:
            with st.form("remove_friend_form"):
                friend_id = st.number_input("Friend's User ID to remove", min_value=1, step=1)
                if st.form_submit_button("Remove Friend"):
                    if remove_friend(user_id, friend_id):
                        st.success("Friend removed.")
                        st.rerun()
                    else:
                        st.error("Failed to remove friend.")
                        
        st.subheader("Leaderboard")
        metric_choice = st.selectbox("Select metric for ranking", ["total_workouts", "total_minutes"])
        leaderboard_data = get_leaderboard(metric_choice)
        if leaderboard_data:
            leaderboard_df = pd.DataFrame(leaderboard_data, columns=['Name', metric_choice.replace('_', ' ').title()])
            leaderboard_df['Rank'] = leaderboard_df[leaderboard_df.columns[1]].rank(ascending=False, method='min').astype(int)
            leaderboard_df.set_index('Rank', inplace=True)
            st.dataframe(leaderboard_df.sort_index())
        else:
            st.info("No leaderboard data available.")
            
    # --- Tab 5: Goals (CRUD) ---
    with tab5:
        st.header("Goal Setting")
        
        st.subheader("Add a New Goal")
        with st.form("new_goal_form"):
            goal_desc = st.text_input("Enter your goal (e.g., 'Workout 5 times a week')")
            if st.form_submit_button("Create Goal"):
                if create_goal(user_id, goal_desc):
                    st.success("Goal added!")
                    st.rerun()
                else:
                    st.error("Failed to add goal.")
                    
        st.subheader("Your Goals")
        goals = read_goals(user_id)
        if goals:
            for goal in goals:
                goal_id, description, is_completed = goal
                col_g1, col_g2, col_g3 = st.columns([0.7, 0.1, 0.2])
                with col_g1:
                    st.write(f"- {description}")
                with col_g2:
                    completed = st.checkbox("Completed?", value=is_completed, key=f"goal_check_{goal_id}")
                    if completed != is_completed:
                        update_goal_status(goal_id, completed)
                        st.rerun()
                with col_g3:
                    if st.button("Delete", key=f"del_goal_{goal_id}"):
                        if delete_goal(goal_id):
                            st.success("Goal deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete goal.")
        else:
            st.info("No goals set yet.")


# --- Main app flow ---
if st.session_state.user_id:
    main_app()
else:
    user_login_ui()