from .assistance_interface import AssistantInterface
from .helping_features.files_manager import FilesManager

from .base_state import BaseState
from .form_loader import FormLoader
from .form_parser import FormParser
from .orchestrator import Orchestrator
from .form_expert import FormExpert

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
import uuid
import functools
import types

class BaseAssistant(AssistantInterface, FilesManager):
    def __init__(self):
        load_dotenv()
        super().__init__()
        self._graph = self._init_graph()
        self._unthemed_diagram = self._set_diagram()
        self._config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
            }
        }
        self._graph.update_state(self._config, {
            "parsed_questionnaire": False
        })
    
    def load_file(self, file, filetype) -> None:
        super().load_file(file, filetype)
        print("Loading file")
        self._graph.update_state(self._config, {
            "messages": self._graph.get_state(self._config).values["messages"],
            "source_questionnaire": self.whole_content(),
            "parsed_questionnaire": False
        })
        parser = FormParser()
        new_state = parser(self._graph.get_state(self._config).values, self._config)
        print("PARSED IS")
        print(new_state)
        self._graph.update_state(self._config, new_state)
    
    def _route(self, state):
        print("DECIDING:")
        #print(self._get_state())
        if self._document_loaded and not self._get_state().values["parsed_questionnaire"]:
            print("Going to parser")
            return "formParser"
        else:
            print("Not going to parser")
            return "end"
    
    def _go_to_next(self, state):
        print("Going to next: ")
        print(state["next"])
        return state["next"]
    
    def _get_state(self):
        return self._graph.get_state(self._config)
    
#    def _node_agent(self, input, state, agent, name):
#        result = agent.run(input, state)
    def _node_agent(self, input, agent, name):
        result = agent.run(input, self._get_state().values)
        print("Result is: ")
        print(result)
        message = result["messages"]
        if isinstance(message, list):
            message = message[-1]
        return {"messages": message}
    
    #def _create_agents(self):
        #agents = []
        #agents.append(functools.partial(self.node_agent, self=self, agent=Orchestrator(), name="orchestrator"))
        #agents.append(functools.partial(self.node_agent, self=self, agent=FormParser(), name="formParser"))
        #return agents
    
    def _init_graph(self):
        # Initialize agents
        #orchestrator = Orchestrator()
        #form_parser_agent = FormParser()

        builder = StateGraph(BaseState)

        #agents = self._create_agents()
        #for i in agents:
            #builder.add_node(i.keywords["name"], i)
        builder.add_node("formLoader", FormLoader())
        builder.add_node("formParser", FormParser())
        builder.add_node("orchestrator", Orchestrator())
        builder.add_node("formExpert", FormExpert())

        builder.set_entry_point("formLoader")
        builder.add_conditional_edges("formLoader", self._route, {"formParser": "formParser", "end": END})
        builder.add_edge("formParser", "orchestrator")
        builder.add_conditional_edges("orchestrator", self._go_to_next, {"formExpert": "formExpert", "end": END})
        builder.add_edge("formExpert", "orchestrator")
        builder.add_edge("orchestrator", END)
        memory = SqliteSaver.from_conn_string(":memory:")
        return builder.compile(memory)

    def _set_diagram(self) -> str:
        diagram = self._graph.get_graph().draw_mermaid()
        diagram = diagram.splitlines()
        theme = "%%{init: {'theme':'base'}}%%"
        diagram[0] = theme
        diagram = diagram[:-3]
        diagram.append("\tclassDef default fill:#EEE,stroke:#000,stroke-width:1px")
        diagram.append("\tclassDef active fill:#EAA,stroke:#000,stroke-width:3px")
        return "\n".join(diagram)

    def get_diagram(self, active = "__start__") -> str:
        diagram = self._unthemed_diagram.splitlines()
        diagram.append("\tclass " + active + " active")
        diagram = "\n".join(diagram)
        print("GRAPH: ")
        print(diagram)
        return diagram

    def generate_stream_response(self, input, state = types.SimpleNamespace()):
        events = self._graph.stream({"messages": ("user", input)}, self._config, stream_mode="values")
        print("It entered")
        #print(events)
        for event in events:
            state.graph_state = self._graph.get_state(self._config).next[0]
            #print("STATE AFTER EVENT IS")
            #print(self._graph.get_state(self._config))
            message = event.get("messages")
            if isinstance(message, list):
                message = message[-1]
            msg_repr = message.pretty_repr(html=False)
            if not isinstance(message, HumanMessage):
                yield "============================= State: "
                yield state.graph_state
                yield ' =============================\n\r'
                yield msg_repr
                yield '\n\r'
        #snapshot = self._get_state()
        #state.snapshot = snapshot
    
    def get_json_form(self):
        state = self._get_state()
        if state.values["parsed_questionnaire"]:
            return state.values["source_questionnaire"]
        else:
            return ""