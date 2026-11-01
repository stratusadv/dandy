import json
import sqlite3
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGE = 'dandy-eval:latest'
LABEL = 'dandy-eval=1'
AGENT_TIMEOUT_SECONDS = 1260
CHECK_TIMEOUT_SECONDS = 300

TURBO_INPUT_PER_MTOK = 1.0
TURBO_OUTPUT_PER_MTOK = 5.0


def build_prompt() -> str:
    task_md = (REPO_ROOT / 'evals' / 'task' / 'project' / 'TASK.md').read_text()
    return (
        'You are working in the current directory (/workdir), a Python project. '
        'Read TASK.md in the current directory and make the project behave exactly as '
        'TASK.md specifies. Work only inside the current directory. When you are done, '
        'reply with a short summary of what you changed.\n\n'
        f'TASK.md:\n\n{task_md}'
    )


def docker_run_agent(agent: str, run_name: str, run_dir: Path, prompt: str) -> dict:
    mounts = [
        f'{REPO_ROOT / "evals" / "task" / "project"}:/task:ro',
        f'{REPO_ROOT / "evals" / "docker" / "entrypoints"}:/entrypoints:ro',
        f'{run_dir}:/workdir',
    ]
    env = ['AI_API_KEY', 'AI_API_HOST', f'AGENT_PROMPT={prompt}']
    if agent == 'dandy':
        mounts += [
            f'{REPO_ROOT / "dandy"}:/dandy-lib/dandy:ro',
            f'{REPO_ROOT / "evals" / "harness" / "dandy_settings.py"}:/eval/dandy_settings.py:ro',
            f'{REPO_ROOT / "evals" / "harness" / "usage_proxy.py"}:/eval/usage_proxy.py:ro',
        ]
    if agent == 'pi':
        mounts += [f'{REPO_ROOT / "evals" / "docker" / "pi-stratus.ts"}:/eval/pi-stratus.ts:ro']
    cmd = [
        'docker',
        'run',
        '--rm',
        '--name',
        run_name,
        '--label',
        LABEL,
    ]
    for env_arg in env:
        cmd += ['-e', env_arg]
    for mount in mounts:
        cmd += ['-v', mount]
    cmd += [
        '-w',
        '/workdir',
        IMAGE,
        'bash',
        f'/entrypoints/{agent}.sh',
    ]
    started = time.time()
    timed_out = False
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=AGENT_TIMEOUT_SECONDS)
        result = {'exit_code': proc.returncode, 'stderr': proc.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(['docker', 'rm', '-f', run_name], capture_output=True, text=True)
        result = {'exit_code': -1, 'stderr': 'harness timeout; container force-removed'}
    result['wall_s'] = round(time.time() - started, 1)
    result['timed_out'] = timed_out
    return result


def docker_run_check(run_name: str, run_dir: Path) -> bool:
    cmd = [
        'docker',
        'run',
        '--rm',
        '--name',
        run_name,
        '--label',
        LABEL,
        '-v',
        f'{run_dir}:/workdir',
        '-v',
        f'{REPO_ROOT / "evals" / "task" / "hidden_tests"}:/hidden-tests:ro',
        '-v',
        f'{REPO_ROOT / "evals" / "docker" / "entrypoints"}:/entrypoints:ro',
        '-w',
        '/workdir',
        IMAGE,
        'bash',
        '/entrypoints/check.sh',
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CHECK_TIMEOUT_SECONDS)
    return proc.returncode == 0


def agent_exit_code(run_dir: Path) -> int | None:
    agent_exit_file = run_dir / 'agent.exit'
    if not agent_exit_file.exists():
        return None
    line = agent_exit_file.read_text().strip()
    return int(line.split('=', 1)[1]) if line.startswith('AGENT_EXIT=') else None


def diff_stat(run_dir: Path) -> str:
    stat_file = run_dir / 'final.diff.stat'
    if not stat_file.exists():
        return ''
    lines = stat_file.read_text().strip().splitlines()
    return lines[-1] if lines else ''


def cost_usd(input_tokens: int, output_tokens: int) -> float:
    return round(input_tokens / 1e6 * TURBO_INPUT_PER_MTOK + output_tokens / 1e6 * TURBO_OUTPUT_PER_MTOK, 6)


def parse_dandy_usage(run_dir: Path) -> tuple[int, int]:
    in_tokens = out_tokens = 0
    usage_file = run_dir / 'usage.jsonl'
    if usage_file.exists():
        for line in usage_file.read_text().splitlines():
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            in_tokens += entry.get('prompt_tokens', 0)
            out_tokens += entry.get('completion_tokens', 0)
    return in_tokens, out_tokens


def parse_opencode_usage(run_dir: Path) -> tuple[int, int]:
    in_tokens = out_tokens = 0
    transcript = run_dir / 'transcript.json'
    if not transcript.exists():
        return in_tokens, out_tokens
    for line in transcript.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        part = event.get('part') or {}
        if part.get('type') == 'step-finish':
            tokens = part.get('tokens') or {}
            in_tokens += tokens.get('input', 0) + tokens.get('reasoning', 0)
            out_tokens += tokens.get('output', 0)
    return in_tokens, out_tokens


def parse_pi_usage(run_dir: Path) -> tuple[int, int]:
    in_tokens = out_tokens = 0
    transcript = run_dir / 'transcript.json'
    if not transcript.exists():
        return in_tokens, out_tokens
    for line in transcript.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') != 'message_end':
            continue
        usage = (event.get('message') or {}).get('usage') or {}
        in_tokens += usage.get('input', 0)
        out_tokens += usage.get('output', 0)
    return in_tokens, out_tokens


def parse_crush_usage(run_dir: Path) -> tuple[int, int]:
    db_path = run_dir / '.crush-data' / 'crush.db'
    if not db_path.exists():
        return 0, 0
    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        try:
            row = conn.execute(
                'select coalesce(sum(prompt_tokens), 0), coalesce(sum(completion_tokens), 0) from sessions'
            ).fetchone()
        finally:
            conn.close()
        return int(row[0]), int(row[1])
    except sqlite3.DatabaseError:
        return 0, 0


USAGE_PARSERS = {
    'dandy': parse_dandy_usage,
    'opencode': parse_opencode_usage,
    'pi': parse_pi_usage,
    'crush': parse_crush_usage,
}
