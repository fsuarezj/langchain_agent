from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.runnables import Runnable

class CostCalculator:
    def __init__(self):
        self._runnable: Runnable
    
    def _costs_invoke_OpenAI(self, costs_dict: dict, state: dict):
        print('INVOCANDO')
        print(costs_dict)
        with get_openai_callback() as cb:
            result = self._runnable.invoke(state)
            my_type = type(self).__name__
            if my_type in costs_dict:
                costs_dict[my_type] += cb.total_cost
            else:
                costs_dict[my_type] = cb.total_cost
        print('AFTER INVOCAR')
        print(costs_dict)
        return result
