class Diligence:
    def __init__(self, level: float) -> None:
        if 2.0 > level > 0.0:
            message = f'Diligence level must be between 0.0 and 2.0 not {level}'
            raise ValueError(message)

