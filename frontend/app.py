import streamlit as st
import requests
from datetime import datetime

# Backend base API url
#API_URL = "http://127.0.0.1:8000"
# Use localhost for internal container communication on Railway
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Team Task Manager", layout="wide")

# --- Initialize Session States ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Helper headers for authenticated requests
def get_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# --- UI Header ---
st.title("🚀 Team Task Manager")
st.markdown("---")

# --- AUTHENTICATION SIDEBAR FLOW ---
with st.sidebar:
    if not st.session_state.token:
        st.subheader("Login / Register")
        auth_mode = st.radio("Choose Action", ["Login", "Register"])
        
        username = st.text_input("Username")
        email = st.text_input("Email (For Registration Only)")
        password = st.text_input("Password", type="password")
        
        if auth_mode == "Register":
            role = st.selectbox("Role", ["Member", "Admin"])
            if st.button("Register Account"):
                payload = {"username": username, "email": email, "password": password, "role": role}
                res = requests.post(f"{API_URL}/register", json=payload)
                if res.status_code == 201:
                    st.success("Account created successfully! Please switch to Login.")
                else:
                    st.error(res.json().get("detail", "Registration Failed"))
                    
        elif auth_mode == "Login":
            if st.button("Log In"):
                payload = {"username": username, "password": password}
                res = requests.post(f"{API_URL}/token", data=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.role = data["role"]
                    st.session_state.username = data["username"]
                    st.rerun()
                else:
                    st.error("Invalid credentials setup.")
    else:
        st.subheader(f"👤 Active: {st.session_state.username}")
        st.info(f"Role Privileges: {st.session_state.role}")
        if st.button("Log Out"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.username = None
            st.rerun()

# --- MAIN APP ROUTING INTERFACE ---
if not st.session_state.token:
    st.info("Please use the left sidebar panel to log in or register a new team profile.")
else:
   # Fetch Data common for dashboards safely
    headers = get_headers()
    projects, tasks, all_users = [], [], []
    
    try:
        projects_res = requests.get(f"{API_URL}/projects", headers=headers)
        if projects_res.status_code == 200: projects = projects_res.json()
        
        tasks_res = requests.get(f"{API_URL}/tasks", headers=headers)
        if tasks_res.status_code == 200: tasks = tasks_res.json()
        
        users_res = requests.get(f"{API_URL}/users", headers=headers)
        if users_res.status_code == 200: all_users = users_res.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Connection to Backend API lost. Please verify your FastAPI server is active on port 8000.")
    
    # Create layout tabs
    tab_dashboard, tab_projects, tab_tasks = st.tabs(["📊 Performance Dashboard", "📁 Project Portfolios", "📝 Tasks Space"])
    
    # 1. PERFORMANCE DASHBOARD TAB
    with tab_dashboard:
        st.subheader("Workspace Progress Analytics")
        
        # Calculate dynamic matrix aggregates
        total_tasks = len(tasks)
        todo_count = len([t for t in tasks if t["status"] == "Todo"])
        progress_count = len([t for t in tasks if t["status"] == "In Progress"])
        done_count = len([t for t in tasks if t["status"] == "Done"])
        
        # Determine overdue metrics safely
        overdue_count = 0
        current_date = datetime.today().date()
        for t in tasks:
            if t["due_date"] and t["status"] != "Done":
                task_due = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                if task_due < current_date:
                    overdue_count += 1
                    
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Scope", total_tasks)
        col2.metric("To Do", todo_count)
        col3.metric("In Progress", progress_count)
        col4.metric("Completed", done_count)
        col5.metric("🚨 OVERDUE", overdue_count, delta_color="inverse")
        
        st.markdown("---")
        
    # 2. PROJECT PORTFOLIOS TAB
    with tab_projects:
        st.subheader("Active Company Projects")
        
        # ADMIN PRIVILEGE: Create Projects
        if st.session_state.role.lower() == "admin":
            with st.expander("➕ Administrative Action: Initialize New Project"):
                p_name = st.text_input("Project Name Label")
                p_desc = st.text_area("Scope Brief / Description")
                if st.button("Deploy Project Container"):
                    if p_name:
                        res = requests.post(f"{API_URL}/projects", json={"name": p_name, "description": p_desc}, headers=headers)
                        if res.status_code == 201:
                            st.success("Project launched successfully!")
                            st.rerun()
                    else:
                        st.warning("Project Name field is required.")
                        
        if projects:
            for proj in projects:
                st.markdown(f"### 📁 {proj['name']}")
                st.caption(proj['description'] or "No structural description provided.")
        else:
            st.write("No active project instances configured yet.")
            
    # 3. TASKS SPACE TAB
    with tab_tasks:
        st.subheader("Task Allocation Matrix")
        
        # ADMIN PRIVILEGE: Task Creation and Assignment
        if st.session_state.role.lower() == "admin":
            with st.expander("➕ Administrative Action: Issue and Delegate Task"):
                if not projects:
                    st.warning("Please configure at least one active project before provisioning tasks.")
                else:
                    t_title = st.text_input("Task Deliverable Name")
                    t_desc = st.text_area("Task Operational Requirements")
                    t_due = st.date_input("Target Due Date Limit")
                    
                    proj_mapping = {p["name"]: p["id"] for p in projects}
                    selected_proj = st.selectbox("Assign to Project Group", list(proj_mapping.keys()))
                    
                    user_mapping = {u["username"]: u["id"] for u in all_users}
                    selected_user = st.selectbox("Delegate Operational Owner", list(user_mapping.keys()))
                    
                    if st.button("Finalize Task Assignment"):
                        payload = {
                            "title": t_title,
                            "description": t_desc,
                            "due_date": str(t_due),
                            "project_id": proj_mapping[selected_proj],
                            "assigned_to_id": user_mapping[selected_user],
                            "status": "Todo"
                        }
                        res = requests.post(f"{API_URL}/tasks", json=payload, headers=headers)
                        if res.status_code == 201:
                            st.success("Task dispatched and assigned successfully!")
                            st.rerun()
                            
        # DISPLAY AND UPDATE STATUS
        if tasks:
            for task in tasks:
                # Find matching structural metrics for display
                p_name = next((p["name"] for p in projects if p["id"] == task["project_id"]), "Unknown Project")
                owner = next((u["username"] for u in all_users if u["id"] == task["assigned_to_id"]), "Unassigned")
                
                with st.container():
                    col_info, col_status_mod = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"#### 📝 {task['title']} (`{task['status']}`)")
                        st.write(f"**Brief:** {task['description']}")
                        st.caption(f"**Project Context:** {p_name} | **Owner:** {owner} | **Due By:** {task['due_date']}")
                        
                    with col_status_mod:
                        status_options = ["Todo", "In Progress", "Done"]
                        try:
                            current_idx = status_options.index(task["status"])
                        except ValueError:
                            current_idx = 0
                            
                        new_status = st.selectbox(
                            "Transition State", 
                            status_options, 
                            index=current_idx, 
                            key=f"status_select_{task['id']}"
                        )
                        
                        if new_status != task["status"]:
                            patch_res = requests.patch(
                                f"{API_URL}/tasks/{task['id']}/status", 
                                json={"status": new_status}, 
                                headers=headers
                            )
                            if patch_res.status_code == 200:
                                st.success("State altered!")
                                st.rerun()
                            else:
                                st.error("Authorization access error.")
                st.markdown("---")
        else:
            st.write("No active deliverables assigned to this profile perspective currently.")