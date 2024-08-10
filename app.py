import streamlit as st
from langchain_agent.assistants.mock_assistant import MockAssistant

st.title('Test LLM chat')
assistant = MockAssistant()

# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Hello"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display assistant response in chat message container
with st.chat_message("assistant"):
    response = st.write_stream(assistant.generate_stream_response(prompt))
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": response})