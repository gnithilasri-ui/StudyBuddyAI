import streamlit as st
import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyBuddy AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Gemini API key not found. Check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "study_material": None,
    "quiz": [],
    "quiz_submitted": False,
    "score": 0,
    "history": [],
    "page": "Dashboard",
    "total_quizzes": 0,
    "total_score": 0.0,
    "last_generation_time": 0.0,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.18);
    }

    .hero {
        padding: 28px;
        border-radius: 22px;
        border: 1px solid rgba(128,128,128,0.18);
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 17px;
        opacity: 0.7;
    }

    .stat-card {
        padding: 22px;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,0.18);
        min-height: 125px;
    }

    .stat-label {
        font-size: 14px;
        opacity: 0.65;
    }

    .stat-value {
        font-size: 32px;
        font-weight: 800;
        margin-top: 5px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .feature-card {
        padding: 20px;
        border-radius: 17px;
        border: 1px solid rgba(128,128,128,0.18);
        min-height: 150px;
    }

    .feature-icon {
        font-size: 28px;
    }

    .feature-title {
        font-size: 17px;
        font-weight: 700;
        margin-top: 8px;
    }

    .feature-text {
        font-size: 14px;
        opacity: 0.68;
        margin-top: 5px;
    }

    .topic-card {
        padding: 15px 18px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.15);
        margin-bottom: 10px;
    }

    .score-card {
        padding: 28px;
        border-radius: 20px;
        border: 1px solid rgba(128,128,128,0.2);
        text-align: center;
        margin: 20px 0;
    }

    .loading-box {
        padding: 15px 20px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.2);
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .app-footer {
        text-align: center;
        opacity: 0.55;
        margin-top: 40px;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# QUIZ FUNCTION
# ============================================================

def render_quiz():

    quiz = st.session_state.quiz

    if not quiz:

        st.info(
            "Generate study material first to create a quiz."
        )

        return

    st.subheader("🧠 Test Yourself")

    st.write(
        "Choose one answer for each question. "
        "Correct answers will be revealed only after submission."
    )

    for i, question in enumerate(quiz):

        st.markdown(
            f"### Question {i + 1}"
        )

        st.write(
            question.get(
                "question",
                ""
            )
        )

        options = question.get(
            "options",
            {}
        )

        option_list = [
            f"A) {options.get('A', '')}",
            f"B) {options.get('B', '')}",
            f"C) {options.get('C', '')}",
            f"D) {options.get('D', '')}"
        ]

        st.radio(
            "Select your answer:",
            option_list,
            index=None,
            key=f"quiz_answer_{i}",
            label_visibility="collapsed"
        )

        st.divider()

    if st.button(
        "🎯 Submit Quiz",
        use_container_width=True
    ):

        score = 0

        for i, question in enumerate(quiz):

            selected = st.session_state.get(
                f"quiz_answer_{i}"
            )

            correct = str(
                question.get("answer", "")
            ).upper()

            if selected:

                selected_letter = selected[0]

                if selected_letter == correct:
                    score += 1

        st.session_state.score = score

        st.session_state.total_quizzes += 1

        st.session_state.total_score += (
            score / len(quiz)
        )

        st.session_state.quiz_submitted = True

        st.rerun()

    # ========================================================
    # QUIZ RESULT
    # ========================================================

    if st.session_state.quiz_submitted:

        score = st.session_state.score

        percentage = round(
            (score / len(quiz)) * 100
        )

        st.markdown(
            f"""
            <div class="score-card">

            <h2>🎉 Quiz Completed</h2>

            <h1>{score} / {len(quiz)}</h1>

            <h2>{percentage}%</h2>

            </div>
            """,
            unsafe_allow_html=True
        )

        if score == len(quiz):

            st.success(
                "🏆 Perfect score! Excellent understanding."
            )

        elif score >= 3:

            st.info(
                "👍 Good job! Review the missed concepts."
            )

        else:

            st.warning(
                "📚 Review the study material and try again."
            )

        st.subheader("💡 Answer Review")

        for i, question in enumerate(quiz):

            selected = st.session_state.get(
                f"quiz_answer_{i}"
            )

            correct = str(
                question.get("answer", "")
            ).upper()

            if selected:

                selected_letter = selected[0]

                if selected_letter == correct:

                    st.success(
                        f"Question {i + 1}: Correct ✅"
                    )

                else:

                    st.error(
                        f"Question {i + 1}: Incorrect ❌"
                    )

            else:

                st.warning(
                    f"Question {i + 1}: Not answered ⚠️"
                )

            st.write(
                f"**Correct Answer:** {correct}"
            )

            st.caption(
                question.get(
                    "explanation",
                    ""
                )
            )


# ============================================================
# GENERATE STUDY MATERIAL
# ============================================================

def generate_study_material(topic=None):

    if topic is None:

        topic = st.session_state.get(
            "topic_input",
            ""
        ).strip()

    else:

        topic = topic.strip()

    subject = st.session_state.get(
        "subject_select",
        "Other"
    )

    difficulty = st.session_state.get(
        "difficulty_select",
        "Beginner"
    )

    if not topic:

        st.warning(
            "Please enter a topic first."
        )

        return

    # --------------------------------------------------------
    # Visible loading message
    # --------------------------------------------------------

    loading_box = st.empty()

    loading_box.markdown(
        """
        <div class="loading-box">
        🤖 <b>StudyBuddy AI is preparing your learning material...</b><br>
        <small>Generating explanation, summary and quiz.</small>
        </div>
        """,
        unsafe_allow_html=True
    )

    start_time = time.time()

    try:

        # ----------------------------------------------------
        # SHORT + SPEED OPTIMIZED PROMPT
        # ----------------------------------------------------

        prompt = f"""
Create a concise study package.

Subject: {subject}
Topic: {topic}
Level: {difficulty}

Return ONLY valid JSON.

Structure:

{{
"title": "short title",
"simple_explanation": "easy explanation in 2-4 short paragraphs",
"quick_summary": [
"point 1",
"point 2",
"point 3"
],
"real_world_example": "one simple practical example",
"key_concepts": [
{{"term":"concept","explanation":"short explanation"}},
{{"term":"concept","explanation":"short explanation"}},
{{"term":"concept","explanation":"short explanation"}}
],
"key_takeaways": [
"takeaway 1",
"takeaway 2",
"takeaway 3"
],
"quiz": [
{{
"question":"question",
"options":{{"A":"option","B":"option","C":"option","D":"option"}},
"answer":"A",
"explanation":"short explanation"
}},
{{
"question":"question",
"options":{{"A":"option","B":"option","C":"option","D":"option"}},
"answer":"B",
"explanation":"short explanation"
}},
{{
"question":"question",
"options":{{"A":"option","B":"option","C":"option","D":"option"}},
"answer":"C",
"explanation":"short explanation"
}},
{{
"question":"question",
"options":{{"A":"option","B":"option","C":"option","D":"option"}},
"answer":"D",
"explanation":"short explanation"
}},
{{
"question":"question",
"options":{{"A":"option","B":"option","C":"option","D":"option"}},
"answer":"A",
"explanation":"short explanation"
}}
]
}}

Rules:
- Exactly 5 quiz questions.
- Exactly 4 options per question.
- Only one correct option.
- Study material must NOT contain quiz questions or answers.
- Keep everything concise.
- Match the requested difficulty.
"""

        # ----------------------------------------------------
        # GEMINI REQUEST
        # ----------------------------------------------------

        response = client.models.generate_content(

            model="gemini-3.5-flash-lite",

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                max_output_tokens=2200,

                temperature=0.3
            )
        )

        # ----------------------------------------------------
        # PARSE RESPONSE
        # ----------------------------------------------------

        data = json.loads(
            response.text
        )

        # ----------------------------------------------------
        # SAVE DATA
        # ----------------------------------------------------

        st.session_state.study_material = data

        st.session_state.quiz = data.get(
            "quiz",
            []
        )

        st.session_state.quiz_submitted = False

        st.session_state.score = 0

        # ----------------------------------------------------
        # RESET OLD QUIZ ANSWERS
        # ----------------------------------------------------

        for i in range(10):

            key = f"quiz_answer_{i}"

            if key in st.session_state:

                del st.session_state[key]

        # ----------------------------------------------------
        # HISTORY
        # ----------------------------------------------------

        st.session_state.history.append(
            {
                "topic": topic,
                "subject": subject,
                "difficulty": difficulty
            }
        )

        # ----------------------------------------------------
        # GENERATION TIME
        # ----------------------------------------------------

        generation_time = round(
            time.time() - start_time,
            2
        )

        st.session_state.last_generation_time = (
            generation_time
        )

        st.session_state.page = "Learn"

        # Remove loading message
        loading_box.empty()

        st.success(
            f"✅ Study material generated in "
            f"{generation_time} seconds."
        )

    except json.JSONDecodeError:

        loading_box.empty()

        st.error(
            "⚠️ AI returned an unexpected response. "
            "Please try again."
        )

    except Exception as e:

        loading_box.empty()

        st.error(
            "⚠️ Gemini is temporarily unavailable. "
            "Please try again."
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🤖 StudyBuddy AI")

    st.caption(
        "Your personalized AI learning companion"
    )

    st.divider()

    if st.button(
        "🏠  Dashboard",
        use_container_width=True
    ):

        st.session_state.page = "Dashboard"

    if st.button(
        "📚  Learn",
        use_container_width=True
    ):

        st.session_state.page = "Learn"

    if st.button(
        "🧠  Quiz",
        use_container_width=True
    ):

        st.session_state.page = "Quiz"

    if st.button(
        "📊  Progress",
        use_container_width=True
    ):

        st.session_state.page = "Progress"

    st.divider()

    st.markdown("### ⚙️ Study Settings")

    st.selectbox(
        "📖 Subject",
        [
            "Computer Science",
            "Programming",
            "Data Science",
            "Artificial Intelligence",
            "Cybersecurity",
            "Mathematics",
            "Other"
        ],
        key="subject_select"
    )

    st.selectbox(
        "🎯 Difficulty",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ],
        key="difficulty_select"
    )

    st.divider()

    st.caption(
        "StudyBuddy AI"
    )

    st.caption(
        "Learn smarter. Learn personally."
    )


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    st.markdown(
        """
        <div class="hero">

        <div class="hero-title">
        👋 Welcome to StudyBuddy AI
        </div>

        <div class="hero-subtitle">
        Learn smarter with personalized AI-powered study support.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">🚀 Start Learning</div>',
        unsafe_allow_html=True
    )

    st.text_input(
        "What do you want to learn?",
        placeholder=(
            "Example: DBMS Normalization, "
            "Python Functions, Machine Learning..."
        ),
        key="topic_input"
    )

    if st.button(
        "✨ Generate Study Material",
        use_container_width=True
    ):

        generate_study_material()

    # ========================================================
    # STATS
    # ========================================================

    st.markdown(
        '<div class="section-title">📊 Your Learning Overview</div>',
        unsafe_allow_html=True
    )

    topics_count = len(
        st.session_state.history
    )

    quizzes = st.session_state.total_quizzes

    if quizzes > 0:

        avg_score = round(
            (
                st.session_state.total_score
                / quizzes
            ) * 100
        )

    else:

        avg_score = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="stat-card">
            <div class="stat-label">
            📚 Topics Studied
            </div>
            <div class="stat-value">
            {topics_count}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="stat-card">
            <div class="stat-label">
            🧠 Quizzes Completed
            </div>
            <div class="stat-value">
            {quizzes}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="stat-card">
            <div class="stat-label">
            🎯 Average Score
            </div>
            <div class="stat-value">
            {avg_score}%
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="stat-card">
            <div class="stat-label">
            🔥 Learning Sessions
            </div>
            <div class="stat-value">
            {topics_count}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # FEATURES
    # ========================================================

    st.markdown(
        '<div class="section-title">✨ What can StudyBuddy do?</div>',
        unsafe_allow_html=True
    )

    f1, f2, f3 = st.columns(3)

    with f1:

        st.markdown(
            """
            <div class="feature-card">

            <div class="feature-icon">
            📚
            </div>

            <div class="feature-title">
            AI Study Material
            </div>

            <div class="feature-text">
            Understand difficult topics through
            simple personalized explanations.
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with f2:

        st.markdown(
            """
            <div class="feature-card">

            <div class="feature-icon">
            🧠
            </div>

            <div class="feature-title">
            Interactive Quiz
            </div>

            <div class="feature-text">
            Test your understanding with
            AI-generated questions and scoring.
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with f3:

        st.markdown(
            """
            <div class="feature-card">

            <div class="feature-icon">
            📊
            </div>

            <div class="feature-title">
            Track Progress
            </div>

            <div class="feature-text">
            Monitor your learning activity
            and quiz performance.
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # RECENT LEARNING
    # ========================================================

    st.markdown(
        '<div class="section-title">🕘 Recent Learning</div>',
        unsafe_allow_html=True
    )

    if st.session_state.history:

        for item in reversed(
            st.session_state.history[-5:]
        ):

            st.markdown(
                f"""
                <div class="topic-card">

                📚 <b>{item['topic']}</b>

                &nbsp; • &nbsp;

                {item['subject']}

                &nbsp; • &nbsp;

                {item['difficulty']}

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "Your recent study topics will appear here."
        )


# ============================================================
# LEARN PAGE
# ============================================================

elif st.session_state.page == "Learn":

    st.title("📚 Learn")

    st.caption(
        "Generate personalized learning material using Gemini AI."
    )

    st.text_input(
        "Enter a topic",
        placeholder=(
            "Example: Operating System Process Scheduling"
        ),
        key="learn_topic"
    )

    if st.button(
        "✨ Generate",
        use_container_width=True
    ):

        generate_study_material(
            st.session_state.learn_topic
        )

    if st.session_state.study_material:

        data = st.session_state.study_material

        st.divider()

        st.header(
            data.get(
                "title",
                "Study Material"
            )
        )

        if st.session_state.last_generation_time:

            st.caption(
                f"⚡ Generated in "
                f"{st.session_state.last_generation_time} seconds"
            )

        tab1, tab2 = st.tabs(
            [
                "📚 Study Material",
                "🧠 Test Yourself"
            ]
        )

        with tab1:

            st.subheader(
                "📚 Simple Explanation"
            )

            st.write(
                data.get(
                    "simple_explanation",
                    ""
                )
            )

            st.subheader(
                "📝 Quick Summary"
            )

            for point in data.get(
                "quick_summary",
                []
            ):

                st.markdown(
                    f"• {point}"
                )

            st.subheader(
                "🌍 Real-World Example"
            )

            st.info(
                data.get(
                    "real_world_example",
                    ""
                )
            )

            st.subheader(
                "🔑 Key Concepts"
            )

            for concept in data.get(
                "key_concepts",
                []
            ):

                st.markdown(
                    f"**{concept.get('term', '')}** — "
                    f"{concept.get('explanation', '')}"
                )

            st.subheader(
                "💡 Key Takeaways"
            )

            for takeaway in data.get(
                "key_takeaways",
                []
            ):

                st.markdown(
                    f"✅ {takeaway}"
                )

            # ------------------------------------------------
            # DOWNLOAD NOTES
            # ------------------------------------------------

            notes = (
                "STUDYBUDDY AI\n"
                "====================\n\n"
            )

            notes += (
                f"TOPIC: "
                f"{data.get('title', '')}\n\n"
            )

            notes += (
                "SIMPLE EXPLANATION\n"
                "------------------\n"
            )

            notes += (
                data.get(
                    "simple_explanation",
                    ""
                )
            )

            notes += (
                "\n\nQUICK SUMMARY\n"
                "-------------\n"
            )

            for point in data.get(
                "quick_summary",
                []
            ):

                notes += f"\n• {point}"

            notes += (
                "\n\nREAL-WORLD EXAMPLE\n"
                "------------------\n"
            )

            notes += data.get(
                "real_world_example",
                ""
            )

            notes += (
                "\n\nKEY CONCEPTS\n"
                "------------\n"
            )

            for concept in data.get(
                "key_concepts",
                []
            ):

                notes += (
                    f"\n{concept.get('term', '')}: "
                    f"{concept.get('explanation', '')}"
                )

            notes += (
                "\n\nKEY TAKEAWAYS\n"
                "-------------\n"
            )

            for takeaway in data.get(
                "key_takeaways",
                []
            ):

                notes += f"\n• {takeaway}"

            st.download_button(
                "📥 Download Study Notes",
                notes,
                file_name="StudyBuddy_Notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        with tab2:

            render_quiz()


# ============================================================
# QUIZ PAGE
# ============================================================

elif st.session_state.page == "Quiz":

    st.title("🧠 Quiz Center")

    st.caption(
        "Test your understanding of your latest topic."
    )

    if st.session_state.quiz:

        render_quiz()

    else:

        st.info(
            "Generate study material first to unlock a quiz."
        )


# ============================================================
# PROGRESS PAGE
# ============================================================

elif st.session_state.page == "Progress":

    st.title("📊 Learning Progress")

    st.caption(
        "Your StudyBuddy learning activity."
    )

    topics_count = len(
        st.session_state.history
    )

    quizzes = st.session_state.total_quizzes

    if quizzes > 0:

        avg_score = round(
            (
                st.session_state.total_score
                / quizzes
            ) * 100
        )

    else:

        avg_score = 0

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "📚 Topics Studied",
            topics_count
        )

    with c2:

        st.metric(
            "🧠 Quizzes Completed",
            quizzes
        )

    with c3:

        st.metric(
            "🎯 Average Score",
            f"{avg_score}%"
        )

    st.divider()

    if st.session_state.history:

        st.subheader(
            "🕘 Study History"
        )

        for item in reversed(
            st.session_state.history
        ):

            st.write(
                f"📚 **{item['topic']}** — "
                f"{item['subject']} — "
                f"{item['difficulty']}"
            )

    else:

        st.info(
            "Start learning to build your progress history."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="app-footer">

    🤖 StudyBuddy AI
    • Personalized learning powered by Generative AI

    </div>
    """,
    unsafe_allow_html=True
)