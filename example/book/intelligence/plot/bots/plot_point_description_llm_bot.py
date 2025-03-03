from typing import Any

from dandy.llm import BaseLlmBot
from example.book.intelligence.plot.intel import PlotIntel


class PlotPointDescriptionLlmBot(BaseLlmBot):
    config = 'COMPLEX'
   
    @classmethod    
    def process(
            cls, 
            *args, 
            **kwargs
    ) -> PlotIntel:
        
        pass