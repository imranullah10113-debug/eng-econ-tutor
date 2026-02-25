import streamlit as st
from openai import OpenAI

# --- PAGE SETUP ---
st.set_page_config(page_title="Eng Econ Tutor", layout="wide")

st.title("📘 Engineering Economy Tutor")
st.caption("Based on Blank & Tarquin, 7th Edition")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Settings")
    
    # 1. Try to get Key from Streamlit Secrets (Best for deployment)
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        # 2. Fallback: Ask user to type it (Best for testing)
        api_key = st.text_input("Enter OpenAI API Key", type="password")
        if not api_key:
            st.warning("Please enter your API Key to proceed.")

    chapter = st.selectbox("Current Chapter / Topic", [
        "Ch 1-3: Foundations & Factors",
        "Ch 4-6: PW, FW, AW Analysis",
        "Ch 7-8: ROR & B/C Analysis",
        "Ch 11: Replacement Analysis",
        "Ch 16: Depreciation (SL, DDB, MACRS)",
        "Ch 17: After-Tax Analysis"
    ])
    
    mode = st.radio("Mode", ["Solve Problem Step-by-Step", "Check My Solution"])

# --- THE AI BRAIN (System Prompt) ---
system_instruction = f"""
ACT AS: Expert Engineering Economy Tutor (Blank & Tarquin 7th Ed).
TOPIC: {chapter}.
MODE: {mode}.

STRICT GUIDELINES:
1.  **Formulas:** Use Standard Factor Notation ONLY (e.g., (P/A, i, n)). 
2.  **Logic:** 
    - Step 1: List Variables (P, F, A, i, n).
    - Step 2: Describe Cash Flow Diagram textually.
    - Step 3: Write Equation with Factor Notation.
    - Step 4: Plug in Factor Value (simulate table lookup).
    - Step 5: Final Math.
3.  **Depreciation:** Differentiate clearly between Book Depreciation and Tax Depreciation. Use 'dt' notation.
4.  **Checking Work:** If user uploads a solution, identify the SPECIFIC error (e.g., "Wrong 'n' used").
"""

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready! Paste a problem or your solution."}]

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle New Input
if prompt := st.chat_input("Type here..."):
    
    # Check if key is present
    if not api_key:
        st.error("Missing API Key. Please enter it in the Sidebar.")
        st.stop()
        
    client = OpenAI(api_key=api_key)
    
    # Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI Response
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o", # Or gpt-3.5-turbo if you want cheaper/faster
            messages=[
                {"role": "system", "content": system_instruction},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ],
            stream=True
        )
        response = st.write_stream(stream)
    
    # Save Response
    st.session_state.messages.append({"role": "assistant", "content": response})
