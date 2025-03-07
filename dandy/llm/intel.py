from dandy.intel import BaseIntel


class DefaultLlmIntel(BaseIntel):
    text: str
    
    def __str__(self):
        return self.text