from pydantic import ValidationError


def pydantic_validation_error_to_str(error: ValidationError) -> str:
    return error.__str__().replace("'", '"')