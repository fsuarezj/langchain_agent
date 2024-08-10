from .assistance_interface import AssistantInterface
import random
import time

class MockAssistant(AssistantInterface):
    def __init__(self):
        self._mock_responses = [
            "Hello, this is response 1",
            "Now I'm giving you response 2",
            "This is not other than response 3"
        ]
    
    def generate_stream_response(self, input):
        for word in random.choice(self._mock_responses).split():
            yield word + " "
            time.sleep(0.05)