from time import time
from typing import List

from dandy.core.singleton import Singleton
from dandy.debug.event import Event


class Debug(Singleton):
    _running: bool = False
    start_time: float
    stop_time: float
    events: List[Event]

    @classmethod
    def add_event(
            cls,
            actor: str,
            action: str,
            data: dict
    ):
        if cls.is_running:
            cls.events.append(
                Event(
                    actor=actor,
                    action=action,
                    data=data
                )
            )

    @classmethod
    def add_event_if_running(
            cls,
            actor: str,
            action: str,
            data: dict
    ):
        if cls.is_running:
            cls.add_event(actor, action, data)

    @classmethod
    def start(cls):
        cls.start_time = time()
        cls._running = True

    @classmethod
    def stop(cls):
        cls.stop_time = time()
        cls._running = False
        cls.events = []

    @classmethod
    def is_running(cls):
        return cls._running