import streamlit as st
from streamlit_mermaid import st_mermaid
from langchain_agent.assistants.mock_assistant import MockAssistant
from langchain_agent.tutorials.customer_support_bot1 import SupportBotIO1

#assistant = MockAssistant()
assistant = SupportBotIO1()

st.title('Test LLM chat')

with st.sidebar:
    st.header("Log")
    st_mermaid(assistant.get_graph())

# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Init log
if "log" not in st.session_state:
    st.session_state.log = ["Jamonada"]

# Display chat messages on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display log on app rerun
for log_message in st.session_state.log:
    st.sidebar.caption(log_message)

# Accept user input
if prompt := st.chat_input("Hello"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display assistant response in chat message container
if prompt:
    with st.chat_message("assistant"):
        response = st.write_stream(assistant.generate_stream_response(prompt))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})