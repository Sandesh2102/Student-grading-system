import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grading App", layout="wide")

# Initialize session state
if "students" not in st.session_state:
    st.session_state.students = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "student_name": "",
        "dbms_score": 0.0,
        "dm_score": 0.0,
        "os_score": 0.0,
        "se_score": 0.0,
        "befa_score": 0.0,
    }

# Grading logic
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    else:
        return "F"

st.title("📊 Student Grading System ")
st.caption("Manage student records, calculate grades, and track performance.")

tab1, tab2, tab3 = st.tabs(["➕ Add / Edit Student", "📁 Upload CSV", "📋 Student Records"])

# Tab 1: Add / Edit Student
with tab1:
    with st.form("student_form"):
        st.subheader("Enter Student Details")

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("👤 Student Name", value=st.session_state.form_data["student_name"])
        with col2:
            st.markdown("### ")

        st.markdown("#### 📝 Subject Scores (0-100)")
        c1, c2, c3 = st.columns(3)
        dbms_score = c1.number_input("Database Management Systems", 0.0, 100.0, step=1.0, value=st.session_state.form_data["dbms_score"])
        dm_score = c2.number_input("Discrete Maths", 0.0, 100.0, step=1.0, value=st.session_state.form_data["dm_score"])
        os_score = c3.number_input("Operating Systems", 0.0, 100.0, step=1.0, value=st.session_state.form_data["os_score"])

        c4, c5 = st.columns(2)
        se_score = c4.number_input("Software Engineering", 0.0, 100.0, step=1.0, value=st.session_state.form_data["se_score"])
        befa_score = c5.number_input("BEFA", 0.0, 100.0, step=1.0, value=st.session_state.form_data["befa_score"])

        submit = st.form_submit_button("✅ Update" if st.session_state.edit_index is not None else "➕ Add")

        if submit:
            if not student_name.strip():
                st.error("Student name cannot be empty.")
            else:
                total = dbms_score + dm_score + os_score + se_score + befa_score
                percentage = total / 5
                grade = calculate_grade(percentage)
                data = {
                    "Name": student_name,
                    "Database Management Systems": dbms_score,
                    "Discrete Maths": dm_score,
                    "Operating Systems": os_score,
                    "Software Engineering": se_score,
                    "BEFA": befa_score,
                    "Total Marks": total,
                    "Percentage": round(percentage, 2),
                    "Grade": grade,
                }

                if st.session_state.edit_index is not None:
                    st.session_state.students[st.session_state.edit_index] = data
                    st.session_state.edit_index = None
                    st.success(f"Updated {student_name}")
                else:
                    st.session_state.students.append(data)
                    st.success(f"Added {student_name}")

                # Reset form
                st.session_state.form_data = {
                    "student_name": "",
                    "dbms_score": 0.0,
                    "dm_score": 0.0,
                    "os_score": 0.0,
                    "se_score": 0.0,
                    "befa_score": 0.0,
                }
                st.rerun()

# Tab 2: Upload CSV
with tab2:
    st.subheader("📤 Upload Student CSV File")
    file = st.file_uploader("Upload CSV with columns: Name, Database Management Systems, Discrete Maths, Operating Systems, Software Engineering, BEFA", type="csv")
    if file:
        try:
            df = pd.read_csv(file)
            required = ["Name", "Database Management Systems", "Discrete Maths", "Operating Systems", "Software Engineering", "BEFA"]
            if all(col in df.columns for col in required):
                for _, row in df.iterrows():
                    if row["Name"].strip() == "":
                        continue
                    scores = [row[col] for col in required[1:]]
                    if any(s < 0 or s > 100 for s in scores):
                        continue
                    total = sum(scores)
                    percentage = total / 5
                    grade = calculate_grade(percentage)
                    student_data = {
                        "Name": row["Name"],
                        "Database Management Systems": row["Database Management Systems"],
                        "Discrete Maths": row["Discrete Maths"],
                        "Operating Systems": row["Operating Systems"],
                        "Software Engineering": row["Software Engineering"],
                        "BEFA": row["BEFA"],
                        "Total Marks": total,
                        "Percentage": round(percentage, 2),
                        "Grade": grade,
                    }
                    st.session_state.students.append(student_data)
                st.success("CSV uploaded successfully!")
                st.rerun()
            else:
                st.error("CSV missing required columns.")
        except Exception as e:
            st.error(f"Failed to process CSV: {e}")

