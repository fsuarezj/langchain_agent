import streamlit as st
from streamlit_mermaid import st_mermaid
from langchain_agent.assistants.mock_assistant import MockAssistant
#from langchain_agent.tutorials.customer_support_bot1 import SupportBotIO1
from langchain_agent.tutorials.customer_support_bot2 import SupportBotIO2, State

#assistant = MockAssistant()
assistant = SupportBotIO2()

# Gets the graph mermaid based on the assistant and its state
@st.cache_data
def mermaid_graph(state: str):
    if state != "waiting_for_input":
        return assistant.get_diagram(state)
    else:
        return assistant.get_diagram("tools")

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
