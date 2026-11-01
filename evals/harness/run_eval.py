import argparse
import csv
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from common import (
    REPO_ROOT,
    USAGE_PARSERS,
    agent_exit_code,
    build_prompt,
    cost_usd,
    diff_stat,
    docker_run_agent,
    docker_run_check,
)
from report import render_report

ALL_AGENTS = ['dandy', 'opencode', 'pi', 'crush']
RESULTS_FIELDS = [
    'agent',
    'run',
    'pass',
    'wall_s',
    'input_tokens',
    'output_tokens',
    'cost_usd',
    'agent_exit',
    'timed_out',
    'diff_stat',
    'judge_total',
    'note',
]


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=RESULTS_FIELDS, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the four-agent CLI eval')
    parser.add_argument('--agents', default='all', help='"all" or comma list of dandy,opencode,pi,crush')
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--stamp', default=None)
    parser.add_argument('--no-judge', action='store_true')
    args = parser.parse_args()

    agents = ALL_AGENTS if args.agents == 'all' else [a.strip() for a in args.agents.split(',')]
    stamp = args.stamp or datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    run_root = REPO_ROOT / 'evals' / 'runs' / stamp
    run_root.mkdir(parents=True, exist_ok=True)

    prompt = build_prompt()
    task_statement = (REPO_ROOT / 'evals' / 'task' / 'project' / 'TASK.md').read_text()

    results: list[dict] = []
    lock = threading.Lock()

    def record(row: dict) -> None:
        with lock:
            results.append(row)
            write_csv(run_root / 'results.csv', results)

    def run_agent(agent: str) -> None:
        for run_index in range(1, args.runs + 1):
            run_dir = run_root / f'{agent}-run{run_index}' / 'workdir'
            run_dir.mkdir(parents=True, exist_ok=True)
            run_name = f'dandy-eval-{stamp.replace("-", "")}-{agent}-{run_index}'
            row = {'agent': agent, 'run': run_index, 'pass': False, 'note': ''}
            try:
                agent_result = docker_run_agent(agent, run_name, run_dir, prompt)
                row['wall_s'] = agent_result['wall_s']
                row['timed_out'] = agent_result['timed_out']
                (run_dir / 'docker.stderr').write_text(agent_result['stderr'])
                if agent_result['exit_code'] not in (0, None):
                    tail = agent_result['stderr'].strip().splitlines()[-3:]
                    row['note'] = f'docker exit {agent_result["exit_code"]}: ' + ' | '.join(tail)
                row['agent_exit'] = agent_exit_code(run_dir)
                row['diff_stat'] = diff_stat(run_dir)
                row['pass'] = docker_run_check(f'{run_name}-check', run_dir)
                if agent_result['timed_out']:
                    row['note'] = 'harness timeout'
            except Exception as exc:
                row['note'] = f'error: {exc}'
            row.setdefault('wall_s', '')
            row.setdefault('timed_out', '')
            row.setdefault('agent_exit', '')
            row.setdefault('diff_stat', '')
            row.setdefault('judge_total', '')
            in_tokens, out_tokens = USAGE_PARSERS[agent](run_dir)
            row['input_tokens'] = in_tokens
            row['output_tokens'] = out_tokens
            row['cost_usd'] = cost_usd(in_tokens, out_tokens)
            record(row)
            print(f'[{agent} run {run_index}] pass={row["pass"]} wall={row.get("wall_s")}s '
                  f'tokens={in_tokens}+{out_tokens} ${row["cost_usd"]} note={row["note"]!r}')

    with ThreadPoolExecutor(max_workers=len(agents)) as pool:
        list(pool.map(run_agent, agents))

    if not args.no_judge:
        for row in results:
            run_dir = run_root / f"{row['agent']}-run{row['run']}" / 'workdir'
            try:
                from judge import judge_run

                judged = judge_run(run_dir, task_statement)
                row['judge_total'] = judged['total']
                (run_dir / 'judge.json').write_text(json.dumps(judged, indent=2))
                print(f"[{row['agent']} run {row['run']}] judge total={judged['total']}")
            except Exception as exc:
                row['note'] = f'{row["note"]}; judge error: {exc}'.strip('; ')
            write_csv(run_root / 'results.csv', results)

    render_report(run_root, results, stamp)
    print(f'report: {run_root / "report.md"}')


if __name__ == '__main__':
    main()