# Tab 3: Records and Actions
with tab3:
    st.subheader("📚 Student Records")
    search = st.text_input("🔍 Search Student by Name")

    filtered = [s for s in st.session_state.students if search.lower() in s["Name"].lower()] if search else st.session_state.students

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Students", len(st.session_state.students))
    col2.metric("📈 Average %", round(sum(s["Percentage"] for s in st.session_state.students) / len(st.session_state.students), 2) if st.session_state.students else 0)
    col3.metric("🎓 Grades A+ / A / B", f"{sum(1 for s in st.session_state.students if s['Grade'] in ['A+', 'A', 'B'])}")

    if filtered:
        df = pd.DataFrame(filtered)

        for i, student in enumerate(filtered):
            with st.container():
                cols = st.columns([4, 1, 1])
                with cols[0]:
                    st.markdown(f"**{student['Name']}** | {student['Percentage']}% | Grade: **{student['Grade']}**")
                with cols[1]:
                    if st.button("✏️ Edit", key=f"edit_{i}"):
                        st.session_state.edit_index = st.session_state.students.index(student)
                        st.session_state.form_data = {
                            "student_name": student["Name"],
                            "dbms_score": student["Database Management Systems"],
                            "dm_score": student["Discrete Maths"],
                            "os_score": student["Operating Systems"],
                            "se_score": student["Software Engineering"],
                            "befa_score": student["BEFA"],
                        }
                        st.rerun()
                with cols[2]:
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        st.session_state.students.remove(student)
                        st.success(f"Deleted {student['Name']}")
                        st.rerun()

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download CSV", data=csv, file_name="student_records.csv", mime="text/csv")

        if st.button("🧹 Clear All"):
            st.session_state.students = []
            st.session_state.edit_index = None
            st.session_state.form_data = {
                "student_name": "",
                "dbms_score": 0.0,
                "dm_score": 0.0,
                "os_score": 0.0,
                "se_score": 0.0,
                "befa_score": 0.0,
            }
            st.success("Cleared all records!")
            st.rerun()
    else:
        st.info("No student records found. Add or upload to begin.")
# 📘 Instructions Section
with st.expander("ℹ️ How to Use This App", expanded=False):
    st.markdown("""
### 🧭 Instructions

Welcome to the **Student Grading System**! Here's how you can use the app:

#### ➕ Add / Edit Student
- Navigate to the **"Add / Edit Student"** tab.
- Enter the student's name and their scores for each subject.
- Press **Add** to save the record.
- To update, click **✏️ Edit** in the records list, update the details, and press **Update**.

#### 📁 Upload CSV
- Go to the **"Upload CSV"** tab.
- Upload a CSV with the following columns:
  - `Name`, `Database Management Systems`, `Discrete Maths`, `Operating Systems`, `Software Engineering`, `BEFA`
- Valid rows will be added automatically.
- Score values must be between **0–100**.

#### 📋 Student Records
- View all student records here.
- Use the search box to filter by student name.
- Click **✏️ Edit** to modify a student.
- Click **🗑️ Delete** to remove a student.
- Use **⬇️ Download CSV** to export records.
- Press **🧹 Clear All** to reset all data.

#### 📊 Metrics
- Top shows quick stats:
  - Total students
  - Average percentage
  - Total high-grade performers (A+, A, B)

Enjoy managing your class easily with this grading app! 🎓
""")

