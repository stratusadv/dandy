from __future__ import annotations

from abc import ABC
from typing import Type, Union

from pydantic import BaseModel


class Workflow(ABC):
    def run(self):
        pass
