from typing import List


class Workflow:
    agents: List['Agent']

    @classmethod
    def process(cls, job: 'Job'):
       for agent in cls.agents:
            agent.process(job)