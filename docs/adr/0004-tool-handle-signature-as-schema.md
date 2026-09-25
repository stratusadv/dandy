# 0004. Tool handle signature is the schema

Status: Accepted
Date: 2026-09-25

## Context

The original tool design kept a tool's *description* and its *execution* in
separate places: tools carried `intel_class` / `include_fields` /
`exclude_fields` attributes describing their parameters, while an external
`tool_functions` handler map supplied the execution. Schema and behavior could
drift apart silently, a missing override was discovered only at call time, and
tools were only reusable when both pieces happened to be passed together.

## Decision

`BaseTool` (`dandy/domain/tool/tool.py`) requires a typed, annotated
`handle(self, ...) -> str | BaseIntel` override; it is abstract, so a tool
class without one cannot be instantiated. The parameter schema is derived
purely from the bound handle signature via
`IntelFactory.callable_signature_to_intel_class` (cached per instance): a
parameter without a default is required, one with a default is optional, and a
no-parameter handle yields an empty schema. At call time the arguments are
validated against that schema and passed to `handle` as typed Python keyword
arguments. An external `tool_functions` entry can still take over execution at
call time and receives the parsed arguments Intel.

## Consequences

- One source of truth: the handle is both the schema and the behavior, so
  tools are self-contained and composable; `tools=[...]` accepts a mix of
  classes and instances.
- Values arrive at `handle` Python-typed (bool/int/nested parsing applied)
  with defaults already filled in; empty or whitespace arguments from
  providers are treated as no arguments.
- A missing name or an undeclared handle fails at definition/instantiation
  time, not mid-conversation.
- Cost: parameters must be statically expressible in a Python signature
  (nothing runtime-generated); signature introspection needs the per-instance
  cache; the `handle` contract (returns `str | BaseIntel`, never raises) is a
  convention the base cannot fully enforce.
