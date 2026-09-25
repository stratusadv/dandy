# Why Use Dandy?

Dandy brings the framework approach to using AI (specifically LLM's) that allows for people to write efficiently and structure AI interactions easily and consistently.

All the parts of Dandy provide clear opportunities to **"Get it right the first time"** stripping away a lot of the difficulty of working with AI and in turn creating more impactful LLM interactions.

>On the execution side we are able to apply pre- & post-processing to everything that happens allowing for optimization the developers are not responsible for.

Beyond token usage, Dandy has a lot of custom error handling and self-recovery that drastically increases the reliability of AI interactions, producing the desired results with less variability.
This in itself is crucial to building value-driven AI interactions which require less iteration on both development and processing, which substantially contributes to token use reduction.

## Creating More Options

Dandy's framework approach enables developers to effectively use a wider range of model sizes and quantization that require less computational resources while maintaining high-quality outputs. 

> These optimizations allow teams to work with more efficient AI models per task easily, creating a potential of energy and cost savings up to a factor of three times (based on parameter count and quantization).

This is especially valuable for:

- Small-to-medium-sized companies with limited AI infrastructure
- Individual developers working on personal hardware
- Teams in regions with restricted access to cloud computing resources or energy
- Educational institutions teaching AI development
- Startups operating with constrained computing budgets

The framework's efficient token usage and optimization features mean you can achieve professional results even when using smaller, more accessible models and quantization levels.

## Reducing Token Usage is Critical

Token usage in AI inference is directly correlated with energy consumption because each token processed (prompt or completion) requires computational operations across multiple layers of the neural network.

Every token triggers matrix multiplications, attention calculations, memory accesses, and cache lookups, all of which consume electrical power on CPUs, GPUs, TPUs, or other accelerators. 

> Since energy use scales approximately linearly with compute time and activation volume in modern AI systems, minimizing token usage is one of the most effective levers for reducing energy consumption, making token efficiency a critical part of sustainable AI.

Beyond environmental benefits, reducing token usage offers significant value-generating advantages.

- Reduced latency providing faster response times to requests
- More capacity for output validation, governance, safety, and quality checks
- Improved throughput allowing for drastically more complex value generation and processing 
- Overall enhanced system performance while reducing operational costs

## Prompting with Structure

Structured prompting removes ambiguity at the input layer - turning unguided text into predictable, optimized, and human-readable prompts that reduce bloat and guide LLMs toward precise outputs.

### Example

```python
from dandy import Prompt

employee = ... # Data retrieved on the employee

employee_information_prompt = (
    Prompt()
    .title(employee.name)
    .lb() # Shorthand for .line_break()
    .heading('Work History')
    .lb()
    .text(employee.work_history_overview)
    .lb()
    .ordered_list([work_history_event for work_history_event in employee.work_history_events])
    .lb()
    .heading('Education')
    .lb()
    .ordered_list([education_event for education_event in employee.education_events])
)

if employee.certificates:
    employee_information_prompt.heading('Certificates')
    
    for certificate in employee.certificates:
        employee_information_prompt.lb()
        employee_information_prompt.sub_heading(certificate.name)
        employee_information_prompt.text(certificate.details)

```

### Why it helps:

- There is over 20 snippets that can be used with the `Prompt` class that are formatted to provide the most affect.
- Labeled items like `title`, `heading`, `text`, and `ordered_list` reduce ambiguity, minimizing rambling outputs.
- New developers are pushed towards programmatic development, which makes dynamic prompt generation easier reducing prompt bloat.

## Intel Development Practice

By defining LLM responses as strict Python schemas, Intel removes guesswork from output parsing - ensuring structured, type-safe results that require no post-processing and consume far fewer tokens than freeform text.

### Example

```python
from typing import Literal
from dandy import BaseIntel

class EmployeeEvaluationIntel(BaseIntel):
    employee_name: str
    primary_skills: list[str]
    secondary_skills: list[str]
    recommended_role: Literal['Junior Developer', 'Intermediate Developer', 'Senior Developer']
    evaluation_notes: str
    
```

### Why it helps:

- Intel schemas constrain the shape and size of the response, allowing you to always interact in python.
- Eliminates back-and-forth “please format properly” or "make sure to add..." retries.
- Smaller, purely structured outputs save tokens compared to narrative text.
- The intel structure alone can act as a guideline or instruction with out increasing the input prompt token count.


## Bots Simplify Interactions

Bots encapsulate the full lifecycle of an AI interaction — from system prompt to structured output — enabling reusable, self-documenting, and optimizable AI agents that eliminate redundancy and accelerate iteration.

### Example

```python
from dandy import Bot, Prompt, BaseIntel


class EmployeeEvaluationBot(Bot):
    role = 'Employee Evaluator'
    task = 'Read through the provided employee information and classify their skills.'
    guidelines = Prompt().list([
        'Use context through out the information to return the top skills.',
        'Please only identify 3 primary and secondary skills.',
    ])
    intel_class = EmployeeEvaluationIntel  # From "Intel Development Practice"


employee_evaluation_intel = EmployeeEvaluationBot.process(
    employee_information_prompt)  # From "Prompting with Structure"

print(employee_evaluation_intel.primary_skills[0])  # Prints the first primary skill

```

### Why it helps:

- Composable sections prevent accidental duplication of long system text across calls.
- As system prompting techniques change, there is no requirement to update the bot structure to get the benefits.
- Programmatic interactions encourage experimentation and rapid change leading to more optimization.

## Decoding Intent & Decisions

Decoders transform ambiguous LLM outputs into deterministic routing keys — enabling high-stakes decisions (classification, routing, policy) with minimal tokens and zero parsing overhead.

### Example

```python
from dandy import Decoder

employee_evaluations_intel = ... # a list of employee evaluation intel from the EmployeeEvaluationBot in "Bots Simplify Interactions"

class EmployeeAssignmentDecoder(Decoder):
    mapping_keys_description = "Employee Skill Evaluation"
    mapping = {
        str(employee_evaluation_intel.primary_skills): employee_evaluation_intel
        for employee_evaluations_intel in employee_evaluations_intel
    }

values = EmployeeAssignmentDecoder().process('Find me all the employees that would be good for a python data processing project.')

print(values[0].employee_name) # Prints the first employee name in from the employee_evaluation_intel

```

### Why it helps:

- The model returns a tiny, validated key instead of paragraphs or long strings of information.
- Great for routing, classification, feature flags, and policy decisions only sending the exact prompt data required.
- Dramatically smaller outputs and fewer follow-up clarifications.
- Strict pre- and post-processing allows for decoders to work very well with small heavily quantized models.

## Caching Made Easy

With a single decorator, caching turns expensive repeated LLM calls into instant, zero-token responses — making scalability and cost-efficiency not just possible, but effortless.

### Example

```python
from dandy import Bot, cache_to_sqlite, Prompt

class EmployeeEvaluationBot(Bot):
    # Same Configuration as "Bots Simplify Interactions"

    @cache_to_sqlite('employee_evaluation', 100)
    def process(self, employee_information_prompt: Prompt):
        # Some custom processing
        return self.llm.prompt_to_intel(
            prompt=employee_information_prompt
        )

# First time we run we will hit our AI server and consume compute (100% token Usage)

employee_evaluation_intel_1 = EmployeeEvaluationBot.process(employee_information_prompt) # From "Prompting with Structure"

# Second time we run with the same prompt we don't us compute (0% token Usage)

employee_evaluation_intel_2 = EmployeeEvaluationBot.process(employee_information_prompt) # From "Prompting with Structure"

```

### Why it helps:

- Simplifying the process to add caching will encourage developers to be more efficient in design.
- On high-throughput processes caching can substantially reduce token usage with minimal effort.
- Cache life cycles can also be used to have a balance of freshness and efficiency in compute.


## Real World Results

Throughout the development of Dandy we have seen a drastic increase in the quality of completion tokens and a sharp reduction in the use of prompt tokens.
We have both tracked the behavioral and computational effects both from an observational and measured perspective.

These results have been a guiding force behind all the updates we make to Dandy, along with how we plan out the future of this framework.

### Our Finding

Across all the areas we observed and measured, we found implementing Dandy into your projects and following best practices provides an **average 25% reduction in token usage**.
After developers gained familiarity with advanced patterns, some integrations achieved **over 60% reduction in token usage**.

> The two main drivers in this were teaching developers the best way to develop artificial intelligence integrations and improving Dandy through feedback so that all interactions are improved in parallel.

### Token Reduction Per Module Results

All results are the average range of reduction in usage per interaction for prompt and completion tokens rounded down to the nearest 5% for simplicity.  

#### Prompt

- Average Reduction Percentage:
    - Prompt Tokens: 0% to 5%
    - Completion Tokens: 5% to 10%
- Effect Source:
    - Developer Behavior
- Measurement:
    - Type:
        - Observational
    - Method:
        - Working with a wide skill range of developers and having them integrate Dandy into their projects.
        - As they implemented or replaced features with Dandy we check the token usage before and after to confirm a reduction in token usage.

#### Intel

- Average Reduction Percentage:
    - Prompt Tokens: 10% to 15%
    - Completion Tokens: 0% to 5%
- Effect Source:
    - Testing
- Measurement:
    - Type:
        - Computational
    - Method:
        - We ran multiple prompts cutting away the prompt tokens and allowing the intel object to guide the LLM. 
        - In these scenarios the direct reduction of prompt tokens did not affect the outcome of the completion tokens.

#### Bot

- Average Reduction Percentage:
    - Prompt Tokens: 5% to 10%
    - Completion Tokens: 15% to 20%
- Effect Source:
    - Developer Behavior
- Measurement:
    - Type:
        - Observational
    - Method:
        - Watching developers use and chain bots together, we measured the before and after of the token usage in their process.
        - Since the structure of the bots was easy and flexible for developers to continuously optimize the pre- and post-processing created a direct reduction in tokens.

#### Decoder

- Average Reduction Percentage:
    - Prompt Tokens: 30% to 35%
    - Completion Tokens: 75% to 80%
- Effect Source:
    - Testing
- Measurement:
    - Type:
        - Computational
    - Method:
        - Evaluating the pre-processing done with the decoder through testing, we were able to measure directly the reduction in tokens required to make decisions using decoders.
        - The dynamic system prompt in the background of Dandy for each of its modules is continuously tested to confirm its performance.

#### Cache

- Average Reduction Percentage:
    - Prompt Tokens: 20% to 25%
      - Completion Tokens: 20% to 25%
- Effect Source:
    - Testing
- Measurement:
    - Type:
        - Computational
    - Method:
        - Across our client projects and development implementation we were able to measure the effected interactions using caching. 
        - We looked at multiple implementations of caching and took the median based on real-world application.

