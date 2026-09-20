import streamlit as st
import os
import json
import time
import textwrap
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


st.set_page_config(
    page_title="StudyBuddy AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "study_material" not in st.session_state:
    st.session_state.study_material = None

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "history" not in st.session_state:
    st.session_state.history = []

if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""

if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = ""

if "selected_difficulty" not in st.session_state:
    st.session_state.selected_difficulty = "Beginner"


# =========================================================
# HTML HELPER
# =========================================================

def render_html(content, container=None):
    """Render custom HTML without Markdown indentation turning it into a code block."""
    html = textwrap.dedent(content).strip()
    target = container if container is not None else st
    target.markdown(html, unsafe_allow_html=True)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =========================================================
   STUDYBUDDY AI — CLEAN, THEME-AWARE DESIGN
   Uses Streamlit theme variables so Light/Dark mode stays readable.
   ========================================================= */

:root {
    --sb-bg: var(--background-color);
    --sb-card: var(--secondary-background-color);
    --sb-text: var(--text-color);
    --sb-primary: var(--primary-color);
    --sb-border: rgba(127, 127, 127, 0.22);
    --sb-muted: color-mix(in srgb, var(--text-color) 62%, transparent);
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    border-right: 1px solid var(--sb-border);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--sb-text);
}

[data-testid="stSidebar"] hr {
    border-color: var(--sb-border);
    margin: 1.1rem 0;
}

/* Navigation radio */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 0.35rem;
}

[data-testid="stSidebar"] [role="radio"] {
    padding: 0.45rem 0.6rem;
    border-radius: 10px;
}

[data-testid="stSidebar"] [role="radio"]:hover {
    background: color-mix(in srgb, var(--sb-primary) 10%, transparent);
}

/* Hero */
.hero {
    position: relative;
    overflow: hidden;
    padding: 34px 36px;
    border-radius: 22px;
    margin-bottom: 26px;
    border: 1px solid color-mix(in srgb, var(--sb-primary) 28%, var(--sb-border));
    background:
        radial-gradient(circle at 92% 10%, color-mix(in srgb, var(--sb-primary) 22%, transparent), transparent 32%),
        linear-gradient(135deg, color-mix(in srgb, var(--sb-primary) 10%, var(--sb-card)), var(--sb-card));
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.08);
}

.hero::after {
    content: "";
    position: absolute;
    width: 180px;
    height: 180px;
    right: -65px;
    bottom: -95px;
    border-radius: 50%;
    background: color-mix(in srgb, var(--sb-primary) 13%, transparent);
}

.hero h1 {
    position: relative;
    z-index: 1;
    margin: 0 0 8px 0;
    font-size: clamp(2rem, 4vw, 2.8rem);
    letter-spacing: -0.03em;
}

.hero p {
    position: relative;
    z-index: 1;
    max-width: 720px;
    margin: 0;
    font-size: 1.02rem;
    line-height: 1.65;
    color: var(--sb-muted);
}

/* Stats */
.stat-card {
    min-height: 118px;
    padding: 22px 18px;
    border-radius: 18px;
    background: var(--sb-card);
    border: 1px solid var(--sb-border);
    text-align: center;
    box-shadow: 0 7px 24px rgba(0, 0, 0, 0.055);
    transition: transform 0.18s ease, border-color 0.18s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    border-color: color-mix(in srgb, var(--sb-primary) 38%, var(--sb-border));
}

.stat-number {
    color: var(--sb-primary);
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
}

.stat-label {
    margin-top: 9px;
    color: var(--sb-muted);
    font-size: 0.82rem;
    font-weight: 600;
}

/* Feature cards */
.feature-card {
    min-height: 158px;
    padding: 22px;
    border-radius: 18px;
    background: var(--sb-card);
    border: 1px solid var(--sb-border);
    box-shadow: 0 7px 24px rgba(0, 0, 0, 0.045);
}

.feature-card h3 {
    margin: 0 0 10px 0;
    font-size: 1.05rem;
}

.feature-card p {
    margin: 0;
    color: var(--sb-muted);
    line-height: 1.6;
}

