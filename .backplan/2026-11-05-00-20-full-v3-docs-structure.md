# Full v3 docs structure

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-05-00-20

## End State

The v3 docs site (`docs/` + `mkdocs.yml`) has a complete structure in which every
still-relevant archived-docs topic (why Dandy, project structure, example project,
2026 roadmap, about: branding/contributors/credits) has a current v3 equivalent page
accurate to the v3.0.0a1 code, all examples use the verified v3 API, `mkdocs.yml` nav
covers every page, and `mkdocs build --strict` passes.

## Observable Concern

The archived content is v2-era: its examples (`Decoder` / `bot.llm.decoder`,
`from dandy.conf import settings`, `from dandy.llm import Prompt`) and its marketing
claims (sub-millisecond overhead, per-module token-reduction percentages measured on
v2) are wrong or unverifiable for v3. Porting any of it without re-verifying each
example against the current code would produce "awesome" docs that actively mislead.
Mitigation: every example in a new page is written against the verified v3 API (and the
book example page against the actual `tests/application/example_project/book` source),
and quantitative claims are either dropped or explicitly labeled as pre-v3 measurements.

## Current State

Verified this session (step 0):

- **Current site**: 24 pages, all in the `mkdocs.yml` nav (confirmed by reading the
  full nav, `mkdocs.yml:27-68`): `index`, `introduction/{what_is_dandy,principles}`,
  `domain_model/{glossary,contexts,tactical}`,
  `architecture/{layering,service_pattern,data_flow,agents}`,
  `getting_started/{installation,quick_start,configuration}`,
  `user_guide/{intel,prompts,bots,options_and_context,tool_calling,skill,decision,
  recording,caching,futures,agent,cli_agent,error_handling}`,
  `reference/{shared,domain,application,infrastructure,interfaces}`,
  `migration/v2_to_v3`, `changelog/v3`.
- **House style**: each user_guide page opens with a "Domain concept:" + "Lives in:"
  pair, uses verified examples with "(Verified: ...)" notes, tight tables, admonitions;
  `mkdocs.yml` enables admonition, attr_list, superfences (+mermaid), tables, snippets;
  theme is Material with `docs/static/img/` logo/favicon.
- **Existing pages are not thin where archived tutorials were deeper**: `intel.md`
  covers include/exclude + nested-dict drilling + helpers; `prompts.md` has the full
  builder catalog table; `caching.md` covers decorators, layered key hashing, manual
  cache use; `futures.md` covers fan-out + `*_future` variants. No rewrites needed.
- **Archived topics and their status**:
  - `why_use_dandy.md` (308): value props + token-efficiency results, **v2 API
    examples** — NO current equivalent → gap.
  - `tutorials/project_structure.md` (98): `intelligence/` convention, one bot per
    file, `Intel` suffix naming — NO current equivalent → gap.
  - `tutorials/example_project.md` (42): links a **stale** GitHub `example/` dir; the
    real project is `tests/application/example_project/book` (book workflow: theme →
    title → characters → world → plot → chapters) — NO current equivalent → gap.
  - `roadmap/2026_roadmap.md` (60) + legend: Jan–Mar items ✅ (v2 alpha/stable, CLI
    prototype); Apr–Dec items 🚧/open (OpenAI options, docs update, file control,
    vision, listening, bots-calling-bots, stateful memory, db connector, cache, error
    handling, compaction, enterprise, encoding, typing, enrichment, recorder,
    prompting) — NO current equivalent → gap (needs honest re-marking against
    v3.0.0a1, several items are now shipped: full `LlmOptions`, multimodal, file
    tools, `Decision`, compaction, sessions).
  - `about/{branding,contributors,credits}.md` — NO current equivalent → gap.
    Branding references icon assets; `docs/static/img/` has only
    `dandy_icon_white_256.png` + `favicon.png`, while `archived_docs/static/img/`
    holds the full set (color/bw/black/white 128/256/512, logo PNGs, `dandy_logo.svg`)
    — assets must be copied for the ported page to render.
    Credits is stale (lists Bottle, Httpx, Pyright, Openpyxl, include-markdown /
    table-reader plugins; current runtime deps are `pydantic`, `requests`, `blessed`,
    `python-dotenv`, with dev extras `ruff`, `ty`, `pytest`, `import-linter`, `faker`,
    `hypothesis`, and the mkdocs stack).
  - `getting_started/read_this_first.md` (35): pydantic/typing prerequisites — no
    current equivalent; `installation.md` Requirements lacks it → small gap.
  - `getting_started/introduction.md` (46): feature pitch — subsumed by `index.md` +
    `what_is_dandy.md` + the new Why Dandy page; the quantitative claims
    (0.3 ms overhead, 90% error recovery) go nowhere without v3 evidence.
  - Already covered by current pages (no action): quick_start, setup, bots, intel,
    prompts, caching, futures, decoders (→ `decision.md`, richer than archived),
    recorder (→ `recording.md`), agents (v1-era page, long superseded by
    `agent.md` + `architecture/agents.md`), handling_errors (→ `error_handling.md`).
  - Intentionally not ported: `changelog/{v0,v1,v2}_changelog.md` (history, stays
    archived), `tutorials/index.md` (superseded by nav), `tutorials/prompt_test_document.md`
    (junk, 2 lines).
