import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo"
if "client" not in st.session_state:
    st.session_state.client = None

# Sidebar for configuration
with st.sidebar:
    st.title("🤖 AI Chatbot Settings")
    
    # API key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="Enter your OpenAI API key",
        help="Get your API key from https://platform.openai.com/account/api-keys"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        # Initialize OpenAI client with the API key
        st.session_state.client = OpenAI(api_key=api_key)
    
    # Model selection
    model = st.selectbox(
        "Select Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        index=0
    )
    st.session_state.model = model
    
    # Chat controls
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Export chat
    if st.button("Export Chat"):
        if st.session_state.messages:
            chat_data = {
                "exported_at": datetime.now().isoformat(),
                "model": st.session_state.model,
                "messages": st.session_state.messages
            }
            st.download_button(
                label="Download Chat JSON",
                data=json.dumps(chat_data, indent=2),
                file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This is an AI-powered chatbot built with Streamlit.
    Enter your OpenAI API key to start chatting!
    """)

# Main chat interface
st.title("🤖 AI Chatbot")
st.markdown("Chat with an AI assistant powered by OpenAI")

# Display chat messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Function to get AI response
def get_ai_response(messages, model="gpt-3.5-turbo"):
    try:
        if st.session_state.client is None:
            return "❌ Error: Please enter your OpenAI API key in the sidebar."
        
        response = st.session_state.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        error_message = str(e)
        if "authentication" in error_message.lower():
            return "❌ Error: Invalid API key. Please check your API key in the sidebar."
        elif "rate limit" in error_message.lower():
            return "❌ Error: Rate limit exceeded. Please try again later."
        elif "connection" in error_message.lower():
            return "❌ Error: Connection error. Please check your internet connection."
        else:
            return f"❌ Error: {error_message}"

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Check if API key is provided
    if not st.session_state.api_key:
        st.error("Please enter your OpenAI API key in the sidebar to start chatting.")
        st.stop()
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
    
    # Get and display AI response
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Prepare messages for API (last 10 messages to manage context length)
                recent_messages = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
                
                # Convert to API format
                api_messages = [{"role": msg["role"], "content": msg["content"]} for msg in recent_messages]
                
                response = get_ai_response(api_messages, st.session_state.model)
                
                # Display response
                st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Instructions for first-time users
if not st.session_state.messages:
    st.info("👋 Welcome! Enter your OpenAI API key in the sidebar and start chatting!")

# Display chat statistics in sidebar
if st.session_state.messages:
    with st.sidebar:
        st.divider()
        user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
        assistant_messages = len([msg for msg in st.session_state.messages if msg["role"] == "assistant"])
        
        st.metric("User Messages", user_messages)
        st.metric("AI Responses", assistant_messages)

# Custom CSS for better styling
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] {
        font-size: 16px;
        line-height: 1.5;
    }
    
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)