from dandy.schema import Schema


class PersonSchema(Schema):
    first_name: str
    last_name: str

    def __str__(self):
        return f'{self.first_name} {self.last_name}'