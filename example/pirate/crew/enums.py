from enum import Enum


class CrewRole(str, Enum):
    CAPTAIN = 'Captain'
    ENGINEER = 'Engineer'
    NAVIGATOR = 'Navigator'
    SAILOR = 'Sailor'
