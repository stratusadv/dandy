from pydantic import BaseModel


class PersonModel(BaseModel):
    first_name: str
    last_name: str