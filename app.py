import streamlit as st
import os

from streamlit_mermaid import st_mermaid
from langchain_agent.assistants.base_assistant import BaseAssistant

assistant = BaseAssistant()
#assistant = SupportBotIO3()

# Gets the graph mermaid based on the assistant and its state
@st.cache_data
def mermaid_graph(state: str):
    if state != "waiting_for_input":
        return assistant.get_diagram(state)
    else:
        return assistant.get_diagram("sensitive_tools")

@st.cache_data
def save_tmp_file(uploaded_file):
    temp_file = "temp.tmp"
    temp_path = os.path.join("cache", temp_file)
    with open(temp_path, "wb") as file:
        file.write(uploaded_file.getvalue())
    return temp_path

st.title('Test LLM chat')

#if st.session_state == None:
    #print("Iniciando State")
    #st.session_state = State()

# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Init log
if "log" not in st.session_state:
    st.session_state.log = ["Jamonada"]

if "graph_state" not in st.session_state:
    st.session_state.graph_state = "__start__"

# Upload file
uploaded_file = st.file_uploader("Upload your survey", type=['pdf', 'docx'])
if uploaded_file:
    print(f"Filetype: {uploaded_file.type}")
    filetype = uploaded_file.type.split("/")[1]
    tmp_file = save_tmp_file(uploaded_file)
    assistant.load_file(tmp_file, filetype)
    st.write(assistant.get_page(0))
    #stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    #st.write(stringio)
    #string_data = stringio.read()
    #st.write(string_data)

# Display chat messages on app rerun
for message in st.session_state["messages"]:
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
if prompt:
    with st.chat_message("assistant"):
        response = st.write_stream(assistant.generate_stream_response(prompt, st.session_state))
        #st.session_state.graph_state = state_aux[0]
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display log on app rerun
with st.sidebar:
    st.header("State")
    st_mermaid(mermaid_graph(st.session_state.graph_state))

#for log_message in st.session_state.log:
    #st.sidebar.caption(log_message)
st.sidebar.caption(st.session_state.graph_state)
