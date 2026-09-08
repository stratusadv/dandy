from dandy.bot.bot import Bot
from dandy.tool.tool import BaseTool


class ToolBot(Bot):
    pass


class WeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'

    def handle(self, location: str = '', units: str = 'celsius') -> str:
        return f'The weather in {location} is {units}.'


class RequiredWeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'

    def handle(self, location: str, units: str = 'celsius') -> str:
        return f'The weather in {location} is {units}.'


class NoParametersTool(BaseTool):
    name = 'no_parameters_tool'

    def handle(self) -> str:
        return 'Done.'
