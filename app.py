from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime  #Import datetime module

# Replace with your MongoDB connection string
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client['chatbot_db']
chat_collection = db["chat_history"]

def save_chat_history(user_message, bot_message):
    chat_collection.insert_one({
        "user_message": user_message,
        "bot_message": bot_message,
        "timestamp": datetime.utcnow(),
        "month": datetime.utcnow().strftime('%B')  # Store the month as a string
    })

def get_chat_history_for_current_month():
    current_month = datetime.utcnow().strftime('%B')
    return list(chat_collection.find({"month": current_month}, {"_id": 0, "user_message": 1, "bot_message": 1, "timestamp": 1}).sort("timestamp", -1))



st.set_page_config(page_title="AI-Chatbot", page_icon="🤖", layout="wide")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a specialist in agriculture. You have to suggest temperature, humidity, type of soil, mainly region in the world where the crop is cultivated when the user gives the crop name. If not the crop name, output should be 'Not a crop'"
)
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=False)
    return response

# Initialize Streamlit app
st.markdown("""
<style>
    .main {
        background-color: #f0f0f5;
        color: #333;
        padding: 2rem;
    }
    .header {
        font-size: 2rem;
        color: #007bff;
    }
    .logo {
        border-radius: 10px;
    }
    .button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1rem;
    }
    .button:hover {
        background-color: #0056b3;
    }
    .history {
        background-color: #fff;
        border: 1px solid #ddd;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Display the logo
logo_path = "./assets/homepage-bot.png"
st.image(logo_path, width=200, output_format="PNG", caption="AI Chatbot")

st.markdown('<div class="header">Chatbot using GEMINI by AiDevops-squad</div>', unsafe_allow_html=True)

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

col1, col2 = st.columns([3, 1])

with col1:
    prompt = st.text_input("Prompt: ", key="prompt", placeholder="Enter crop name here...")
    
with col2:
    submit = st.button("Ask the question", key="submit", help="Click to get a response")

if submit and prompt:
    response = get_gemini_response(prompt)
    response_text = "".join(chunk.text for chunk in response)
    # Add user query and response to session state chat history
    st.session_state['chat_history'].append(("User", prompt))
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("Bot", chunk.text))
    save_chat_history(prompt, response_text)

# Add a collapsible chat history section to the sidebar
st.sidebar.header("ChatBot 🤖")
with st.sidebar:
    with st.expander("Chat History"):
        chat_history = get_chat_history_for_current_month()
        if chat_history:
            for entry in chat_history:
                user_message = entry.get('user_message', 'No user message')
                bot_message = entry.get('bot_message', 'No bot message')
                timestamp = entry.get('timestamp', 'No timestamp')
                st.write(f"User input: {user_message}")
                st.write(f"Bot response: {bot_message}")
                st.write(f"Date : {timestamp}")
                st.write("---")
        else:
            st.write("No chat history for the current month.")


# Add a new feature as per your requirement:
st.sidebar.subheader("Instructions")
st.sidebar.markdown("""
You are a specialist in agriculture. You have to suggest temperature, humidity, type of soil, mainly region in the world where the crop is cultivated when the user gives the crop name. If not the crop name, output should be 'Not a crop'.
""")