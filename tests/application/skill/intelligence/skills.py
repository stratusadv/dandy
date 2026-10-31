from dandy.domain.skill.skill import BaseSkill


class NotesSkill(BaseSkill):
    name = 'notes'
    description = 'Keep and recall notes. Use when the user wants to store or find a note.'
    prompt = 'Store notes with notes_save and find them with notes_recall.'
    active = True
    tools = ['save', 'recall']

    def save(self, note: str) -> str:
        """Store a note."""
        return f'Saved: {note}'

    def recall(self, keyword: str = '') -> str:
        """Recall notes matching a keyword."""
        return f'Notes matching {keyword or "everything"}: none yet'


class WeatherSkill(BaseSkill):
    name = 'weather'
    description = 'Get current weather. Use when the user asks about the weather.'
    prompt = 'Answer weather questions using the weather tool.'
    active = False
    tools = ['current']

    def current(self, location: str) -> str:
        """Get the current weather for a location."""
        return f'The current weather in {location} is sunny.'
