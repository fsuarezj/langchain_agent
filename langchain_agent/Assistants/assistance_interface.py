
class AssistantInterface:
    def generate_stream_response(self, input, state):
        pass

    def get_diagram(self, active = "__start__") -> str:
        diagram = """
            %%{init: {'theme':'base'}}%%
            graph TD
                __start__ --> __end__
            classDef default fill:#EEE,stroke:#000,stroke-width:1px
            classDef active fill:#EAA,stroke:#000,stroke-width:3px
            """
        diagram += f"class {active} active"
        return diagram
