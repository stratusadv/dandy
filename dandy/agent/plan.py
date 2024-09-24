from pydantic import BaseModel


class Step(BaseModel):

    action: str

class Plan(BaseModel):
    instructions: str