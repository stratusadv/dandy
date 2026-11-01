import csv
import json
from pathlib import Path

AGENTS = ['dandy', 'opencode', 'pi', 'crush']


def _read_csv(run_root: Path) -> list[dict]:
    with open(run_root / 'results.csv') as f:
        return list(csv.DictReader(f))


def _last_check_line(run_dir: Path) -> str:
    check_log = run_dir / 'check.log'
    if not check_log.exists():
        return '(checker never ran)'
    lines = check_log.read_text().strip().splitlines()
    tail = [line for line in lines[-3:] if line.strip()]
    return ' | '.join(tail)


def _load_judge(run_dir: Path) -> dict | None:
    judge_file = run_dir / 'judge.json'
    if not judge_file.exists():
        return None
    try:
        return json.loads(judge_file.read_text())
    except ValueError:
        return None


def render_report(run_root: Path, rows: list[dict], stamp: str) -> None:
    out = []
    out.append(f'# CLI eval: dandy vs opencode vs pi vs crush\n')
    out.append(f'- stamp: `{stamp}`')
    out.append('- task: stockroom (spec-compliance: 4 planted bugs + 1 missing command, 15 hidden tests)')
    out.append('- model: `stratus.turbo` for all four agents (same endpoint, same model, same prompt)')
    out.append('- runs per agent: 3 independent containers; judge: dandy `JudgeBot` on `stratus.thinking`')
    out.append('- cost = tokens x stratus.turbo list price ($1.00/$5.00 per Mtok)\n')

    out.append('## Aggregate\n')
    out.append('| agent | passed | wall (mean) | cost (total) | judge (mean) |')
    out.append('|---|---|---|---|---|')
    for agent in AGENTS:
        agent_rows = [row for row in rows if row['agent'] == agent]
        if not agent_rows:
            continue
        passed = sum(1 for row in agent_rows if row['pass'] == 'True')
        walls = [float(row['wall_s']) for row in agent_rows if row.get('wall_s')]
        mean_wall = sum(walls) / len(walls) if walls else 0
        total_cost = sum(float(row['cost_usd'] or 0) for row in agent_rows)
        judges = [float(row['judge_total']) for row in agent_rows if row.get('judge_total')]
        mean_judge = sum(judges) / len(judges) if judges else 0
        out.append(
            f'| {agent} | {passed}/{len(agent_rows)} | {mean_wall:.0f}s | ${total_cost:.4f} | '
            f'{mean_judge:.1f} |'
        )

    out.append('\n## Per run\n')
    out.append('| agent | run | pass | wall_s | in_tok | out_tok | cost_usd | agent_exit | diff_stat | judge | note |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for row in rows:
        out.append(
            '| {agent} | {run} | {pass} | {wall_s} | {input_tokens} | {output_tokens} | {cost_usd} '
            '| {agent_exit} | {diff_stat} | {judge_total} | {note} |'.format(**row)
        )

    out.append('\n## Run detail\n')
    for row in rows:
        run_dir = run_root / f"{row['agent']}-run{row['run']}" / 'workdir'
        out.append(f"### {row['agent']} run {row['run']}\n")
        out.append(f"- pass: **{row['pass']}**, wall {row.get('wall_s')}s, "
                   f"tokens {row.get('input_tokens')}+{row.get('output_tokens')}, "
                   f"cost ${row.get('cost_usd')}")
        out.append(f"- checker: `{_last_check_line(run_dir)}`")
        out.append(f"- diff stat: `{row.get('diff_stat') or '(none)'}`")
        if row.get('note'):
            out.append(f"- note: {row['note']}")
        judge = _load_judge(run_dir)
        if judge:
            out.append(
                f"- judge: correctness={judge['correctness']} approach={judge['approach']} "
                f"quality={judge['quality']} no_gaming={judge['no_gaming']} total={judge['total']}"
            )
            out.append(f"- judge notes: {judge['notes']}")
        out.append('')

    out.append('## Caveats\n')
    out.append('- All runs share one model (stratus.turbo), one prompt, and identical task trees; '
               'container images are identical. Wall time is measured around `docker run`.')
    out.append('- Permission behavior differs by agent: pi has no permission gates by design; '
               'crush `run` mode executes tools without prompts; opencode used `--auto`; '
               'dandy RunCommandTool runs without confirmation. None of the agents had to ask.')
    out.append('- dandy token usage is measured by a localhost proxy that logs the API `usage` '
               'field; the other agents report usage in their own transcripts.')
    out.append('- The judge (stratus.thinking) is a single LLM scoring pass over the diff, the '
               'checker output, and the agent final message; treat its numbers as one opinion.')

    (run_root / 'report.md').write_text('\n'.join(out) + '\n')
