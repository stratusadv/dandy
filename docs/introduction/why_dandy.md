# Why Dandy

Dandy is built around one idea: **get the LLM interaction right the first time.**
Structured prompts in, validated objects out, self-recovery around the probabilistic
boundary, and deterministic control for everything else. This page makes the case for
why that matters, and where each mechanism lives.

## Token efficiency is a first-class goal

Every token processed — prompt or completion — costs money, latency, and energy: each
token triggers matrix multiplications, attention, and memory traffic across the whole
network, and energy scales roughly linearly with that compute. Reducing token usage is
therefore one of the most effective levers for cost, responsiveness, and sustainable AI.
It also buys you capacity for validation, governance, and quality checks on the output.

Dandy attacks both sides of the conversation with the same four mechanisms:

| Mechanism | What it reduces |
|---|---|
| [Structured prompts](../user_guide/prompts.md) | prompt tokens — labeled, minimal, programmatic prompt construction instead of bloat |
| [Intel contracts](../user_guide/intel.md) | completion tokens — constrained shape and size, no narrative padding |
| [Decisions](../user_guide/decision.md) | completion tokens — the model returns a tiny validated key, not a paragraph |
| [Caching](../user_guide/caching.md) | both — repeated calls become zero-token hits |

The sections below show each one on a single running example: evaluating an employee
and assigning them to a project.

### Structured prompts

`Prompt` turns unguided text into predictable, human-readable prompts. Labeled
snippets (`title`, `heading`, `text`, `ordered_list`, ...) remove ambiguity at the
input layer, and because prompts are built in code, dynamic data never bloats them:

```python
from dandy import Prompt

employee = ...  # retrieved employee data

prompt = (
    Prompt()
    .title(employee.name)
    .line_break()
    .heading('Work History')
    .line_break()
    .text(employee.work_history_overview)
    .line_break()
    .ordered_list([event for event in employee.work_history_events])
)
if employee.certificates:
    prompt.heading('Certificates')
    for certificate in employee.certificates:
        prompt.line_break()
        prompt.sub_heading(certificate.name)
        prompt.text(certificate.details)
```

### Intel contracts

Defining the answer as a strict pydantic schema removes guesswork from output parsing:
the response is type-safe, needs no post-processing, and is *smaller* than the
equivalent freeform text. The schema itself acts as a guideline — constraining the
model without adding a word to the prompt:

```python
from typing import Literal

from dandy import BaseIntel


class EmployeeEvaluationIntel(BaseIntel):
    employee_name: str
    primary_skills: list[str]
    secondary_skills: list[str]
    recommended_role: Literal['Junior', 'Intermediate', 'Senior']
    evaluation_notes: str
```

### Bots

A [Bot](../user_guide/bots.md) captures the whole interaction — role, task,
guidelines, and return type — as a named, reusable unit. Composable sections prevent
long system text from being duplicated across calls, and when prompting technique
improves you update one bot instead of every call site:

```python
from dandy import Bot, Prompt


class EmployeeEvaluationBot(Bot):
    role = 'Employee Evaluator'
    task = 'Read the provided employee information and classify their skills.'
    guidelines = Prompt().list(
        [
            'Use context throughout the information to return the top skills.',
            'Identify exactly 3 primary and 3 secondary skills.',
        ]
    )
    intel_class = EmployeeEvaluationIntel


evaluation = EmployeeEvaluationBot().process(prompt)
print(evaluation.primary_skills[0])
```

### Decisions

For routing, classification, and policy work, [Decision](../user_guide/decision.md)
lets the model return a tiny validated key instead of paragraphs. The model never
re-states the data it is choosing from — it just picks:

```python
from dandy import Bot


class EmployeeAssignmentBot(Bot):
    def process(self, prompt: str, evaluations: list[EmployeeEvaluationIntel]):
        return self.llm.decision.prompt_to_value(
            prompt=prompt,
            keys_description='employee skill evaluations',
            keys_values={
                str(evaluation.primary_skills): evaluation
                for evaluation in evaluations
            },
        )


employee = EmployeeAssignmentBot().process(
    'Find me the best employee for a python data processing project.', evaluations
)
print(employee.employee_name)
```

### Caching

With one decorator, expensive repeated calls become instant, zero-token responses —
and while a recording is live, a cache hit records a "Cached Response" event, so you
can *see* in a report that no LLM call was made:

```python
from dandy import cache_to_sqlite


class CachedEvaluationBot(EmployeeEvaluationBot):
    @cache_to_sqlite('employee_evaluation', limit=100)
    def process(self, prompt):
        return super().process(prompt)
```

## Self-recovery

AI endpoints fail in transient ways — timeouts, rate limits, malformed responses,
wrong-shape JSON. Dandy classifies every failure as [Critical or
Recoverable](../user_guide/error_handling.md) and recovers from the recoverable ones
automatically:

- A wrong-shape response is re-prompted with the validation errors until
  `prompt_retry_count` is exhausted.
- HTTP timeouts, connection errors, and non-2xx responses are retried
  (`HTTP_CONNECTION_RETRY_COUNT` times).
- A decision that returns no choice, or too many, is re-prompted the same way.

What is left after recovery is a deterministic, typed failure you can branch on —
the [error handling page](../user_guide/error_handling.md) shows the pattern.

## It works with the models you have

Because the answer is constrained by a schema rather than prose, Dandy makes
smaller, cheaper, and quantized models practical for work that would otherwise need a
flagship endpoint. That matters for:

- small-to-medium teams with limited AI infrastructure
- individual developers on personal hardware
- teams with restricted cloud access or constrained budgets
- educational settings teaching AI development

Any OpenAI-compatible chat-completions endpoint works — see
[Configuration](../getting_started/configuration.md).

## Measured results

!!! note "Pre-v3 measurements"

    The numbers below were collected while developing Dandy v0–v2 (observationally,
    across client integrations, and computationally, by trimming prompts and
    measuring before/after). They have not been re-run against v3, and are offered
    as direction: every mechanism above still exists in v3, but your integration's
    numbers will depend on your workloads.

Across the integrations tracked, following the practices above produced an
**average ~25% reduction in token usage**, with experienced integrations reaching
**over 60%**. The per-module breakdown, as measured:

| Module | Prompt tokens | Completion tokens | Measurement |
|---|---|---|---|
| Prompt | 0–5% | 5–10% | observational |
| Intel | 10–15% | 0–5% | computational |
| Bot | 5–10% | 15–20% | observational |
| Decision (was Decoder) | 30–35% | 75–80% | computational |
| Cache | 20–25% | 20–25% | computational |

The two main drivers behind the numbers: teaching the integration the patterns, and
improving the framework's pre/post-processing in parallel.

## Where to read next

- [What is Dandy](what_is_dandy.md) — the architecture that makes all of this
  possible.
- [The Quick Start](../getting_started/quick_start.md) — a typed call in four steps.
- [The Example Project](../user_guide/example_project.md) — every mechanism used
  together to generate a book.
