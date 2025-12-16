import streamlit as st
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# ======================================================
# Load Environment Variables
# ======================================================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# ======================================================
# Streamlit Config
# ======================================================
st.set_page_config(
    page_title="Incident Management Chatbot",
    page_icon="💬",
    layout="centered"
)

st.markdown("## 💬 Incident Management Chatbot")
st.caption("FAQs • Walkthroughs • RCA • Smart Chat")

# ======================================================
# Initialize AI (SAFE)
# ======================================================
llm = None
if API_KEY:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=API_KEY,
            temperature=0.3
        )
    except Exception:
        llm = None


def ai_answer(question: str) -> str:
    if not llm:
        return (
            "⚠️ AI service is not configured.\n\n"
            "You can continue using menu options below."
        )
    try:
        prompt = f"""
        You are an Incident Management assistant.
        Explain clearly in simple bullet points.

        Question:
        {question}
        """
        return llm.invoke(prompt).content
    except Exception:
        return (
            "⚠️ AI service is temporarily unavailable.\n\n"
            "Please try again later or use the menu."
        )


def ai_rca(desc: str) -> str:
    if not llm:
        return (
            "⚠️ AI RCA service is not available.\n\n"
            "Please submit RCA manually in the application."
        )
    try:
        prompt = f"""
        You are a healthcare incident RCA assistant.
        Provide 3–5 probable root causes in bullet points.

        Incident Description:
        {desc}
        """
        return llm.invoke(prompt).content
    except Exception:
        return (
            "⚠️ AI RCA service is temporarily unavailable.\n\n"
            "Please try again later."
        )

# ======================================================
# Session State
# ======================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = "MAIN_MENU"

if "temp" not in st.session_state:
    st.session_state.temp = {}

if "incidents" not in st.session_state:
    st.session_state.incidents = {}

# ======================================================
# UI Content
# ======================================================
def main_menu():
    return (
        "🏠 **Main Menu**\n\n"
        "1️⃣ Report Incident\n"
        "2️⃣ View My Incidents\n"
        "3️⃣ RCA Assistance\n"
        "4️⃣ FAQs & Help\n\n"
        "_Reply with a number OR ask any question_"
    )


def faq_list():
    return (
        "❓ **FAQs**\n\n"
        "1️⃣ How to report a new incident?\n"
        "2️⃣ What incident categories are available?\n"
        "3️⃣ How do I add incident details?\n"
        "4️⃣ How can I upload photos/documents?\n"
        "5️⃣ How to check the status of a reported incident?\n"
        "6️⃣ Who is assigned to my incident?\n"
        "7️⃣ How to view RCA details?\n"
        "8️⃣ What does each incident status mean?\n"
        "9️⃣ How long does incident resolution usually take?\n"
        "🔟 Whom to contact for urgent incidents?"
    )


def walkthrough_reporting():
    return (
        "📝 **Incident Reporting Walkthrough**\n\n"
        "• Select Report Incident\n"
        "• Choose incident type\n"
        "• Enter description\n"
        "• Add location/date/time\n"
        "• Submit & receive Incident ID"
    )


def walkthrough_rca():
    return (
        "🧠 **RCA Assistance Walkthrough**\n\n"
        "• Select RCA Assistance\n"
        "• AI suggests causes\n"
        "• Review / edit RCA\n"
        "• Submit for review"
    )


def generate_incident_id():
    return f"INC-{str(uuid.uuid4().int)[:4]}"


def incident_card(iid, inc):
    return (
        f"🧾 **Incident ID:** `{iid}`\n\n"
        f"• Category: {inc['category']}\n"
        f"• Status: {inc['status']}\n"
        f"• Assigned: {inc['assigned']}\n"
        f"• Reported On: {inc['date']}"
    )

# ======================================================
# Display Chat History
# ======================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ======================================================
# Chat Input
# ======================================================
user_input = st.chat_input("Type here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # ================= MAIN MENU =================
    if st.session_state.step == "MAIN_MENU":

        if user_input.isdigit():
            if user_input == "1":
                reply = "📂 **Enter Incident Category**"
                st.session_state.step = "INC_CATEGORY"

            elif user_input == "2":
                reply = "🔍 **Enter Incident ID**"
                st.session_state.step = "VIEW_INCIDENT"

            elif user_input == "3":
                reply = "🧠 **Describe the incident for RCA**"
                st.session_state.step = "RCA_AI"

            elif user_input == "4":
                reply = faq_list()
                st.session_state.step = "FAQ_MENU"

            else:
                reply = main_menu()

        else:
            reply = (
                "ℹ️ **Here’s what I found:**\n\n"
                f"{ai_answer(user_input)}\n\n"
                + main_menu()
            )

    # ================= REPORT INCIDENT =================
    elif st.session_state.step == "INC_CATEGORY":
        st.session_state.temp["category"] = user_input
        reply = "📝 **Enter Incident Description**"
        st.session_state.step = "INC_DESC"

    elif st.session_state.step == "INC_DESC":
        iid = generate_incident_id()
        st.session_state.incidents[iid] = {
            "category": st.session_state.temp["category"],
            "description": user_input,
            "status": "Reported",
            "assigned": "Safety Team",
            "date": datetime.now().strftime("%d-%m-%Y %H:%M")
        }
        reply = (
            "✅ **Incident Created Successfully**\n\n"
            f"🆔 Incident ID: `{iid}`\n\n"
            + main_menu()
        )
        st.session_state.step = "MAIN_MENU"
        st.session_state.temp = {}

    # ================= VIEW INCIDENT =================
    elif st.session_state.step == "VIEW_INCIDENT":
        inc = st.session_state.incidents.get(user_input)
        if inc:
            reply = incident_card(user_input, inc) + "\n\n" + main_menu()
        else:
            reply = "❌ Incident not found\n\n" + main_menu()
        st.session_state.step = "MAIN_MENU"

    # ================= RCA =================
    elif st.session_state.step == "RCA_AI":
        reply = (
            "🤖 **AI RCA Suggestions**\n\n"
            f"{ai_rca(user_input)}\n\n"
            "✅ RCA submitted\n\n"
            + main_menu()
        )
        st.session_state.step = "MAIN_MENU"

    # ================= FAQ =================
    elif st.session_state.step == "FAQ_MENU":

        if user_input.isdigit():
            faq_answers = {
                "1": walkthrough_reporting(),
                "2": "Medication Error, Equipment Failure, Patient Fall, Safety Hazard",
                "3": "You can add description, location, date and time during reporting.",
                "4": "Attachments can be uploaded in the main application.",
                "5": "Use View My Incidents and enter Incident ID.",
                "6": "Assigned person is visible in incident details.",
                "7": walkthrough_rca(),
                "8": "Reported → In Progress → RCA Pending → Closed",
                "9": "Usually resolved within 24–72 hours.",
                "10": "Contact Safety Officer or Admin for urgent incidents."
            }
            reply = faq_answers.get(user_input, faq_list()) + "\n\n" + main_menu()

        else:
            reply = (
                "ℹ️ **Here’s what I found:**\n\n"
                f"{ai_answer(user_input)}\n\n"
                + main_menu()
            )

        st.session_state.step = "MAIN_MENU"

    # ================= BOT RESPONSE =================
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()

# ======================================================
# Initial Message
# ======================================================
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": main_menu()
    })
    st.rerun()
