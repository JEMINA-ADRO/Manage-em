import streamlit as st
import datetime
import sqlite3
from ai_service import analyze_tasks_with_ai, build_task_context, load_ai_model, parse_task_with_ai

@st.cache_resource
def get_ai_model():
    return load_ai_model()

conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    deadline TEXT,
    priority TEXT,
    status TEXT
)
""")

conn.commit()

def add_task_to_db(name, deadline, priority, status):
    cursor.execute("""
        INSERT INTO tasks (name, deadline, priority, status)
        VALUES (?, ?, ?, ?)
    """, (name, deadline, priority, status))

    conn.commit()

def get_tasks_from_db(
        sort_by="id", 
        ascending=True, 
        search_query="", 
        priority_filter="All", 
        status_filter="All",
        deadline_from=None,
        deadline_to=None
        ):
    allowed_columns = ["id", "name", "deadline", "priority", "status"]
    
    if sort_by not in allowed_columns:
        sort_by = "id"

    if ascending:
        direction = "ASC"
    else:
        direction = "DESC"

    conditions=[]
    parameters=[]

    if search_query:
        conditions.append("name LIKE ?")
        parameters.append(f"%{search_query}%")

    if priority_filter != "All":
        conditions.append("priority = ?")
        parameters.append(priority_filter)

    if status_filter != "All":
        conditions.append("status = ?")
        parameters.append(status_filter)

    if deadline_from is not None and deadline_to is not None:
        conditions.append("deadline BETWEEN ? AND ?")
        parameters.extend([deadline_from, deadline_to])

    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
    else:
        where_clause = ""

    if sort_by == "priority":
        query = (f"""
            SELECT * FROM tasks
            {where_clause}
            ORDER BY CASE priority
                WHEN 'Low' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'High' THEN 3
            END {direction}
        """)
    else:
        query = (f"SELECT * FROM tasks {where_clause} ORDER BY {sort_by} {direction}")

    cursor.execute(query, parameters)
    rows = cursor.fetchall()

    tasks = []

    for row in rows:
        tasks.append({
            "id": row[0],
            "name": row[1],
            "deadline": row[2],
            "priority": row[3],
            "status": row[4]
        })

    return tasks

def update_task_in_db(task_id, name, deadline, priority, status):
    cursor.execute("""
        UPDATE tasks
        SET name = ?, deadline = ?, priority = ?, status = ?
        WHERE id = ?
    """, (name, deadline, priority, status, task_id))

    conn.commit()

def update_task_status_in_db(task_id, status):
    cursor.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (status, task_id))

    conn.commit()

def delete_task_from_db(task_id):
    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    

st.set_page_config(layout="wide")

st.title("Manage 'em")
st.write("by JEMINA J (10607)")

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "show_add_row" not in st.session_state:
    st.session_state.show_add_row = False

if "sort_by" not in st.session_state:
    st.session_state.sort_by = "id"

if "sort_ascending" not in st.session_state:
    st.session_state.sort_ascending = True

if "applied_search" not in st.session_state:
    st.session_state.applied_search = ""

if "applied_priority" not in st.session_state:
    st.session_state.applied_priority = "All"

if "applied_status" not in st.session_state:
    st.session_state.applied_status = "All"

if "filter_deadline_from" not in st.session_state:
    st.session_state.filter_deadline_from = None

if "filter_deadline_to" not in st.session_state:
    st.session_state.filter_deadline_to = None

if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None

if "ai_task_text" not in st.session_state:
    st.session_state.ai_task_text = ""

tasks = get_tasks_from_db(st.session_state.sort_by, 
                          st.session_state.sort_ascending, 
                          st.session_state.applied_search,
                          st.session_state.applied_priority,
                          st.session_state.applied_status,
                          st.session_state.filter_deadline_from,
                          st.session_state.filter_deadline_to
                            )

status_map = {"⏳": "Pending", "✅": "Completed", "All": "All"}
priority_map = {"🟢": "Low", "🟡": "Medium", "🔴": "High", "All": "All"}
if "filter" not in st.session_state:
    st.session_state.filter = False

all_tasks = get_tasks_from_db("id", True, "", "All", "All", None, None)
total_tasks = len(all_tasks)

pending_count = sum(1 for task in all_tasks if task["status"] == "Pending")

completed_count = sum(1 for task in all_tasks if task["status"] == "Completed")

high_priority_pending = sum(1 for task in all_tasks if task["status"] == "Pending" and task["priority"] == "High")

if total_tasks > 0:
    completion_percentage = (completed_count / total_tasks) * 100
else:
    completion_percentage = 0

st.subheader("Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tasks", total_tasks)
col2.metric("Pending Tasks", pending_count)
col3.metric("Completed Tasks", completed_count)
col4.metric("High Priority Pending", high_priority_pending)

st.write("")

st.progress(completion_percentage / 100)
st.caption(f"{completion_percentage:.1f}% of tasks completed")

st.subheader("Your Task List")

st.write("")

head1, head2, head3, head4, head5, head6, head7, head8 = st.columns([0.1, 0.25, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05])
with head1:
    text_col, btn_col = st.columns([0.7, 0.3])
    with text_col:
        st.write("**ID**")
    with btn_col:
        if st.button("⥯", key="sort_id_btn"):
            if st.session_state.sort_by == "id":
                st.session_state.sort_ascending = not st.session_state.sort_ascending
            else:
                st.session_state.sort_by = "id"
                st.session_state.sort_ascending = True
            st.rerun()
with head2:
    text_col, btn_col = st.columns([0.8, 0.2])
    with text_col:
        st.write("**Task**")
    with btn_col:
        if st.button("⥯", key="sort_btn"):
            if st.session_state.sort_by == "name":
                st.session_state.sort_ascending = not st.session_state.sort_ascending
            else:
                st.session_state.sort_by = "name"
                st.session_state.sort_ascending = True
            st.rerun()
with head3:
    text_col, btn_col = st.columns([0.7, 0.3])
    with text_col:
        st.write("**Deadline**")
    with btn_col:
        if st.button("⥯", key="sort_deadline_btn"):
            if st.session_state.sort_by == "deadline":
                st.session_state.sort_ascending = not st.session_state.sort_ascending
            else:
                st.session_state.sort_by = "deadline"
                st.session_state.sort_ascending = True
            st.rerun()
with head4:
    text_col, btn_col = st.columns([0.7, 0.3])
    with text_col:
        st.write("**Priority**")
    with btn_col:
        if st.button("⥯", key="sort_priority_btn"):
            if st.session_state.sort_by == "priority":
                st.session_state.sort_ascending = not st.session_state.sort_ascending
            else:
                st.session_state.sort_by = "priority"
                st.session_state.sort_ascending = True
            st.rerun()
with head5:
    text_col, btn_col = st.columns([0.7, 0.3])
    with text_col:
        st.write("**Status**")
    with btn_col:
        if st.button("⥯", key="sort_status_btn"):
            if st.session_state.sort_by == "status":
                st.session_state.sort_ascending = not st.session_state.sort_ascending
            else:
                st.session_state.sort_by = "status"
                st.session_state.sort_ascending = True
            st.rerun()

with head6:
    st.write("**Actions**")
with head7:
    if st.button("⏚", key="filter_btn"):
        if not st.session_state.filter:
            st.session_state.filter = True
        elif st.session_state.filter:
            st.session_state.filter = False
with head8:
    if st.button("➕", key="add_new_btn"):
        st.session_state.show_add_row = True
        st.rerun()

if st.session_state.filter:
    col_empty_1, col_search, col_filter_deadline, col_filter_priority, col_filter_status, col_empty_2 = st.columns([0.1, 0.25, 0.2, 0.15, 0.1, 0.2])
    with col_empty_1:
        st.empty()
    with col_search:
        search_query = st.text_input("Search", placeholder="Type to search...", key="search_box", label_visibility="collapsed")
    with col_filter_deadline:
        filter_date_range = st.date_input("Filter by Deadline", value=[], label_visibility="collapsed")
        t1, t2 = st.columns(2)
        with t1:
            filter_time_from = st.time_input("From Time", value=datetime.time(0, 0), label_visibility="collapsed")
        with t2:
            filter_time_to = st.time_input("To Time", value=datetime.time(23, 59), label_visibility="collapsed")
    with col_filter_priority:
        filter_priority = priority_map[st.selectbox("Filter by Priority", ["All", "🟢", "🟡", "🔴"], label_visibility="collapsed")]
    with col_filter_status:
        filter_status = status_map[st.selectbox("Filter", ["All", "⏳", "✅"], label_visibility="collapsed")]
    with col_empty_2:
        if st.button("Apply Filter", key="apply_Filter_btn"):
            st.session_state.applied_search = search_query.strip()
            st.session_state.applied_priority = filter_priority
            st.session_state.applied_status = filter_status
            if len(filter_date_range) == 2:
                start_dt = datetime.datetime.combine(filter_date_range[0], filter_time_from)
                end_dt = datetime.datetime.combine(filter_date_range[1], filter_time_to)
                st.session_state.filter_deadline_from = start_dt.strftime("%Y-%m-%d %H:%M")
                st.session_state.filter_deadline_to = end_dt.strftime("%Y-%m-%d %H:%M")
            else:
                st.session_state.filter_deadline_from = None
                st.session_state.filter_deadline_to = None

            st.rerun()
st.divider()

if (not tasks) and (not st.session_state.show_add_row):
    st.info("No tasks yet. Click the ➕ button above to add one!")

else:
    for index, task in enumerate(tasks):
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.1, 0.25, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05])

        with col1:
            st.write(f"**{task['id']}**")
        
        if st.session_state.edit_index == index:
            with col2:
                updated_name = st.text_input("Update task", value=task['name'], key=f"edit_box_{index}", label_visibility="collapsed")
            with col3:
                dt_obj = datetime.datetime.strptime(task['deadline'], "%Y-%m-%d %H:%M")
                col3_1, col3_2 = st.columns([0.5, 0.5])
                with col3_1:
                    updated_date = st.date_input("Update deadline", value=dt_obj.date(), key=f"date_box_{index}", label_visibility="collapsed")
                with col3_2:
                    updated_time = st.time_input("Update Time", value=dt_obj.time(), key=f"time_box_{index}", label_visibility="collapsed")
            with col4:
                updated_priority = priority_map[st.selectbox("Update priority", ["🟢", "🟡", "🔴"], index=["Low", "Medium", "High"].index(task['priority']), key=f"priority_box_{index}", label_visibility="collapsed")]
            with col5:
                updated_status = status_map[st.selectbox("Update status", ["⏳", "✅"], index=["Pending", "Completed"].index(task['status']), key=f"status_box_{index}", label_visibility="collapsed")]
            with col6:
                if st.button("💾", key=f"save_{index}"):
                    update_task_in_db(task["id"], updated_name, f"{updated_date.strftime('%Y-%m-%d')} {updated_time.strftime('%H:%M')}", updated_priority, updated_status)
                    st.session_state.edit_index = None
                    st.session_state.ai_summary = None
                    st.rerun()
            with col7:
                if st.button("❌", key=f"cancel_{index}"):
                    st.session_state.edit_index = None
                    st.rerun()
            with col8:
                st.empty()
        else:
            with col2:
                st.write(f"{task['name']}")
            with col3:
                deadline_obj = datetime.datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M")
                st.write(deadline_obj.strftime("%d-%m-%Y %H:%M"))
            with col4:
                if task['priority'] == "Low":
                    st.write("🟢")
                elif task['priority'] == "Medium":
                    st.write("🟡")
                elif task['priority'] == "High":
                    st.write("🔴")
            with col5:
                if task["status"] == "Completed":
                    st.write("✅")
                elif task["status"] == "Pending":
                    st.write("⏳")
            with col6:
                action = "✅" if task["status"] == "Pending" else "⏳"
                if st.button(action, key=f"complete_{index}"):
                    if task["status"] == "Completed":
                        new_status = "Pending"
                    elif task["status"] == "Pending":
                        new_status = "Completed"
                    update_task_status_in_db(task["id"], new_status)
                    st.session_state.ai_summary = None
                    st.rerun()
            with col7:
                if st.button("✏️", key=f"edit_{index}"):
                    st.session_state.edit_index = index
                    st.rerun()
            with col8:
                if st.button("🗑️", key=f"delete_{index}"):
                    # st.session_state.tasks.pop(index)
                    delete_task_from_db(task["id"])
                    st.session_state.ai_summary = None
                    st.rerun()
        
if st.session_state.show_add_row:
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.1, 0.25, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05])
    with col1:
        st.write("")
    with col2:
        new_name = st.text_input("Add new task", placeholder="Type a new task...", key="new_task_name", label_visibility="collapsed")
    with col3:
        col3_1, col3_2 = st.columns([0.5, 0.5])
        with col3_1:
            new_deadline = st.date_input("Deadline", key="new_task_deadline", label_visibility="collapsed")
        with col3_2:
            new_time = st.time_input("Deadline Time", value=datetime.time(12, 0), key="new_task_time", label_visibility="collapsed")
    with col4:
        new_priority = priority_map[st.selectbox("Priority", ["🟢", "🟡", "🔴"], key="new_task_priority", label_visibility="collapsed")]
    with col5:
        new_status = status_map[st.selectbox("Status", ["⏳", "✅"], key="new_task_status", label_visibility="collapsed")]
    with col6:
        if st.button("💾", key=f"save_new"):
            if new_name:
                deadline_txt = f"{new_deadline.strftime('%Y-%m-%d')} {new_time.strftime('%H:%M')}"
                add_task_to_db(new_name, deadline_txt, new_priority, new_status)
                st.session_state.ai_summary = None
                st.session_state.show_add_row = False
                st.rerun()
            else:
                st.warning("Please type a task first!")
    with col7:
        if st.button("❌", key=f"cancel_new"):
            st.session_state.show_add_row = False
            st.rerun()
    with col8:
        st.empty()

# st.write(tasks)

# st.write(
#     "Applied from:",
#     st.session_state.filter_deadline_from
# )

# st.write(
#     "Applied to:",
#     st.session_state.filter_deadline_to
# )

st.write("")
st.write("")
st.write("Describe your text")
text_col, button_col, sum_col = st.columns([0.6, 0.2, 0.2])

with text_col:
    ai_task_text = st.text_input(
                    "Describe your task",
                    placeholder="e.g. Finish report tomorrow at 6 PM high priority",
                    label_visibility ="collapsed"
                )
with button_col:
    add_w_ai = st.button("Add with AI", icon = "➕")

if add_w_ai:
    if not ai_task_text.strip():
        st.warning("Please enter a task description.")
    else:
        try:
            with st.spinner("Understanding your task..."):

                tokenizer, model = get_ai_model()

                current_datetime = datetime.datetime.now()

                parsed_task = parse_task_with_ai(
                    ai_task_text,
                    current_datetime,
                    tokenizer,
                    model
                )

                add_task_to_db(
                    parsed_task["name"],
                    parsed_task["deadline"],
                    parsed_task["priority"],
                    parsed_task["status"]
                )

                st.session_state.ai_summary = None
                st.rerun()

        except Exception:
            st.error(
                "AI could not understand this task. Please try rephrasing it."
            )

with sum_col:
    generate_summary = st.button(
        "Generate AI Summary", 
        icon=":material/auto_awesome:", 
        use_container_width=True)

if generate_summary:
    with st.spinner("Analyzing your tasks..."):
        if not all_tasks:
            st.session_state.ai_summary = "No tasks have been added yet."
        else:
            tokenizer, model = get_ai_model()
            task_context = build_task_context(all_tasks)
            st.session_state.ai_summary = analyze_tasks_with_ai(task_context, tokenizer, model)
if st.session_state.ai_summary:
    st.markdown(st.session_state.ai_summary)