/* Buttons */
.stButton > button {
    border-radius: 11px;
    border: 1px solid color-mix(in srgb, var(--sb-primary) 45%, var(--sb-border));
    font-weight: 700;
    min-height: 42px;
    transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 18px color-mix(in srgb, var(--sb-primary) 18%, transparent);
}

/* Inputs */
[data-baseweb="input"], [data-baseweb="select"] > div {
    border-radius: 10px;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 650;
}

/* Alerts */
.success-box {
    padding: 15px 17px;
    border-radius: 13px;
    background: color-mix(in srgb, #10b981 10%, var(--sb-card));
    border: 1px solid color-mix(in srgb, #10b981 35%, var(--sb-border));
    color: var(--sb-text);
}

.warning-box {
    padding: 15px 17px;
    border-radius: 13px;
    background: color-mix(in srgb, #f59e0b 10%, var(--sb-card));
    border: 1px solid color-mix(in srgb, #f59e0b 35%, var(--sb-border));
    color: var(--sb-text);
}

/* General readability */
[data-testid="stMetricValue"] {
    color: var(--sb-text);
}

[data-testid="stMetricLabel"] {
    color: var(--sb-muted);
}

[data-testid="stCaptionContainer"] {
    color: var(--sb-muted);
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# GEMINI GENERATION
# =========================================================

def generate_study_material(subject, topic, difficulty):

    prompt = f"""
You are StudyBuddy AI, an educational assistant.

Create study material for:

Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Return ONLY valid JSON.

Use this exact structure:

{{
    "title": "topic title",

    "simple_explanation": "2 to 4 short paragraphs explaining the topic simply",

    "quick_summary": [
        "point 1",
        "point 2",
        "point 3"
    ],

    "key_concepts": [
        "concept 1",
        "concept 2",
        "concept 3"
    ],

    "real_world_example": "one simple real-world example",

    "key_takeaways": [
        "takeaway 1",
        "takeaway 2",
        "takeaway 3"
    ],

    "quiz": [
        {{
            "question": "question",
            "options": {{
                "A": "option",
                "B": "option",
                "C": "option",
                "D": "option"
            }},
            "answer": "A",
            "explanation": "short explanation"
        }}
    ]
}}

Rules:

- Create exactly 5 quiz questions.
- Each question must have A, B, C and D.
- Do NOT include quiz questions inside the explanation.
- Do NOT include quiz answers anywhere outside the quiz section.
- Keep the explanation beginner-friendly.
- Avoid unnecessary technical complexity.
"""

    start_time = time.time()

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
    )

    generation_time = time.time() - start_time

    data = json.loads(response.text)

    return data, generation_time


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("🤖 StudyBuddy AI")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📚 Learn",
        "🧠 Quiz",
        "📊 Progress"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption("AI-powered learning companion")
st.sidebar.caption("Built with Python + Gemini + Streamlit")


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    render_html("""
    <div class="hero">

    <h1>🤖 StudyBuddy AI</h1>

    <p>
    Your personal AI-powered learning companion.
    Learn concepts, test your knowledge and track your progress.
    </p>

    </div>
    """)

    total_topics = len(st.session_state.history)
    total_quizzes = len(st.session_state.quiz_history)

    if total_quizzes > 0:
        average_score = sum(
            item["percentage"]
            for item in st.session_state.quiz_history
        ) / total_quizzes

        best_score = max(
            item["percentage"]
            for item in st.session_state.quiz_history
        )
    else:
        average_score = 0
        best_score = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-number">{total_topics}</div>
            <div class="stat-label">Topics Studied</div>
        </div>
        """)

    with col2:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-number">{total_quizzes}</div>
            <div class="stat-label">Quiz Attempts</div>
        </div>
        """)

    with col3:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-number">{average_score:.0f}%</div>
            <div class="stat-label">Average Score</div>
        </div>
        """)

    with col4:
        render_html(f"""
        <div class="stat-card">
            <div class="stat-number">{best_score:.0f}%</div>
            <div class="stat-label">Best Score</div>
        </div>
        """)

    st.markdown('<div style="height: 10px"></div>', unsafe_allow_html=True)

    st.subheader("🚀 What can you do?")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_html("""
        <div class="feature-card">

        <h3>📚 Learn</h3>

        <p>
        Enter any academic topic and get
        simple AI-generated study material.
        </p>

        </div>
        """)

    with col2:
        render_html("""
        <div class="feature-card">

        <h3>🧠 Practice</h3>

        <p>
        Test your understanding using
        automatically generated quizzes.
        </p>

        </div>
        """)

    with col3:
        render_html("""
        <div class="feature-card">

        <h3>📊 Track</h3>

        <p>
        Monitor your quiz performance
        and identify topics that need more practice.
        </p>

        </div>
        """)

    st.markdown("---")

    st.subheader("🕒 Recent Learning")

    if st.session_state.history:

        for item in reversed(st.session_state.history[-5:]):

            st.markdown(
                f"""
                **📚 {item['topic']}**
                
                Subject: {item['subject']}  
                Difficulty: {item['difficulty']}  
                Generated: {item['time']}
                """
            )

            st.markdown("---")

    else:

        st.info(
            "No learning activity yet. Go to **Learn** and generate your first topic."
        )


# =========================================================
# LEARN
# =========================================================

elif page == "📚 Learn":

    st.title("📚 Learn Something New")

    st.write(
        "Enter a topic and StudyBuddy will create personalized study material."
    )

    col1, col2 = st.columns(2)

    with col1:

        subject = st.selectbox(
            "📘 Subject",
            [
                "Computer Science",
                "Data Science",
                "Database Management",
                "Operating Systems",
                "Computer Networks",
                "Artificial Intelligence",
                "Machine Learning",
                "General"
            ]
        )

    with col2:

        difficulty = st.selectbox(
            "🎯 Difficulty",
            [
                "Beginner",
                "Intermediate",
                "Advanced"
            ]
        )

    topic = st.text_input(
        "🔎 Enter Topic",
        placeholder="Example: Operating System"
    )

    generate = st.button(
        "✨ Generate Study Material",
        use_container_width=True
    )

    if generate:

        if not topic.strip():

            st.warning("Please enter a topic first.")

        else:

            loading = st.empty()

            render_html(
                """
                <div class="success-box">
                🤖 <b>StudyBuddy AI is preparing your learning material...</b><br>
                Generating explanation, summary and quiz.
                </div>
                """,
                loading
            )

            try:

                data, generation_time = generate_study_material(
                    subject,
                    topic,
                    difficulty
                )

                st.session_state.study_material = data
                st.session_state.quiz = data.get("quiz", [])
                st.session_state.quiz_submitted = False
                st.session_state.score = 0

                st.session_state.selected_topic = topic
                st.session_state.selected_subject = subject
                st.session_state.selected_difficulty = difficulty

                st.session_state.history.append({
                    "topic": topic,
                    "subject": subject,
                    "difficulty": difficulty,
                    "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
                })

                loading.empty()

                st.success(
                    f"✅ Study material generated in {generation_time:.2f} seconds."
                )

            except Exception as e:

                loading.empty()

                st.error(
                    "❌ Something went wrong while generating the study material."
                )

                st.code(str(e))


    # -----------------------------------------------------
    # DISPLAY STUDY MATERIAL
    # -----------------------------------------------------

    if st.session_state.study_material:

        data = st.session_state.study_material

        st.markdown("---")

        st.header(
            f"📖 {data.get('title', st.session_state.selected_topic)}"
        )

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📚 Explanation",
                "⚡ Quick Summary",
                "🌍 Real World",
                "🎯 Key Takeaways"
            ]
        )

        with tab1:

            st.subheader("Simple Explanation")

            st.write(
                data.get(
                    "simple_explanation",
                    "No explanation available."
                )
            )

            st.subheader("🔑 Key Concepts")

            for concept in data.get("key_concepts", []):

                st.markdown(
                    f"- **{concept}**"
                )

        with tab2:

            st.subheader("Quick Summary")

            for point in data.get("quick_summary", []):

                st.markdown(
                    f"✅ {point}"
                )

        with tab3:

            st.subheader("🌍 Real-World Example")

            st.info(
                data.get(
                    "real_world_example",
                    "No example available."
                )
            )

        with tab4:

            st.subheader("🎯 Key Takeaways")

            for point in data.get("key_takeaways", []):

                st.markdown(
                    f"💡 {point}"
                )

        st.markdown("---")

        notes = f"""
StudyBuddy AI
=============

Topic: {st.session_state.selected_topic}
Subject: {st.session_state.selected_subject}
Difficulty: {st.session_state.selected_difficulty}

SIMPLE EXPLANATION
------------------
{data.get('simple_explanation', '')}

QUICK SUMMARY
-------------
"""

        for point in data.get("quick_summary", []):

            notes += f"\n- {point}"

        notes += "\n\nKEY CONCEPTS\n------------\n"

        for concept in data.get("key_concepts", []):

            notes += f"\n- {concept}"

        notes += "\n\nREAL WORLD EXAMPLE\n------------------\n"
        notes += data.get("real_world_example", "")

        notes += "\n\nKEY TAKEAWAYS\n-------------\n"

        for point in data.get("key_takeaways", []):

            notes += f"\n- {point}"

        st.download_button(
            "⬇️ Download Study Notes",
            data=notes,
            file_name=f"{topic.replace(' ', '_')}_StudyBuddy.txt",
            mime="text/plain"
        )


# =========================================================
# QUIZ
# =========================================================

elif page == "🧠 Quiz":

    st.title("🧠 Test Your Knowledge")

    if not st.session_state.quiz:

        st.info(
            "No quiz available yet. Go to **Learn** and generate study material first."
        )

    else:

        st.write(
            f"Topic: **{st.session_state.selected_topic}**"
        )

        st.write(
            f"Difficulty: **{st.session_state.selected_difficulty}**"
        )

        st.markdown("---")

        for i, question in enumerate(
            st.session_state.quiz
        ):

            st.subheader(
                f"Question {i + 1}"
            )

            st.write(
                question["question"]
            )

            options = question["options"]

            option_text = [
                f"A. {options['A']}",
                f"B. {options['B']}",
                f"C. {options['C']}",
                f"D. {options['D']}"
            ]

            st.radio(
                "Choose your answer",
                option_text,
                index=None,
                key=f"quiz_answer_{i}",
                label_visibility="collapsed"
            )

            st.markdown("")

        if not st.session_state.quiz_submitted:

            if st.button(
                "✅ Submit Quiz",
                use_container_width=True
            ):

                score = 0
                answered = 0

                for i, question in enumerate(
                    st.session_state.quiz
                ):

                    selected = st.session_state.get(
                        f"quiz_answer_{i}"
                    )

                    if selected:

                        answered += 1

                        selected_letter = selected[0]

                        if selected_letter == question["answer"]:

                            score += 1

                st.session_state.score = score
                st.session_state.quiz_submitted = True

                percentage = (
                    score / len(st.session_state.quiz)
                ) * 100

                st.session_state.quiz_history.append({

                    "topic":
                        st.session_state.selected_topic,

                    "subject":
                        st.session_state.selected_subject,

                    "difficulty":
                        st.session_state.selected_difficulty,

                    "score":
                        score,

                    "total":
                        len(st.session_state.quiz),

                    "percentage":
                        percentage,

                    "time":
                        datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        )
                })

                st.rerun()

        else:

            score = st.session_state.score
            total = len(st.session_state.quiz)

            percentage = (
                score / total
            ) * 100

            st.markdown("---")

            if percentage >= 80:

                st.success(
                    f"🏆 Excellent! You scored {score}/{total} ({percentage:.0f}%)."
                )

            elif percentage >= 50:

                st.info(
                    f"👍 Good attempt! You scored {score}/{total} ({percentage:.0f}%)."
                )

            else:

                st.warning(
                    f"📚 Keep practicing! You scored {score}/{total} ({percentage:.0f}%)."
                )

            st.subheader("📖 Answer Review")

            for i, question in enumerate(
                st.session_state.quiz
            ):

                correct = question["answer"]

                selected = st.session_state.get(
                    f"quiz_answer_{i}"
                )

                selected_letter = (
                    selected[0]
                    if selected
                    else None
                )

                if selected_letter == correct:

                    st.success(
                        f"Question {i + 1}: Correct ✅"
                    )

                else:

                    st.error(
                        f"Question {i + 1}: Incorrect ❌"
                    )

                st.write(
                    f"Correct Answer: **{correct}. "
                    f"{question['options'][correct]}**"
                )

                st.caption(
                    question.get(
                        "explanation",
                        ""
                    )
                )

            if st.button(
                "🔄 Retake Quiz",
                use_container_width=True
            ):

                st.session_state.quiz_submitted = False
                st.session_state.score = 0

                for i in range(len(st.session_state.quiz)):

                    key = f"quiz_answer_{i}"

                    if key in st.session_state:

                        del st.session_state[key]

                st.rerun()


# =========================================================
# PROGRESS
# =========================================================

elif page == "📊 Progress":

    st.title("📊 Your Learning Progress")

    st.write(
        "Track your learning activity and quiz performance."
    )

    total_topics = len(
        st.session_state.history
    )

    total_quizzes = len(
        st.session_state.quiz_history
    )

    if total_quizzes > 0:

        average_score = sum(
            item["percentage"]
            for item in st.session_state.quiz_history
        ) / total_quizzes

        best_score = max(
            item["percentage"]
            for item in st.session_state.quiz_history
        )

    else:

        average_score = 0
        best_score = 0


    # -----------------------------------------------------
    # TOP STATS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📚 Topics Studied",
            total_topics
        )

    with col2:

        st.metric(
            "🧠 Quiz Attempts",
            total_quizzes
        )

    with col3:

        st.metric(
            "🎯 Average Score",
            f"{average_score:.0f}%"
        )

    with col4:

        st.metric(
            "🏆 Best Score",
            f"{best_score:.0f}%"
        )


    st.markdown("---")


    # -----------------------------------------------------
    # SCORE TREND
    # -----------------------------------------------------

    st.subheader("📈 Quiz Performance")

    if st.session_state.quiz_history:

        chart_data = []

        for i, item in enumerate(
            st.session_state.quiz_history
        ):

            chart_data.append({
                "Attempt": i + 1,
                "Score (%)": item["percentage"]
            })

        import pandas as pd

        df = pd.DataFrame(chart_data)

        st.line_chart(
            df.set_index("Attempt")
        )

    else:

        st.info(
            "Complete a quiz to see your performance graph."
        )


    st.markdown("---")


    # -----------------------------------------------------
    # WEAK TOPICS
    # -----------------------------------------------------

    st.subheader("⚠️ Topics That Need More Practice")

    if st.session_state.quiz_history:

        topic_scores = {}

        for item in st.session_state.quiz_history:

            topic = item["topic"]

            if topic not in topic_scores:

                topic_scores[topic] = []

            topic_scores[topic].append(
                item["percentage"]
            )


        topic_average = []

        for topic, scores in topic_scores.items():

            avg = sum(scores) / len(scores)

            topic_average.append(
                {
                    "Topic": topic,
                    "Average Score": avg
                }
            )

        topic_average.sort(
            key=lambda x: x["Average Score"]
        )

        for item in topic_average[:3]:

            if item["Average Score"] < 60:

                st.warning(
                    f"⚠️ **{item['Topic']}** — "
                    f"Average score: "
                    f"{item['Average Score']:.0f}%"
                )

            else:

                st.info(
                    f"📘 **{item['Topic']}** — "
                    f"Average score: "
                    f"{item['Average Score']:.0f}%"
                )

    else:

        st.info(
            "Complete some quizzes to identify weak topics."
        )


    st.markdown("---")


    # -----------------------------------------------------
    # QUIZ HISTORY
    # -----------------------------------------------------

    st.subheader("📝 Quiz History")

    if st.session_state.quiz_history:

        for item in reversed(
            st.session_state.quiz_history
        ):

            st.markdown(
                f"""
                **📚 {item['topic']}**

                Score: **{item['score']}/{item['total']}**
                ({item['percentage']:.0f}%)

                Difficulty: {item['difficulty']}

                🕒 {item['time']}
                """
            )

            st.markdown("---")

    else:

        st.info(
            "No quiz attempts yet."
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "StudyBuddy AI • Learn smarter. Practice better. Track your progress."
)