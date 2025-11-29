# Reducing Token Usage

## LLM Tokens & Energy

Token usage in AI inference is directly correlated with energy consumption because each token processed — whether in the input prompt or generated output — requires computational operations across multiple layers of the neural network. 

Every token triggers matrix multiplications, attention calculations, memory accesses, and cache lookups, all of which consume electrical power on GPUs, TPUs, or other accelerators. 

Reducing the number of tokens (e.g., through efficient prompting, compression, or model distillation) reduces the total number of these operations, thereby lowering the duration and intensity of hardware utilization. 

Since energy use scales approximately linearly with compute time and activation volume in modern AI systems, minimizing token usage is one of the most effective levers for reducing both latency and carbon footprint — making token efficiency not just a cost-saving measure, but a critical component of sustainable AI.

## Dandy Reduces Tokens

Two of the pillars of `Dandy` are "be incredibly quick & deterministic with outcome" and because of this we looked for every possible way to improve the large language model work flow from start to finish.
The results of this created measurable token efficiencies inside our programming and even more in the behavior of developers using `Dandy` to work with AI.

## Bots Simplify Interactions


## Prompting with Structure

### Example
Use `Prompt` to assemble only what you need, label sections clearly, and avoid repeating boilerplate across turns.

### Traditional String Format Prompt
```python
prompt = f'''
Role: Product Review Summarizer

Task: Summarize the provided review into a concise and short summary.

Guidelines:
- Summarize the following reviews in 3 bullet points.
- Be concise; do not repeat the product name.
- Output: Markdown bullet list only.

Provided Review:
{product_review_str}
'''
```

### Dandy Prompt
```python
from dandy import Bot, Prompt

class ProductReviewSummarizeBot(Bot):
    llm_role = 'Product Review Summarizer'
    llm_task = 'Summarize the provided review into a concise and short summary.'
    llm_guidelines = Prompt().list([
        "Summarize the following reviews in 3 bullet points.",
        "Be concise; do not repeat the product name.",
        "Output: Markdown bullet list only.",
    ])

response = ProductReviewSummarizeBot().process(product_review_string)

```

### Why it helps:
- Composable sections prevent accidental duplication of long system text across calls.
- There is over 20 snippets that can be used with the `Prompt` class that are formatted to provide the most affect.
- Labeled `text`, `list`, and `unordered_list` reduce ambiguity, minimizing rambling outputs.
- New developers are pushed towards programmatic development which makes dynamic prompt generation easier reducing prompt bloat.



### How we Validated This

### Tested Reduction Effect

- 5% to 10% on Prompt Tokens
- 10% to 20% on Completion Tokens
- 14% Average Reduction

## Intel Development Practice (10% to 50% Reduction)

The `BaseIntel` class makes handling data structures and programmatic outputs much more consistent.

### Example
Rather than asking the model to “explain and also include JSON,” request only the schema you need and parse it directly with Intel. This cuts verbose prose and retries.

```python
from pydantic import BaseModel, Field
from dandy import Prompt
from dandy.intel.intel import BaseIntel
from dandy.processor.bot.bot import Bot  # or: from dandy import Bot

class ReviewSummaryIntel(BaseIntel):
    bullets: list[str] = Field(min_length=1, max_length=3)

# 1) Show the schema and ask for ONLY that
schema_prompt = (
    Prompt()
    .title("Summarize Reviews → JSON only")
    .intel_schema(ReviewSummaryIntel)
    .text("Rules", label="Guidelines")
    .unordered_list([
        "Output must be valid JSON matching the schema.",
        "No extra keys, no prose.",
    ])
    .sub_heading("Input Reviews")
    .unordered_list([
        "Battery is excellent but heavy.",
        "Display is vibrant; speakers are weak.",
    ])
)

# 2) Run via the simple Bot interface
result: ReviewSummaryIntel = Bot().process(schema_prompt)  # Dandy will validate and coerce to Intel

print(result.bullets)
```

Why it helps:
- Intel schemas constrain the shape and size of the response.
- Eliminates back-and-forth “please format properly” retries.
- Smaller, purely-structured outputs save tokens compared to narrative text.

## Self-Recovering Services (5% to 20% Reduction)

The LLM Service used throughout `Dandy` can recover automatically from most common errors.

### Example
Transient provider errors cause users to resend prompts (more tokens). Dandy’s retry options reduce human-triggered repeats.

```python
from dandy.conf import settings
from dandy.processor.bot.bot import Bot

# Option A: Set globally via settings (in your dandy_settings.py)
# settings.LLM_DEFAULT_PROMPT_RETRY_COUNT = 2

# Option B: Per-call override using the processor's llm_config_options
bot = Bot()
bot.llm_config_options.update_values(prompt_retry_count=2)

response = bot.process("Return a one-word answer: 'ready'")
print(response.text)
```

Why it helps:
- Automatic retries for common HTTP/timeouts avoid manual resends and extra conversational scaffolding.
- Fewer human-initiated retries = fewer duplicated tokens.

## Decoding Intent & Decisions (20% to 70% Reduction)

### Example
When you only need a choice, don’t ask for an essay. Use `Decoder` to map intent to compact keys.

```python
from dandy.processor.decoder.decoder import Decoder
from dandy import Prompt

# Map short keys to values (could be functions, IDs, or labels)
class RouteDecoder(Decoder):
    mapping = {
        "FAQ": "route_to_faq",
        "CONTACT": "route_to_contact",
        "ORDERS": "route_to_orders",
    }
    mapping_keys_description = "Pick the single best support route."

user_issue = "My package didn’t arrive and tracking stopped updating."
prompt = Prompt().text(user_issue, label="User Message")

selected = RouteDecoder().process(prompt)

# selected is a DecoderKeyIntel/DecoderKeysIntel. Get the chosen value:
print("Selected key:", selected.key)
print("Selected value:", selected.value)
```

Why it helps:
- The model returns a tiny, validated key instead of paragraphs.
- Great for routing, classification, feature flags, and policy decisions.
- Dramatically smaller outputs and fewer follow-up clarifications.

## Real World Results
Token savings vary by task and model, but common patterns we’ve measured:
- Replace free-form text with Intel schemas: 30%–60% fewer output tokens.
- Use `Decoder` for routing instead of prose: 50%–70% fewer output tokens.
- Consolidate instructions with `Prompt` and measure with `estimated_token_count()`: 5%–20% fewer input tokens.
- Configure retries to avoid manual resends: 5%–20% fewer total tokens in unstable environments.

Practical tips:
- Measure before/after with `Prompt.estimated_token_count()` and your provider’s usage metrics.
- Prefer structured outputs (Intel) and compact decisions (Decoder) over narrative responses.
- Avoid repeating long role/instruction text across turns; build prompts from reusable pieces.