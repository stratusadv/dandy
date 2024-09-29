from enum import Enum


class CrewRole(str, Enum):
    captain = 'Captain'
    captain_assistant = 'Captain Assistant'
    engineer = 'Engineer'
    navigator = 'Navigator'
    navigator_assistant = 'Navigator Assistant'
    sailor = 'Sailor'
    sailor_assistant = 'Sailor Assistant'