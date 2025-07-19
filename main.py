# 📚 Study Tool with Aesthetic UI + Smart Features
import streamlit as st
import os
import json
import fitz  # PyMuPDF
from datetime import datetime
import random

# --- Setup ---
os.makedirs("summaries", exist_ok=True)
os.makedirs("tasks", exist_ok=True)

quotes = [
    "Study hard, for the well is deep, and our brains are shallow. – Richard Baxter",
    "The beautiful thing about learning is nobody can take it away from you. – B.B. King",
    "Education is the most powerful weapon you can use to change the world. – Nelson Mandela",
    "Push yourself, because no one else is going to do it for you.",
    "Dream big. Study smart. Work hard."
]

# --- Page Config ---
st.set_page_config(page_title="Smart Study Tool", layout="wide")
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');
    html, body, [class*='css']  {{ font-family: 'Quicksand', sans-serif; }}
    .stApp {{
        background-image: url('https://i.pinimg.com/originals/e0/fe/49/e0fe49f73302e6c98ac445b023d34b90.jpg');
        background-size: cover;
        background-attachment: fixed;
    }}
    .stTextArea > div > div > textarea {{
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    font-size: 16px;
    }}

    .stRadio > div {{
        background-color: rgba(255,255,255,0.6);
        padding: 5px;
        border-radius: 8px;
    }}
    .stDownloadButton {{
        color: white;
        background-color:grey;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("📂 Menu")
page = st.sidebar.radio("Navigate", ["📄 View Summaries", "➕ Upload & Quiz", "🗓 Task Planner"])

# --- Dynamic Quote ---
if 'quote' not in st.session_state:
    st.session_state['quote'] = random.choice(quotes)
if st.button("🔁 Inspire Me"):
    st.session_state['quote'] = random.choice(quotes)
st.success(f"💬 {st.session_state['quote']}")

# --- File Extractor ---
def extract_text(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# --- Save & Load ---
def save_summary(name, content):
    with open(f"summaries/{name}.txt", "w", encoding="utf-8") as f:
        f.write(content)

def load_summaries():
    return os.listdir("summaries")

def load_tasks():
    try:
        with open("tasks/tasks.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_tasks(data):
    with open("tasks/tasks.json", "w") as f:
        json.dump(data, f, indent=2)

# --- Fallback Quiz Generator ---
def generate_mcqs_from_text(text, num_questions=5):
    sentences = [s.strip() for s in text.split('.') if len(s.strip().split()) > 5]
    questions = []

    for i, sentence in enumerate(sentences[:num_questions]):
        words = sentence.split()
        if len(words) < 6:
            continue

        keyword = words[random.randint(2, len(words)-2)]
        question = sentence.replace(keyword, "")

        options = random.sample(words, 3)
        if keyword not in options:
            options.append(keyword)
        random.shuffle(options)

        questions.append({
            "question": f"Q{i+1}: {question}?",
            "options": options,
            "answer": keyword
        })

    return questions

# --- Page 1: View Summaries ---
if page == "📄 View Summaries":
    st.subheader("📂 Your Summaries")
    files = load_summaries()
    if files:
        query = st.text_input("🔍 Search Summaries")
        filtered = [f for f in files if query.lower() in f.lower()] if query else files
        selected = st.selectbox("Choose a file:", filtered)
        with open(f"summaries/{selected}", "r", encoding="utf-8") as f:
            st.text_area("📄 Content", f.read(), height=400)
    else:
        st.info("No summaries saved yet.")

# --- Page 2: Upload & Quiz ---
elif page == "➕ Upload & Quiz":
    tab1, tab2 = st.tabs(["📥 Upload", "🧠 Quiz"])

    with tab1:
        st.markdown("### Upload a File (.txt or .pdf)")
        file = st.file_uploader("Choose file", type=["txt", "pdf"])
        if file:
            text = file.read().decode("utf-8") if file.name.endswith(".txt") else extract_text(file)
            st.text_area("📖 File Content", text, height=300)

            style = st.selectbox("🖋 Summary Style", ["Normal", "Simplified", "Bullets"])
            name = st.text_input("Summary name", value="summary1")

            if st.button("💾 Save Summary"):
                summary = text[:1500] + "..." if len(text) > 1500 else text
                if style == "Simplified":
                    summary = "➤ " + summary.replace(". ", "\n➤ ")
                elif style == "Bullets":
                    summary = "\n• " + summary.replace(". ", "\n• ")
                save_summary(name, summary)
                st.success(f"✅ '{name}' saved.")
                st.download_button("📥 Download TXT", summary, file_name=f"{name}.txt")

    with tab2:
        st.markdown("### Auto Quiz from Uploaded File")
        quiz_file = st.file_uploader("Upload file for quiz", type=["txt", "pdf"], key="quiz_upload")
        if quiz_file:
            content = quiz_file.read().decode("utf-8") if quiz_file.name.endswith(".txt") else extract_text(quiz_file)
            mcqs = generate_mcqs_from_text(content)
            score = 0
            user_answers = {}

            if mcqs:
                with st.form("quiz_form"):
                    for idx, q in enumerate(mcqs):
                        user_answers[idx] = st.radio(q["question"], q["options"], key=f"q{idx}")
                    submitted = st.form_submit_button("✅ Submit Answers")

                if submitted:
                    for idx, q in enumerate(mcqs):
                        if user_answers.get(idx) == q["answer"]:
                            st.success(f"✅ Q{idx+1} Correct")
                            score += 1
                        else:
                            st.error(f"❌ Q{idx+1} Wrong. Correct: {q['answer']}")
                    st.info(f"🎯 Final Score: {score}/{len(mcqs)}")
            else:
                st.warning("⚠ Not enough valid sentences for quiz.")

# --- Page 3: Task Planner ---
elif page == "🗓 Task Planner":
    st.subheader("📝 Plan Your Study Tasks")
    tasks = load_tasks()

    with st.form("task_add", clear_on_submit=True):
        title = st.text_input("Task")
        due = st.date_input("Due Date")
        time = st.time_input("Due Time")
        submit = st.form_submit_button("➕ Add Task")
        if submit:
            if title.strip():
                due_str = datetime.combine(due, time).strftime("%Y-%m-%d %H:%M:%S")
                tasks.append({"task": title.strip(), "done": False, "due": due_str})
                save_tasks(tasks)
                st.success(f"Task '{title}' added.")
            else:
                st.error("Task title cannot be empty.")

    if not tasks:
        st.info("No tasks yet.")
    else:
        st.markdown("### 📋 Your Tasks")
        tasks = sorted(tasks, key=lambda x: x.get("due"))
        done = sum(t["done"] for t in tasks)
        st.progress(int((done / len(tasks)) * 100))
        for i, t in enumerate(tasks):
            cols = st.columns([4, 2, 2, 1, 1])
            with cols[0]:
                st.write(f"{'✅' if t['done'] else '⏳'} {t['task']}")
                st.caption(f"Due: {t['due']}")
            with cols[1]:
                if st.button(f"✅ Done {i}", key=f"done-{i}"):
                    tasks[i]['done'] = True
                    save_tasks(tasks)
                    st.rerun()
            with cols[2]:
                if st.button(f"❌ Delete {i}", key=f"del-{i}"):
                    tasks.pop(i)
                    save_tasks(tasks)
                    st.rerun()