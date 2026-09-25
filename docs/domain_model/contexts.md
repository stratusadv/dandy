# Bounded Contexts

Strategic design: where the domain's boundaries are, how each part is classified, and how
the contexts relate. Dandy is a framework, so its bounded contexts are *the contexts the
framework models for you* — the same boundaries your application code will follow.

## Subdomain classification

| Subdomain | Classification | Why |
|---|---|---|
| Structured LLM interaction (Intel, Prompt, messages, options, tool calling, decoders, diligence) | **Core** | This is what Dandy competes on. It is modeled in detail, tested hermetically, and changes with care. |
| Observability (events, recordings, renderers) | **Supporting** | Essential to the product's trust story, but not the differentiator. Modeled, but deliberately simple. |
| Concurrency (futures) | **Generic** | A commodity capability; the framework ships one small thread-pool primitive and stops. |
| Persistence (caching, file I/O) | **Generic** | Commodity memoization and disk access. Deliberately dumb: it hashes arguments, it does not understand them. |
| Coding agent (agentic coding session, planning, toolset, session state) | **Supporting (own context)** | A bounded context *built on* the core, with its own language: turns, plans, project paths, agent tools. |

## The contexts

### 1. Structured LLM interaction (core)

**Question it answers:** *what is being asked, what must the answer look like, and what
are the invariants of the conversation?*

Language: [Intel](glossary.md#glossary), [Prompt](glossary.md#glossary),
[Message/MessageHistory](glossary.md#glossary), [options](glossary.md#glossary),
[tool](glossary.md#glossary), [decoder](glossary.md#glossary),
[diligence](glossary.md#glossary).

This is the domain layer plus its use cases. Its invariants (validated Intel, one leading
system message, paired tool calls, a context window that is never exceeded) are enforced
in code and pinned by tests.

### 2. Observability

**Question it answers:** *what did the system do, in a form a human or a reviewer can
audit?*

Language: [Event, Recording](glossary.md#glossary), renderers.

The context is *event-sourced in spirit*: behavior is captured as typed events as they
happen (the framework auto-records every `Bot.process` call), and a Recording is a
projection of those events into HTML/JSON/Markdown. The capture side (event builders)
lives inside the adapters it observes; the storage and rendering side is the recorder
adapter.

### 3. Concurrency

**Question it answers:** *how do we run this off the calling thread with a timeout?*

Language: [Future](glossary.md#glossary). One primitive, `process_to_future` /
`AsyncFuture`, on a shared thread pool. No async, no queues, no workers — a generic
capability, kept deliberately small.

### 4. Persistence

**Question it answers:** *how do we not pay twice for the same work?*

Language: [cache, cache key](glossary.md#glossary), file primitives.

Two stores (memory, SQLite), one key policy (layered, depth-capped hashing of arguments).
The context is intentionally ignorant of what it caches — that is what makes it generic.

### 5. The coding agent (own context)

**Question it answers:** *how does an agent carry out a multi-step coding task in a
project?*

Language: turn, plan, project base path, agent tool, session.

This context **consumes** the core context: a coding agent turn is a use case that sends
a prompt (with an optional plan) into the core's tool-calling loop with an agent-specific
toolset (file editing, search, command, git). It keeps its own state (the persistent
conversation, the session) and its own compaction policy. It is isolated in
`dandy/application/agent/` so the core stays free of CLI concerns.

## Context mapping

```text
                 ┌──────────────────────────────┐
                 │      Coding Agent context    │
                 │  (own language, own state)   │
                 └──────────────┬───────────────┘
                                │ consumes (shared kernel for session state,
                                │ core for prompts/intel/tool loop)
┌──────────────────┐   ┌────────▼───────────────────────┐
│  Observability   │◄──┤   Structured LLM interaction  │
│ (event capture)  │   │            (core)             │
└──────────────────┘   └────────┬───────────────────────┘
                                │ uses
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
        ┌───────────┐     ┌───────────┐     ┌───────────┐
        │ Concurrency│     │Persistence│     │  Kernel   │
        │ (generic) │     │ (generic) │     │ (shared)  │
        └───────────┘     └───────────┘     └───────────┘
```

- **Core → generic contexts:** the core use cases *call into* concurrency and persistence
  (a service may run on a future; a call may be cached). The generic contexts never call
  back.
- **Observability ← core:** every core use case emits events; the recorder adapter
  consumes them. The one type-only reverse references (event builders annotating the
  objects they record) are [documented seams](../architecture/layering.md#documented-seams).
- **Coding agent → core:** the agent is a client of the core's tool loop, not a peer.
  It adds tools and state; it does not change the loop's rules.
- **Everything → kernel:** the kernel is depended on by all contexts and depends on none.

## Rule of thumb for your application

When you build on Dandy, keep the same boundaries: your domain's Intel and Prompts are
your core; your Bots are your use cases; caching, futures, and recording are generic
utilities you reach for, not things you model around. That mirroring is deliberate — it is
what lets the framework's layer rules keep applying to your code.
