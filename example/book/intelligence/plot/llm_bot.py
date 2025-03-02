from typing import Any

from dandy.llm import BaseLlmBot
from example.book.intelligence.plot.intel import PlotStructureIntel


class PlotOutlineLlmBot(BaseLlmBot):
    config = 'COMPLEX'
   
    @classmethod    
    def process(
            cls, 
            *args, 
            **kwargs
    ) -> PlotStructureIntel:
        
        pass