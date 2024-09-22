from pydantic import BaseModel, ValidationError


class Cat(BaseModel):
    name: str
    age: int
    breed: str


mr_wiskers = Cat(name='Mr. Wiskers', age=5, breed='Maine Coon')

print(mr_wiskers.model_dump_json(indent=4))

json_good = '{"name": "Mr. Wiskers", "age": 5, "breed": "Maine Coon"}'
json_bad = '{"name": "Mr. Wiskers", "breed": "Maine Coon"}'

try:
    mr_wiskers_good = Cat.model_validate_json(json_bad)

except ValidationError as e:
    ve = e.__str__().replace("'", '"')
    print(e)
    print(ve)
