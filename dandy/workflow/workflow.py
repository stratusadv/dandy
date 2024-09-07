from __future__ import annotations

from abc import ABC

from dandy.handler.handler import Handler


class Workflow(Handler, ABC):
    ...
