
import json
import requests
import streamlit as st
from pypdf import PdfReader

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="StudyPilot AI",
    page_icon="🎓",
    layout="wide"
)

MODEL = "qwen2.5:1.5b"
OLLAMA_URL = "http://localhost:11434/api/generate"

# ---------------- SESSION STATE ----------------

defaults = {
    "quiz_questions": [],
    "quiz_submitted": False,
    "study_result": "",
    "result_title": "",
    "quiz_topic": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- CUSTOM UI ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0b1020;
    color: #f1f5f9;
}
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
[data-testid="stSidebar"] {
    background-color: #111827;
}
div.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("🎓 StudyPilot AI")
    st.caption("Your personal AI study assistant")
    st.divider()

    st.markdown("### Learning tools")
    st.write("📚 Notes summarizer")
    st.write("🧠 Interactive quiz")
    st.write("📅 Study planner")
    st.write("💬 Doubt solver")
    st.write("📄 PDF reader")

    st.divider()
    st.caption("Powered by local Ollama AI")
    st.caption("No paid API required")

# ---------------- HEADER ----------------

st.title("Your learning, upgraded.")
st.write(
    "Transform your notes into summaries, "
    "quizzes and personalized study plans."
)

st.divider()

# ---------------- INPUTS ----------------

feature = st.selectbox(
    "Choose your learning mode",
    [
        "Summarize Notes",
        "Generate Quiz",
        "Create Study Plan",
        "Solve a Doubt"
    ]
)

topic = st.text_input(
    "Topic name",
    placeholder="Example: Python Loops or Quantum Physics"
)

notes = st.text_area(
    "Paste your notes or enter your question",
    placeholder="Enter your study material here...",
    height=180
)

uploaded_pdf = st.file_uploader(
    "Or upload a text-based PDF",
    type=["pdf"]
)

# ---------------- PDF EXTRACTION ----------------

pdf_text = ""

if uploaded_pdf is not None:
    try:
        reader = PdfReader(uploaded_pdf)

        if reader.is_encrypted:
            st.warning(
                "This PDF is password-protected. "
                "Please upload an unlocked PDF."
            )
        else:
            pages = []

            for page in reader.pages:
                pages.append(page.extract_text() or "")

            pdf_text = "\n\n".join(pages)

            if pdf_text.strip():
                st.success(
                    f"PDF loaded: {len(reader.pages)} pages"
                )
            else:
                st.warning(
                    "No selectable text found. "
                    "Scanned PDFs need OCR."
                )

    except Exception as error:
        st.error(f"Could not read PDF: {error}")

# PDF text takes priority when a readable PDF is uploaded.
if pdf_text.strip():
    source_text = pdf_text
else:
    source_text = notes

# ---------------- AI GENERATION ----------------

def generate_ai(prompt, json_mode=False):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    if json_mode:
        payload["format"] = "json"

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300
    )

    response.raise_for_status()

    data = response.json()
    answer = data.get("response", "").strip()

    if not answer:
        raise ValueError("The AI returned an empty response.")

    return answer


# ---------------- QUIZ VALIDATION ----------------

def validate_quiz(answer):
    data = json.loads(answer)

    questions = data.get("questions", [])

    if not isinstance(questions, list):
        raise ValueError("Invalid questions format.")

    valid = []

    for q in questions:
        if not isinstance(q, dict):
            continue

        question = q.get("question")
        options = q.get("options")
        correct = q.get("answer")
        explanation = q.get("explanation", "")

        if not isinstance(question, str) or not question.strip():
            continue

        if (
            not isinstance(options, list)
            or len(options) != 4
            or not all(
                isinstance(option, str) and option.strip()
                for option in options
            )
        ):
            continue

        if (
            not isinstance(correct, int)
            or isinstance(correct, bool)
            or not 0 <= correct < 4
        ):
            continue

        if not isinstance(explanation, str):
            explanation = ""

        valid.append({
            "question": question,
            "options": options,
            "answer": correct,
            "explanation": explanation
        })

    if not valid:
        raise ValueError(
            "No valid MCQs were returned. Please try again."
        )

    return valid


# ---------------- GENERATE BUTTON ----------------

