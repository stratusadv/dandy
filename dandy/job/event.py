from time import time

from dandy.job.enums import EventActorType


class Event:
    def __init__(
            self,
            actor: EventActorType,
            description: str,
    ):
        self.timestamp = time()
        self.actor = actor
        self.description = description


class EventManager:
    def __init__(self):
        self.events = []

    def add_event(self, actor: EventActorType, description: str):
        self.events.append(
            Event(
                actor,
                description
            )
        )
