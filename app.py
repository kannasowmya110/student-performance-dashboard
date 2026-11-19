
import streamlit as st
import pandas as pd
import sqlite3
import json
import hmac
# SQLite Database Connection
DB_PATH = "student_performance.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT UNIQUE,
            total REAL,
            average REAL,
            result TEXT,
            rank INTEGER,
            subject_marks TEXT,
            saved_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Safely add columns if an older database already exists
    cursor.execute("PRAGMA table_info(students)")
    existing_columns = [column[1] for column in cursor.fetchall()]

    if "subject_marks" not in existing_columns:
        cursor.execute("ALTER TABLE students ADD COLUMN subject_marks TEXT")

    if "saved_at" not in existing_columns:
        cursor.execute("ALTER TABLE students ADD COLUMN saved_at TEXT")

    conn.commit()
    conn.close()


def save_students_to_database(data, subject_columns):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in data.iterrows():
        marks_json = json.dumps({
            subject: float(row[subject])
            for subject in subject_columns
        })

        cursor.execute("""
            INSERT INTO students
                (student_name, total, average, result, rank, subject_marks)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_name) DO UPDATE SET
                total = excluded.total,
                average = excluded.average,
                result = excluded.result,
                rank = excluded.rank,
                subject_marks = excluded.subject_marks,
                saved_at = CURRENT_TIMESTAMP
        """, (
            str(row["student"]).strip(),
            float(row["Total"]),
            float(row["Average"]),
            str(row["Result"]),
            int(row["Rank"]),
            marks_json
        ))

    conn.commit()
    conn.close()


def get_saved_students():
    conn = sqlite3.connect(DB_PATH)
    saved_df = pd.read_sql_query("""
        SELECT student_name AS Student,
               total AS Total,
               average AS Average,
               result AS Result,
               rank AS Rank,
               subject_marks AS Subject_Marks,
               saved_at AS Saved_At
        FROM students
        ORDER BY rank ASC, student_name ASC
    """, conn)
    conn.close()
    return saved_df


