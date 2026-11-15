from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from dandy.application.agent.intelligence.tools.tool_errors import tool_error
from dandy.domain.tool.tool import BaseTool

LOCAL_TIMEZONE = 'local'


class ClockTool(BaseTool):
    name = 'get_time'
    description = (
        'Get the current date and time. '
        'Returns the local date and time, or the date and time in a named IANA timezone '
        'such as "UTC" or "America/New_York" when one is given.'
    )

    action_label = 'Getting current time'

    def action_output(self, **kwargs: Any) -> str:
        timezone = kwargs.get('timezone') or ''

        return f'in {timezone}' if timezone and timezone != LOCAL_TIMEZONE else 'system time'

    @tool_error('getting time')
    def handle(self, timezone: str = LOCAL_TIMEZONE) -> str:
        resolved_timezone = None if timezone == LOCAL_TIMEZONE else ZoneInfo(timezone)
        now = datetime.now(resolved_timezone)

        if now.tzinfo is None:
            now = now.astimezone()

        return f'{now.strftime("%A, %Y-%m-%d %H:%M:%S")} {now.tzname()}'