- **Build state**: `mkdocs build --strict` green; `uvx codespell docs/` clean
  (2 pre-existing hits live in `AGENTS.md` / `docs/architecture/data_flow.md`);
  pytest 729 passed / 29 skipped (docs-only work, suite should be unchanged).
- `archived_docs/` is read-only per `AGENTS.md` (no edits there; copying static
  assets out of it is the only permitted interaction).
- Git identity: Nathan Johnson (nathanj@stratusadv.com), branch `v3/base`, clean tree.

## Plan

1. Why Dandy page
   - New `docs/introduction/why_dandy.md`: port the value case from
     `archived_docs/getting_started/why_use_dandy.md` (token-efficient structured
     Intel, self-correcting validation-retry loop, provider flexibility, recording /
     governance, small footprint) with every example rewritten against the verified
     v3 API (`BaseIntel`/`Bot.process`, `bot.llm.decision` for the old decoder pitch);
     quantitative claims dropped or explicitly labeled as pre-v3 measurements;
     cross-links to `what_is_dandy.md`, `principles.md`, `error_handling.md`,
     `recording.md`.
   - Done when the page exists, every example uses only verified v3 symbols, and no
     unverifiable v2 statistic appears without a "pre-v3" label.
2. Project structure page + prerequisites
   - New `docs/getting_started/project_structure.md`: port the `intelligence/`
     convention from `archived_docs/tutorials/project_structure.md` (one bot per file
     under `intelligence/bots/`, `Intel` suffix on intel classes, one file per Intel,
     prompts beside their bot), adapted to how v3 users consume the framework (user
     code composes `Bot`/`Agent`; the DDD layering binds the framework, not the user
     project) and to the `intelligence/` fixture convention in `tests/`.
   - Small edit to `docs/getting_started/installation.md`: add a short
     "Prerequisites" section (pydantic/typing familiarity) from
     `read_this_first.md`.
   - Done when both files exist/updated, examples use v3 API, and the convention
     matches `tests/` reality.
3. Example project page
   - New `docs/user_guide/example_project.md`: document the real multi-bot
     orchestration reference at `tests/application/example_project/book` — the book
     workflow (theme → title → characters → world → plot → chapters), Intel flowing
     between bots, the `create_book` composition pattern — citing the actual source
     files in the repo, replacing the archived page's dead GitHub link.
   - Done when the page exists, every cited path exists in the repo, and the pattern
     described matches `book/workflow.py` and the bot definitions.
4. Roadmap page
   - New `docs/roadmap/2026.md` with the legend inline: re-mark every item of
     `archived_docs/roadmap/2026_roadmap.md` against the verified v3.0.0a1 state
     (e.g. full OpenAI options → shipped via `LlmOptions`; vision/listening → shipped
     multimodal; file system control → shipped agent file tools; bots calling bots /
     stateful memory → shipped book example + sessions; docs update → in progress,
     this work; error handling / data compaction → shipped) and mark genuinely open
     items as such; lead with the v3.0.0a1 pre-alpha status.
   - Done when every item carries a status that is individually checkable against the
     v3.0.0a1 code, and nothing shipped is left marked open.
