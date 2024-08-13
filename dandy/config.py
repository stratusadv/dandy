

class Config:
    llm: str
    llm_address: str
    llm_port: int

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance


config = Config()