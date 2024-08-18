class AssistantInterface:
    def generate_stream_response(self, input):
        pass

    def get_graph(self) -> str:
        return """
            graph TD
                A --> B
            """