import streamlit as st
import os

from streamlit_mermaid import st_mermaid
from langchain_agent.assistants.base_assistant import BaseAssistant

@st.cache_resource
def load_assistant():
    return BaseAssistant()
assistant = load_assistant()
#assistant = SupportBotIO3()

# Gets the graph mermaid based on the assistant and its state
@st.cache_data
def mermaid_graph(state: str):
    if state != "waiting_for_input":
        return assistant.get_diagram(state)
    else:
        return assistant.get_diagram("sensitive_tools")

@st.cache_data
def update_json(json):
    if json:
        with st.expander("JSON Form"):
            st.write(json)

# Saves tm
@st.cache_data
def load_file(uploaded_file, filetype):
    temp_file = "temp.tmp"
    temp_path = os.path.join("cache", temp_file)
    # First save the file
    with open(temp_path, "wb") as file:
        file.write(uploaded_file.getvalue())
    # Then load the file in the assistant
    assistant.load_file(temp_path, filetype)
    return assistant.get_json_form()

st.title('Test LLM chat')

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
    json_form = load_file(uploaded_file, filetype)
    #st.write(assistant.whole_content())
    update_json(json_form)


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
    update_json(assistant.get_json_form())

# Display log on app rerun
with st.sidebar:
    st.header("State")
    st_mermaid(mermaid_graph(st.session_state.graph_state))
    if uploaded_file:
        with open("new_form.xlsx", "rb") as f:
            st.download_button("Download XLSForm", f, file_name="new_form.xlsx")
    costs = assistant.get_costs()
    if not costs.empty:
        st.bar_chart(costs, horizontal=True, x_label="Cost (USD)", y_label="Agents")
    st.subheader("Total cost: $" + str(round(sum(costs.to_list()),6)))# + " USD")

#for log_message in st.session_state.log:
    #st.sidebar.caption(log_message)
st.sidebar.caption(st.session_state.graph_state)
