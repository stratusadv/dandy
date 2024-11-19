import importlib

from dandy.handler.handler import Handler


def test_handler(module_and_class: str, user_prompt: str) -> None:
    if user_prompt:
        user_input = user_prompt
    else:
        user_input = input(f'User Input: ')

    print(f'Testing {module_and_class} ... depending on your llm configuration this may take up to a couple minutes')

    print(f'Module: {".".join(module_and_class.split(".")[0:-1])}')
    module = importlib.import_module('.'.join(module_and_class.split('.')[0:-1]))

    print(f'Class: {module_and_class.split(".")[-1]}')
    cls: Handler = getattr(module, module_and_class.split('.')[-1])

    result = cls.process(user_input=user_input)

    print(result)