5. About pages + assets
   - New `docs/about/branding.md` (palette + logo, ported), `docs/about/contributors.md`
     (ported list), `docs/about/credits.md` (updated to the current v3 dependency
     stack from `pyproject.toml`: runtime `pydantic`/`requests`/`blessed`/
     `python-dotenv`, dev extras, docs stack; drop the stale v2 libraries).
   - Copy the missing icon assets (color/bw/black/white 256, logo 256, `dandy_logo.svg`)
     from `archived_docs/static/img/` into `docs/static/img/` so the branding page's
     images resolve.
   - Done when the three pages exist, every image they reference exists under
     `docs/static/img/`, and credits match `pyproject.toml`.
6. Nav + home page wiring
   - `mkdocs.yml` nav: add Why Dandy (after What is Dandy), Project Structure (after
     Configuration), Example Project (end of User Guide, after Error Handling), a new
     **Roadmap** section (after Migration), a new **About** section (after Changelog).
   - `docs/index.md`: extend the "Start here" table with rows for Why Dandy and the
     Example Project.
   - Done when every `.md` file under `docs/` appears exactly once in the nav.
7. Verification pass
   - Run the completion test (step 8); fix any broken links, nav omissions, spelling
     hits, or strict-build failures.
   - Done when the completion test passes clean and the real output is quoted below.

## Completion Test

```bash
cd /home/nathanj/PycharmProjects/dandy

# 1. Strict docs build (CI gate)
PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings NO_MKDOCS_2_WARNING=1 \
  .venv/bin/python -m mkdocs build --strict

# 2. Spelling (no new hits vs baseline)
uvx codespell docs/

# 3. Nav + link walk: every docs/*.md is in the nav exactly once, and every
#    relative link in every docs/*.md resolves to an existing file
PYTHONPATH=. .venv/bin/python - <<'EOF'
import re, sys
from pathlib import Path
docs = Path('docs')
nav = Path('mkdocs.yml').read_text()
files = {p.relative_to(docs).as_posix() for p in docs.rglob('*.md')}
in_nav = {l.strip().rsplit(' ', 1)[-1] for l in nav.splitlines() if re.match(r'\s+-\s+.*\.md', l)}
missing = files - in_nav
extra = in_nav - files
dups = len(re.findall(r'\.md', nav.split('nav:')[1].split('plugins:')[0])) != len(in_nav)
bad = []
for p in sorted(files):
    text = (docs / p).read_text()
    for m in re.finditer(r'\]\(([^)#\s]+\.md)(#[^)]*)?\)', text):
        target = (p.parent / m.group(1)).resolve()
        if not target.exists():
            bad.append(f'{p}: {m.group(1)}')
print('missing from nav:', sorted(missing) or 'none')
print('in nav but absent:', sorted(extra) or 'none')
print('broken links:', bad or 'none')
sys.exit(1 if (missing or extra or dups or bad) else 0)
EOF

# 4. Test suite unchanged (docs-only work)
DANDY_SETTINGS_MODULE=tests.dandy_settings AI_API_KEY=placeholder \
  .venv/bin/python -m pytest tests -q
```

Pass = strict build green, codespell no new hits, nav/link walk prints all "none",
pytest reports 729 passed / 29 skipped.

### Observed output (2026-11-05)

```
INFO    -  Documentation built in 1.08 seconds          # mkdocs build --strict

docs/architecture/data_flow.md:61: unparseable ==> unparsable   # pre-existing

pages: 40
nav entries: 40
missing from nav: none
in nav but absent: none
duplicate nav entries: none
broken links: none

729 passed, 29 skipped, 49 subtests passed in 9.93s
```

## Deviations

1. Fixed a pre-existing broken snippet in `docs/getting_started/installation.md`
    - What: the Verify section ran `python -c "import dandy; print(dandy.__version__)"`,
      but `dandy` does not expose `__version__` (verified: `getattr(dandy, '__version__',
      'MISSING')` → `MISSING`); replaced with
      `from dandy.shared.constants import __VERSION__`.
    - Why: the docs task's bar is accuracy, and the snippet as written raised
      `AttributeError`; it sat inside a file this plan already touched (Prerequisites
      section).