if st.button("✨ Generate with AI", type="primary"):

    if not source_text.strip():
        st.warning("Please enter notes or upload a readable PDF.")

    else:
        # Limit input to avoid sending excessively large PDFs.
        material = source_text[:18000]

        if len(source_text) > 18000:
            st.info(
                "Only the first part of this large document "
                "will be used in this version."
            )

        if feature == "Generate Quiz":

            prompt = f"""
You are StudyPilot AI, a tutor for first-year college students.

Create 5 multiple-choice questions based on the material.

Return ONLY valid JSON in this format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "Explain the correct answer."
    }}
  ]
}}

Rules:
- Exactly 5 questions if possible.
- Exactly 4 options per question.
- answer must be an integer from 0 to 3.
- answer indicates the index of the correct option.
- Questions must be based on the provided material.
- Include an explanation for every answer.

Topic: {topic or "General"}

Study material:
{material}
"""

        else:
            task_prompts = {
                "Summarize Notes": (
                    "Summarize the material with headings, "
                    "important concepts, definitions and "
                    "simple bullet points."
                ),
                "Create Study Plan": (
                    "Create a realistic 7-day study plan. "
                    "Include daily topics, tasks and revision."
                ),
                "Solve a Doubt": (
                    "Explain the topic in simple English. "
                    "Give a beginner-friendly example and "
                    "explain difficult terms."
                )
            }

            prompt = f"""
You are StudyPilot AI, a helpful tutor for first-year students.

Topic: {topic or "General"}

Task:
{task_prompts[feature]}

Use clear headings and simple language.
Base the answer on the supplied material.

Study material:
{material}
"""

        with st.spinner("Your local AI tutor is working..."):

            try:
                answer = generate_ai(
                    prompt,
                    json_mode=(feature == "Generate Quiz")
                )

                if feature == "Generate Quiz":
                    questions = validate_quiz(answer)

                    for key in list(st.session_state.keys()):
                        if key.startswith("quiz_choice_"):
                            del st.session_state[key]

                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_topic = topic or "General"
                    st.session_state.study_result = ""
                    st.session_state.result_title = ""

                else:
                    st.session_state.study_result = answer
                    st.session_state.result_title = feature
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_submitted = False

            except requests.exceptions.ConnectionError:
                st.error(
                    "Ollama is not running. Open Ollama "
                    "and try again."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The AI took too long to respond. "
                    "Try shorter notes and retry."
                )

            except requests.exceptions.RequestException as error:
                st.error(f"AI request failed: {error}")

            except (ValueError, KeyError, TypeError):
                st.error(
                    "Could not process the AI response. "
                    "Please try again."
                )

            except json.JSONDecodeError:
                st.error(
                    "The AI did not return valid quiz JSON. "
                    "Please generate the quiz again."
                )

# ---------------- DISPLAY AI RESULT ----------------

if st.session_state.study_result:
    st.divider()
    st.subheader(
        f"📖 {st.session_state.result_title}"
    )
    st.markdown(st.session_state.study_result)

# ---------------- INTERACTIVE QUIZ ----------------

if st.session_state.quiz_questions:

    st.divider()
    st.header("🧠 Test Your Knowledge")

    questions = st.session_state.quiz_questions

    st.write(
        f"Topic: {st.session_state.quiz_topic} "
        f"• Questions: {len(questions)}"
    )

    with st.form("quiz_form"):

        for i, question in enumerate(questions):

            st.markdown(f"### Question {i + 1}")
            st.write(question["question"])

            st.radio(
                "Choose one answer",
                question["options"],
                index=None,
                key=f"quiz_choice_{i}"
            )

        submitted = st.form_submit_button(
            "✅ Submit Quiz",
            type="primary"
        )

    if submitted:

        unanswered = [
            i for i in range(len(questions))
            if st.session_state.get(f"quiz_choice_{i}") is None
        ]

        if unanswered:
            st.warning(
                f"{len(unanswered)} question(s) unanswered. "
                "Please answer every question."
            )
        else:
            st.session_state.quiz_submitted = True

    if st.session_state.quiz_submitted:

        score = 0

        for i, question in enumerate(questions):

            selected = st.session_state.get(
                f"quiz_choice_{i}"
            )

            correct_answer = question["options"][
                question["answer"]
            ]

            if selected == correct_answer:
                score += 1

        percentage = score / len(questions) * 100

        st.divider()
        st.subheader("🏆 Your Quiz Results")

        st.metric(
            "Final Score",
            f"{score}/{len(questions)}",
            f"{percentage:.0f}%"
        )

        if percentage >= 80:
            st.success("Excellent work! Keep it up.")
        elif percentage >= 50:
            st.info("Good effort. Review the explanations.")
        else:
            st.warning(
                "Keep practising and revise the topic again."
            )

        for i, question in enumerate(questions):

            selected = st.session_state.get(
                f"quiz_choice_{i}"
            )

            correct_answer = question["options"][
                question["answer"]
            ]

            st.markdown(
                f"**Question {i + 1}:** {question['question']}"
            )

            if selected == correct_answer:
                st.success(f"Correct: {correct_answer}")
            else:
                st.error(f"Your answer: {selected}")
                st.write(f"Correct answer: {correct_answer}")

            st.caption(
                "Explanation: " + question["explanation"]
            )

        if st.button("🔄 Generate Another Quiz"):

            for key in list(st.session_state.keys()):
                if key.startswith("quiz_choice_"):
                    del st.session_state[key]

            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False

            st.rerun()

# ---------------- FOOTER ----------------

st.divider()
st.caption(
    "StudyPilot AI | Built by Daksh Verma | "
    "Local AI • No paid API"
)
