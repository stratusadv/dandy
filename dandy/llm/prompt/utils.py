from typing_extensions import List


def list_to_str(items: List, ordered: bool = False, indent: int = 0, ordered_number_prefix: str = '') -> str:
    output_str = ''
    ordered_correction = 1

    for i, item in enumerate(items):
        output_str += '    ' * indent

        if isinstance(item, (list, tuple, set)):
            ordered_correction -= 1
            output_str += list_to_str(items=item, ordered=ordered, indent=indent + 1, ordered_number_prefix=f'{ordered_number_prefix}{i + ordered_correction}.')
        else:
            if ordered:
                output_str += f'{ordered_number_prefix}{i + ordered_correction}. '
            else:
                output_str += '- '

            output_str += f'{item}\n'

    return output_str
