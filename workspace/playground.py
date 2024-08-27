import os

from dandy import config
from tests.agents.work_order_comparison_agent import WorkOrderComparisonAgent
from tests.factories import generate_current_work_order

config.setup_ollama(
    url=os.getenv("OLLAMA_URL"),
    port=int(os.getenv("OLLAMA_PORT", 11434))
)

something = WorkOrderComparisonAgent.run(generate_current_work_order())

print(something.model_dump_json(indent=4))