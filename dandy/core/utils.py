from pydantic import ValidationError, BaseModel


def pydantic_validation_error_to_str(error: ValidationError) -> str:
    return error.__str__()


def json_default(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    else:
        try:
            return str(obj)
        except TypeError:
            return '<unserializable value>'
