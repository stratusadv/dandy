from dandy.bot.bot import Bot
from dandy.tool.tool import BaseTool

from tests.llm.tool.intelligence.intel import (
    WeatherIntel,
    WeatherUnitsRequiredIntel,
)


class ToolBot(Bot):
    pass


class WeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'
    intel_class = WeatherIntel


class MinimalWeatherTool(WeatherTool):
    include_fields = {'location'}


class NoUnitsWeatherTool(WeatherTool):
    exclude_fields = {'units'}


class RequiredUnitsWeatherTool(WeatherTool):
    intel_class = WeatherUnitsRequiredIntel
