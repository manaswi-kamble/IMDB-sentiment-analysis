import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Brainlox Course Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance the UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
    }
    .chat-message.user {
        background-color: #e6f3ff;
    }
    .chat-message.bot {
        background-color: #f8f9fa;
    }
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .message-content {
        flex: 1;
    }
    .thinking {
        display: inline-block;
        font-size: 1.2rem;
        margin-left: 1rem;
        color: #666;
    }
    .stTextInput > div > div > input {
        padding: 0.75rem;
    }
    .css-1cpxqw2 {
        display: flex;
        width: 100%;
        height: 3.5rem;
        padding: 0.75rem;
        background-color: white;
        border-radius: 0.5rem;
    }
    .powered-by {
        text-align: center;
        font-size: 0.8rem;
        color: #888;
        margin-top: 2rem;
    }
    .mistral-gradient {
        background: linear-gradient(90deg, #7928CA, #FF0080);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🧠 Brainlox Course Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Your AI guide to Brainlox technical courses</p>", unsafe_allow_html=True)
st.markdown("<p class='powered-by'>Powered by <span class='mistral-gradient'>Mistral AI</span></p>", unsafe_allow_html=True)

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:5000/api")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'thinking' not in st.session_state:
    st.session_state.thinking = False

# Sidebar for controls and info
with st.sidebar:
    st.image("https://brainlox.com/assets/img/brand/logo.svg", width=200)
    st.markdown("### About")
    st.markdown("""
    This AI assistant helps you explore technical courses available on Brainlox. 
    Ask questions about courses, topics, or get recommendations based on your interests.
    """)
    
    st.markdown("### Sample Questions")
    sample_questions = [
        "What Python courses are available?",
        "Tell me about machine learning courses",
        "What are the most popular web development courses?",
        "Which courses are good for beginners?",
        "What advanced courses do you recommend for data scientists?"
    ]
    
    for question in sample_questions:
        if st.button(question):
            st.session_state.messages.append({"role": "user", "content": question})
            st.session_state.thinking = True
            st.rerun()  # Updated from experimental_rerun
    
    # Add model selection
    st.markdown("### Model Settings")
    model_option = st.selectbox(
        "Select Mistral AI Model",
        ["mistral-large-latest", "mistral-medium", "mistral-small-latest"],
        index=0
    )
    
    if st.button("Reset Conversation", key="reset"):
        try:
            response = requests.post(f"{API_URL}/reset")
            if response.status_code == 200:
                st.session_state.messages = []
                st.success("Conversation reset successfully!")
                time.sleep(1)
                st.rerun()  # Updated from experimental_rerun
            else:
                st.error("Failed to reset conversation. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user">
            <img class="avatar" src="https://www.gravatar.com/avatar/{hash('user')%500}?s=200&d=identicon">
            <div class="message-content">
                {message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot">
            <img class="avatar" src="https://www.gravatar.com/avatar/{hash('assistant')%500}?s=200&d=identicon">
            <div class="message-content">
                {message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Input for user query
user_query = st.text_input("Ask about Brainlox courses:", key="user_input", placeholder="e.g., What Python courses are available?")

# Process the query when submitted
if user_query and not st.session_state.thinking:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.thinking = True
    st.rerun()  # Updated from experimental_rerun

# If thinking, show the thinking animation and get response
if st.session_state.thinking and st.session_state.messages:
    with st.spinner("Thinking..."):
        try:
            last_user_message = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), None)
            
            if last_user_message:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"query": last_user_message},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.messages.append({"role": "assistant", "content": data["response"]})
                else:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "I'm sorry, I encountered an error processing your request. Please try again."
                    })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"I'm sorry, I encountered an error: {str(e)}"
            })
        
        st.session_state.thinking = False
        st.rerun()  # Updated from experimental_rerun