def search_student_in_database(student_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT student_name, total, average, result, rank, subject_marks, saved_at
        FROM students
        WHERE student_name LIKE ? COLLATE NOCASE
        ORDER BY student_name
    """, (f"%{student_name.strip()}%",))

    records = cursor.fetchall()
    conn.close()
    return records


create_database()

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ADMIN LOGIN
# ==========================================

# For local practice, these demo credentials work until secrets are configured.
# For deployment, set credentials in .streamlit/secrets.toml.
try:
    ADMIN_USERNAME = st.secrets["admin"]["username"]
    ADMIN_PASSWORD = st.secrets["admin"]["password"]
except Exception:
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.markdown(
        "<h1 style='text-align:center;color:#7C3AED;'>🔐 Admin Login</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;'>Login to access the Student Performance Dashboard</p>",
        unsafe_allow_html=True
    )

    with st.form("admin_login_form"):
        username_input = st.text_input("Username", placeholder="Enter admin username")
        password_input = st.text_input(
            "Password",
            type="password",
            placeholder="Enter admin password"
        )
        login_submitted = st.form_submit_button("Login", use_container_width=True)

    if login_submitted:
        username_ok = hmac.compare_digest(username_input, ADMIN_USERNAME)
        password_ok = hmac.compare_digest(password_input, ADMIN_PASSWORD)

        if username_ok and password_ok:
            st.session_state.admin_logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect username or password. Please try again.")

    st.info("Local demo login: username `admin` | password `admin123`")
    st.stop()

# ==========================================
# 2. CUSTOM PURPLE GRADIENT DESIGN
# ==========================================

st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(135deg, #F8F5FF, #F1EAFE);
}

/* Main content */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Header */
.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #6D28D9, #C026D3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fadeIn 1.2s ease-in-out;
}

.sub-title {
    text-align: center;
    font-size: 17px;
    color: #7C3AED;
    margin-bottom: 20px;
    animation: fadeIn 1.5s ease-in-out;
}

/* Metric Cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FFFFFF, #F3E8FF);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #DDD6FE;
    box-shadow: 0 5px 15px rgba(109,40,217,0.10);
    transition: all 0.3s ease;
    animation: slideUp 0.8s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(109,40,217,0.20);
}

/* Section headings */
h1, h2, h3 {
    color: #5B21B6 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4C1D95, #7E22CE);
}

/* Sidebar alert text visibility */
section[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: #F3E8FF !important;
    border: 1px solid #C4B5FD !important;
    border-radius: 12px;
}

section[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: #4C1D95 !important;
}

/* Sidebar normal text */
section[data-testid="stSidebar"] p {
    color: #FFFFFF !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background: linear-gradient(90deg, #7C3AED, #C026D3);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton button:hover,
.stDownloadButton button:hover {
    transform: scale(1.03);
    box-shadow: 0 5px 18px rgba(126,34,206,0.30);
}

/* File uploader */
div[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 2px dashed #A78BFA;
    border-radius: 15px;
    padding: 15px;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border: 1px solid #DDD6FE;
    border-radius: 14px;
    overflow: hidden;
}

/* Input fields */
.stTextInput input {
    border-radius: 10px;
    border: 1px solid #C4B5FD;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Divider */
hr {
    border-color: #DDD6FE;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. DASHBOARD HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🎓 Student Performance Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '✨ Student Performance Analysis and Prediction System ✨'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# 4. SIDEBAR
# ==========================================

st.sidebar.title("🎓 Student Dashboard")
st.sidebar.success("🔓 Admin logged in")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.admin_logged_in = False
    st.rerun()

st.sidebar.markdown("### Welcome!")
st.sidebar.write("Analyze student academic performance.")
st.sidebar.info(
    "📊 Python | Pandas | Streamlit"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Dashboard Features")
st.sidebar.markdown("""
- 📂 CSV Upload
- 📋 Student Analysis
- 📊 Performance Charts
- 🏆 Ranking System
- ✅ Pass / Fail Analysis
- 🔮 Performance Prediction
- 📥 Report Download
- 📚 Study Suggestions
""")


# ==========================================
# 5. CSV UPLOAD
# ==========================================

st.header("📂 Step 1: Upload Student Dataset")

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info("👆 Please upload a CSV file to start analysis.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception:
    st.error("Unable to read this CSV file. Please check its format.")
    st.stop()

df.columns = df.columns.str.strip().str.lower()

if df.empty:
    st.warning("The uploaded CSV has no student records.")
    st.stop()

if "student" not in df.columns:
    st.error("Your CSV must contain a 'student' column.")
    st.stop()

df["student"] = df["student"].astype(str).str.strip()

if df["student"].eq("").any() or df["student"].str.lower().eq("nan").any():
    st.error("Student names cannot be empty.")
    st.stop()

if df["student"].duplicated().any():
    st.error("Duplicate student names found. Please make each student name unique.")
    st.stop()

subject_columns = [
    col for col in df.columns if col != "student"
]

if not subject_columns:
    st.error("Please add at least one subject column.")
    st.stop()

# Convert subject marks to numbers
for col in subject_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

if df[subject_columns].isna().any().any():
    st.error("Please enter valid numeric marks in all subject columns.")
    st.stop()

if not df[subject_columns].apply(
    lambda col: col.between(0, 100).all()
).all():
    st.error("Marks must be between 0 and 100.")
    st.stop()

st.success("✅ CSV File Uploaded Successfully!")

st.info(
    f"📚 Detected {len(subject_columns)} subjects: "
    + ", ".join(subject_columns).title()
)


# ==========================================
# 6. TOTAL, AVERAGE, RESULT AND RANK
# ==========================================

df["Total"] = df[subject_columns].sum(axis=1)

df["Average"] = df[subject_columns].mean(axis=1)

pass_marks = 35

df["Result"] = df[subject_columns].apply(
    lambda row: "Pass" if (row >= pass_marks).all() else "Fail",
    axis=1
)

df["Rank"] = df["Average"].rank(
    ascending=False,
    method="dense"
).astype(int)


# ==========================================
# 7. COMPLETE STUDENT PERFORMANCE TABLE
# ==========================================

st.header("📋 Step 2: Student Performance Analysis")

display_columns = (
    ["student"] +
    subject_columns +
    ["Total", "Average", "Result", "Rank"]
)

display_df = df[display_columns].sort_values(
    by=["Rank", "student"]
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 7A. SAVE AND VIEW SQLITE DATABASE RECORDS
# ==========================================

st.subheader("🗄️ Save Student Records to SQLite Database")
st.write(
    "Save the uploaded student results permanently. "
    "If a student name already exists, the latest uploaded marks will update that record."
)

if st.button("💾 Save Student Records to Database", use_container_width=True):
    try:
        save_students_to_database(df, subject_columns)
        st.success(f"Successfully saved/updated {len(df)} student records in SQLite!")
    except sqlite3.Error as error:
        st.error(f"Database error: {error}")

st.subheader("📚 Records Stored in Database")
saved_students_df = get_saved_students()

if saved_students_df.empty:
    st.info("No student records saved yet. Click the Save Student Records button above.")
else:
    st.metric("Total Records in Database", len(saved_students_df))
    st.dataframe(
        saved_students_df.drop(columns=["Subject_Marks"]),
        use_container_width=True,
        hide_index=True
    )
    with st.expander("View saved subject-wise marks"):
        st.dataframe(
            saved_students_df[["Student", "Subject_Marks"]],
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# 7B. SEARCH STUDENT AND VIEW INDIVIDUAL REPORT
# ==========================================

st.subheader("🔎 Search Student and View Individual Report")

search_name = st.text_input(
    "Enter student name",
    placeholder="Type full name or part of the name",
    key="database_student_search"
)

if st.button("🔍 Search Student", use_container_width=True):
    if not search_name.strip():
        st.warning("Please enter a student name to search.")
    else:
        try:
            matching_students = search_student_in_database(search_name)

            if not matching_students:
                st.warning("No matching student found in the database. Save the uploaded records first.")
            else:
                st.success(f"Found {len(matching_students)} matching student record(s).")

                for record in matching_students:
                    student_name, total, average, result, student_rank, marks_json, saved_at = record

                    st.markdown(f"### 👩‍🎓 {student_name}")
                    report_col1, report_col2, report_col3, report_col4 = st.columns(4)
                    report_col1.metric("Total Marks", f"{total:.2f}")
                    report_col2.metric("Average", f"{average:.2f}")
                    report_col3.metric("Result", result)
                    report_col4.metric("Rank", student_rank)

                    try:
                        marks_data = json.loads(marks_json) if marks_json else {}
                    except (json.JSONDecodeError, TypeError):
                        marks_data = {}

                    if marks_data:
                        marks_df = pd.DataFrame(
                            list(marks_data.items()),
                            columns=["Subject", "Marks"]
                        )
                        st.write("**Subject-wise Marks**")
                        st.dataframe(
                            marks_df,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Subject-wise marks are not available for this record.")

                    st.caption(f"Last saved: {saved_at or 'Not available'}")
                    st.divider()

        except sqlite3.Error as error:
            st.error(f"Database search error: {error}")


# ==========================================
# 8. PERFORMANCE SUMMARY
# ==========================================

st.header("📊 Step 3: Performance Summary")

total_students = len(df)
highest_total = df["Total"].max()
class_average = df["Average"].mean()

pass_count = (df["Result"] == "Pass").sum()
fail_count = (df["Result"] == "Fail").sum()

pass_percentage = (pass_count / total_students) * 100

col1, col2, col3 = st.columns(3)

col1.metric("👨‍🎓 Total Students", total_students)
col2.metric("🏆 Highest Total", f"{highest_total:.0f}")
col3.metric("📊 Class Average", f"{class_average:.2f}")

col4, col5, col6 = st.columns(3)

col4.metric("✅ Passed Students", pass_count)
col5.metric("❌ Failed Students", fail_count)
col6.metric("📈 Pass Percentage", f"{pass_percentage:.2f}%")


# ==========================================
# 9. SUBJECT-WISE COMBINED GRAPH
# ==========================================

st.header("📚 Step 4: Subject-wise Performance Analysis")

subject_average = df[subject_columns].mean()

st.write("### 📊 Average Marks in All Subjects")

st.bar_chart(subject_average)

subject_avg_df = pd.DataFrame({
    "Subject": subject_average.index.str.title(),
    "Average Marks": subject_average.values.round(2)
})

st.write("### Subject-wise Average Details")

st.dataframe(
    subject_avg_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 10. PASS / FAIL ANALYSIS
# ==========================================

st.header("✅ Step 5: Pass / Fail Analysis")

result_counts = df["Result"].value_counts()

st.bar_chart(result_counts)

col1, col2 = st.columns(2)

col1.metric("✅ Passed", pass_count)
col2.metric("❌ Failed", fail_count)


# ==========================================
# 11. STUDENT RANKING
# ==========================================

st.header("🏆 Step 6: Student Ranking System")

top_student = df.loc[df["Average"].idxmax()]

st.success(
    f"🥇 Top Performer: {top_student['student']} | "
    f"Average: {top_student['Average']:.2f}"
)

st.write("### 🏅 Top Performing Students")

st.dataframe(
    display_df[["student", "Total", "Average", "Result", "Rank"]],
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 12. NEW STUDENT PERFORMANCE PREDICTION
# ==========================================

st.header("🔮 Step 7: New Student Performance Prediction")

st.write("Enter marks for all detected subjects.")

new_marks = {}

input_columns = st.columns(3)

for i, subject in enumerate(subject_columns):
    with input_columns[i % 3]:
        new_marks[subject] = st.text_input(
            f"📝 {subject.title()} Marks",
            placeholder="Enter marks (0-100)",
            key=f"prediction_{subject}"
        )

if st.button("🔮 Predict Average Marks"):

    try:
        if any(value.strip() == "" for value in new_marks.values()):
            st.error("Please enter marks in all subject boxes.")

        else:
            entered_marks = {
                subject: float(value)
                for subject, value in new_marks.items()
            }

            if not all(
                0 <= mark <= 100
                for mark in entered_marks.values()
            ):
                st.error("Marks must be between 0 and 100.")

            else:
                predicted_average = (
                    sum(entered_marks.values()) /
                    len(entered_marks)
                )

                st.success(
                    f"🎯 Predicted Average: {predicted_average:.2f}"
                )

                if predicted_average >= 75:
                    st.info("🌟 Excellent Performance!")

                elif predicted_average >= 50:
                    st.info("👍 Good Performance!")

                elif predicted_average >= 35:
                    st.warning("📚 Average Performance. Keep Practicing!")

                else:
                    st.error("⚠️ Needs Improvement. Keep Learning!")

                prediction_result = (
                    "Pass"
                    if all(mark >= pass_marks for mark in entered_marks.values())
                    else "Fail"
                )

                st.write(f"**Predicted Result:** {prediction_result}")

    except ValueError:
        st.error("Please enter valid numeric marks.")


# ==========================================
# 13. DOWNLOAD STUDENT REPORT
# ==========================================

st.header("📥 Step 8: Download Student Report")

report = display_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 Download Complete Student Report",
    data=report,
    file_name="student_performance_report.csv",
    mime="text/csv",
    use_container_width=True
)

st.success("✅ Your student report is ready!")


# ==========================================
# 14. STUDENT CONFIDENCE BUILDING
# ==========================================

st.header("💜 Step 9: Student Confidence Building")

st.write(
    "Get personalized study suggestions based on academic performance."
)

student_index = st.selectbox(
    "👩‍🎓 Select Student",
    range(len(df)),
    format_func=lambda i: str(df.iloc[i]["student"])
)

student_data = df.iloc[student_index]

average = student_data["Average"]

weak_subject = min(
    subject_columns,
    key=lambda subject: student_data[subject]
)

st.subheader(f"Hello, {student_data['student']}! 👋")

st.metric("📊 Your Average Marks", f"{average:.2f}")

st.write(
    f"📌 Subject to improve: **{weak_subject.title()}**"
)

if average >= 75:
    st.success(
        "🌟 Excellent work! Keep learning and believe in yourself!"
    )

elif average >= 50:
    st.info(
        "👍 Good effort! Regular practice will help you improve."
    )

elif average >= 35:
    st.warning(
        "💪 You can improve! Focus on your weak subject."
    )

else:
    st.info(
        "💜 Start with basic topics and keep practising."
    )


# ==========================================
# 15. PERSONALIZED STUDY SUGGESTIONS
# ==========================================

st.subheader("📚 Personalized Study Suggestions")

suggestions = {
    "maths": "Practice mathematical problems daily and revise formulas.",
    "science": "Understand science concepts and practise diagrams.",
    "english": "Read passages, learn new words and practise grammar.",
    "computer": "Practice programming and learn computer concepts.",
    "social": "Read important topics and revise key points regularly.",
    "physics": "Understand formulas and practise numerical problems.",
    "chemistry": "Learn chemical reactions and practise equations."
}

study_advice = suggestions.get(
    weak_subject,
    f"Revise {weak_subject.title()} regularly, practise questions "
    "and focus on difficult topics."
)

st.info(f"💡 {study_advice}")


# ==========================================
# 16. FOOTER
# ==========================================

st.divider()

st.markdown("""
<div style="
    background: linear-gradient(90deg, #6D28D9, #C026D3);
    padding: 22px;
    border-radius: 15px;
    text-align: center;
    color: white;
">
    <h3 style="color:white !important;">
        🎓 Student Performance Dashboard
    </h3>
    <p>Developed using Python, Pandas and Streamlit</p>
    <p>💜 Learn • Analyze • Improve • Succeed</p>
</div>
""", unsafe_allow_html=True)
