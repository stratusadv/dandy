from dandy.intel.intel import BaseIntel


class WeatherIntel(BaseIntel):
    location: str
    units: str | None = None


class WeatherUnitsRequiredIntel(WeatherIntel):
    units: str


class FinalAnswerIntel(BaseIntel):
    text: str
