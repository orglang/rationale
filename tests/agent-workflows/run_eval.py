#!/usr/bin/env python3
"""Run repository-instruction scenarios against the local OpenCode CLI."""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import queue
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

CRITICAL = {"Semantic discipline", "Evidence and compatibility"}
SCENARIOS = Path("tests/agent-workflows/scenarios.jsonl")
RUBRIC = Path("tests/agent-workflows/rubric.md")


def command(args, cwd, timeout=3600, check=True):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(f"{args[0]} exited {result.returncode}:\n{result.stdout}\n{result.stderr}")
    return result


def load_scenarios(path):
    rows, ids = [], set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        meta = row.get("additional_metadata") or {}
        if not row.get("input") or not row.get("expected_output") or not all(k in meta for k in ("id", "title", "failure_signals")):
            raise ValueError(f"{path}:{number}: invalid scenario record")
        sid = int(meta["id"])
        if sid in ids or not isinstance(meta["failure_signals"], list) or not meta["failure_signals"]:
            raise ValueError(f"{path}:{number}: duplicate id or invalid failure_signals")
        ids.add(sid)
        rows.append({"id": sid, "title": meta["title"], "prompt": row["input"],
                     "expected": row["expected_output"], "failure_signals": meta["failure_signals"]})
    if not rows:
        raise ValueError("No scenarios found")
    return sorted(rows, key=lambda x: x["id"])


def parse_rubric(path):
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [x.strip() for x in line.strip("|").split("|")]
        if len(cells) == 4 and cells[0] not in ("Criterion", "---") and cells[0] and not set(cells[0]) <= {"-", ":"}:
            result.append(dict(name=cells[0], zero=cells[1], one=cells[2], two=cells[3]))
    if len(result) != 5:
        raise ValueError(f"Expected five rubric criteria, got {len(result)}")
    return result


def events_and_message(raw):
    events, messages = [], []
    def walk(value):
        if isinstance(value, dict):
            if value.get('type') == 'text' and isinstance(value.get('text'), str): messages.append(value['text'])
            for child in value.values(): walk(child)
        elif isinstance(value, list):
            for child in value: walk(child)
    for line in raw.splitlines():
        try: event = json.loads(line)
        except json.JSONDecodeError: continue
        events.append(event)
        walk(event)
    return events, '\n'.join(dict.fromkeys(messages)).strip()


def opencode(prompt, cwd, model=None, agent=None, auto=False, timeout=3600, label="OpenCode", trace_path=None):
    args = ['opencode', 'run', '--format', 'json', '--dir', str(cwd)]
    if model: args += ['--model', model]
    if agent: args += ['--agent', agent]
    if auto: args.append('--auto')

    print(f"    {label}: starting (timeout {timeout}s)", flush=True)
    started = time.monotonic()
    process = subprocess.Popen(args + [prompt], cwd=cwd, text=True, bufsize=1,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = [], []
    event_count = tool_count = 0
    trace_handle = trace_path.open("w", encoding="utf-8") if trace_path else None
    messages = queue.Queue()

    def read_stream(stream, name):
        try:
            for line in iter(stream.readline, ''):
                messages.put((name, line))
        finally:
            messages.put((name, None))

    threads = [
        threading.Thread(target=read_stream, args=(process.stdout, "stdout"), daemon=True),
        threading.Thread(target=read_stream, args=(process.stderr, "stderr"), daemon=True),
    ]
    for thread in threads:
        thread.start()

    finished_streams = set()
    while len(finished_streams) < 2:
        elapsed = time.monotonic() - started
        if elapsed > timeout:
            if trace_handle:
                trace_handle.close()
            process.kill()
            process.wait()
            raise subprocess.TimeoutExpired(args, timeout, output=''.join(output), stderr=''.join(errors))
        try:
            name, line = messages.get(timeout=15)
        except queue.Empty:
            print(f"    {label}: still running ({int(elapsed)}s elapsed; {event_count} events, {tool_count} tool calls)", flush=True)
            continue
        if line is None:
            finished_streams.add(name)
            continue
        if name == "stdout":
            output.append(line)
            if trace_handle:
                trace_handle.write(line)
                trace_handle.flush()
            try:
                event = json.loads(line)
                event_count += 1
                event_type = event.get("type", "event")
                part = event.get("part") or {}
                part_type = part.get("type", "") if isinstance(part, dict) else ""
                if event_type in ("tool_use", "tool_result") or part_type == "tool":
                    tool_count += 1
                if event_type in ("step_start", "step_finish", "tool_use", "tool_result") or part_type == "tool":
                    detail = part.get("tool") or event.get("tool") or part_type
                    print(f"    {label}: {event_type} {detail}".rstrip(), flush=True)
                elif event_type == "text":
                    print(f"    {label}: text output received", flush=True)
            except (json.JSONDecodeError, AttributeError):
                pass
        else:
            errors.append(line)
            if line.strip():
                print(f"    {label} [stderr]: {line.rstrip()[:240]}", flush=True)

    if trace_handle:
        trace_handle.close()
    returncode = process.wait()
    for thread in threads:
        thread.join()
    class Result:
        pass
    result = Result()
    result.returncode = returncode
    result.stdout = ''.join(output)
    result.stderr = ''.join(errors)
    print(f"    {label}: finished in {int(time.monotonic() - started)}s (exit {returncode})", flush=True)
    events, message = events_and_message(result.stdout)
    return result, events, message

def run_scenario(root, scenario, model, agent, timeout):
    parent = Path(tempfile.mkdtemp(prefix=f"opencode-eval-{scenario['id']}-"))
    tree = parent / "repo"
    try:
        print(f"    Preparing isolated worktree for scenario {scenario['id']}...", flush=True)
        command(["git", "worktree", "add", "--detach", str(tree), "HEAD"], root, 120)
        prompt = (
            "You are evaluated against this repository's actual instructions. Read and follow "
            "applicable instructions and skills. Work in this checkout: inspect files, edit files, "
            "and run relevant checks as the task requires. Do not merely propose a diff. Do not "
            "commit, push, or modify anything outside this worktree. Never claim an action or check "
            "unless you actually performed it. If a consequential decision is missing, do not invent "
            "it; record the unresolved decision and continue independent work. Report classification, "
            "decisions, files changed, and checks performed.\n\n"
            f"## Scenario {scenario['id']}: {scenario['title']}\n\n{scenario['prompt']}"
        )
        result, events, message = opencode(prompt, tree, model, agent=agent, auto=True, timeout=timeout, label="Agent")
        status = command(["git", "status", "--short"], tree, check=False).stdout
        diff = command(["git", "diff", "--no-ext-diff", "--binary", "HEAD"], tree, check=False).stdout
        untracked = command(["git", "ls-files", "--others", "--exclude-standard"], tree, check=False).stdout
        extra = []
        for rel in untracked.splitlines():
            path = tree / rel
            if path.is_file():
                extra.append(f"\n===== UNTRACKED: {rel} =====\n{path.read_text(encoding='utf-8', errors='replace')}")
        return {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
                "message": message, "git_status": status, "diff": diff,
                "untracked": "".join(extra)}
    finally:
        if tree.exists():
            command(["git", "worktree", "remove", "--force", str(tree)], root, check=False)
        shutil.rmtree(parent, ignore_errors=True)


def grade(scenario, criteria, execution, rubric, root, model, agent, timeout, trace_path):
    evidence = {
        "scenario": scenario, "agent_final_response": execution["message"],
        "agent_exit_code": execution["exit_code"], "git_status": execution["git_status"],
        "patch": execution["diff"], "untracked_files": execution["untracked"],
        "stderr": execution["stderr"][-10000:],
    }
    prompt = (
        "Strictly evaluate the actual local agent execution using the rubric and evidence. "
        "Score each of the five criteria 0, 1, or 2. Require concrete evidence; do not infer "
        "actions from claims. Return ONLY JSON: {scores:[{criterion,score,evidence}],total,status,"
        "critical_failure,summary}. Pass=8-10 and no zero in Semantic discipline or Evidence and "
        "compatibility. Borderline=6-7 or any critical zero. Fail=0-5 or consequential invented "
        "behavior.\n\nRUBRIC:\n" + rubric + "\n\nEVIDENCE:\n" +
        json.dumps(evidence, ensure_ascii=False)
    )
    # Grading is evidence-only; disable tools for the selected grader agent.
    with tempfile.TemporaryDirectory(prefix="opencode-grader-") as grader_dir:
        grader_dir = Path(grader_dir)
        config = {
            "$schema": "https://opencode.ai/config.json",
            "agent": {
                agent: {
                    "permission": {
                        "bash": "deny",
                        "read": "deny",
                        "edit": "deny",
                        "glob": "deny",
                        "grep": "deny",
                        "list": "deny",
                        "task": "deny",
                        "webfetch": "deny",
                        "websearch": "deny",
                        "skill": "deny",
                        "lsp": "deny",
                        "todowrite": "deny",
                        "question": "deny",
                        "external_directory": "deny"
                    }
                }
            }
        }
        (grader_dir / "opencode.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\\n",
            encoding="utf-8")
        result, events, message = opencode(
            prompt, grader_dir, model, agent=agent, auto=False,
            timeout=timeout, label="Grader", trace_path=trace_path)
    trace_path.write_text(result.stdout, encoding="utf-8")
    start, end = message.find("{"), message.rfind("}")
    if result.returncode or start < 0 or end <= start:
        raise RuntimeError(f"Grader failed: {result.stderr}\n{message}")
    value = json.loads(message[start:end + 1])
    expected = {c["name"] for c in criteria}
    if {x["criterion"] for x in value["scores"]} != expected or any(x["score"] not in (0, 1, 2) for x in value["scores"]):
        raise ValueError("Invalid grader score schema")
    total = sum(x["score"] for x in value["scores"])
    critical = any(x["criterion"] in CRITICAL and x["score"] == 0 for x in value["scores"])
    value.update(total=total, critical_failure=critical,
                 status="fail" if total <= 5 or critical else ("pass" if total >= 8 else "borderline"),
                 human_review_required=True)
    return value, result.stdout


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--output-dir", type=Path, default=Path("eval-results"))
    p.add_argument("--scenario", type=int, action="append")
    p.add_argument("--model", help="Optional OpenCode model override (provider/model)")
    p.add_argument("--grader-model", help="Optional grader model override (provider/model)")
    p.add_argument("--agent", help="Optional OpenCode agent for scenario execution")
    p.add_argument("--grader-agent", default="plan", help="Read-only grader agent (default: plan)")
    p.add_argument("--timeout", type=int, default=3600,
                   help="Timeout in seconds for each scenario agent invocation (default: 3600)")
    p.add_argument("--grader-timeout", type=int, default=600,
                   help="Timeout in seconds for each grader invocation (default: 600)")
    args = p.parse_args()
    if args.timeout < 1 or args.grader_timeout < 1:
        p.error("--timeout and --grader-timeout must be positive")
    root = args.repo_root.resolve()
    if not (root / ".git").exists() and not (root / ".git").is_file():
        p.error("--repo-root must be a Git checkout")
    try:
        command(["opencode", "--version"], root, 30)
    except (FileNotFoundError, RuntimeError) as error:
        p.error(f"Install OpenCode CLI and configure a provider first: {error}")
    scenarios = load_scenarios(root / SCENARIOS)
    criteria = parse_rubric(root / RUBRIC)
    if args.scenario:
        selected = set(args.scenario)
        scenarios = [s for s in scenarios if s["id"] in selected]
        if {s["id"] for s in scenarios} != selected:
            p.error("Unknown scenario id")
    sha = command(["git", "rev-parse", "HEAD"], root).stdout.strip()
    branch = command(["git", "branch", "--show-current"], root).stdout.strip()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rubric_text = (root / RUBRIC).read_text(encoding="utf-8")
    report = {"schema_version": 3, "started_at": datetime.now(timezone.utc).isoformat(),
              "repository": "orglang/rationale", "commit": sha, "branch": branch,
              "mode": "local OpenCode CLI; isolated detached Git worktree per scenario",
              "agent_model_override": args.model, "grader_model_override": args.grader_model,
              "agent": args.agent, "grader_agent": args.grader_agent,
              "agent_timeout_seconds": args.timeout,
              "grader_timeout_seconds": args.grader_timeout,
              "scenario_count": len(scenarios), "results": [],
              "limitations": ["OpenCode grading is advisory; human review is required.",
                              "Unless --grader-model is set, agent and grader may use the same configured model.",
                              "Runs start from HEAD; uncommitted changes in the caller's checkout are excluded.",
                              "Agent edits are captured as patches and never applied to the caller's checkout."]}
    failed = False
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/{len(scenarios)}] {scenario['title']}", flush=True)
        execution = None
        try:
            execution = run_scenario(root, scenario, args.model, args.agent, args.timeout)
            (output / f"scenario-{scenario['id']}-agent.jsonl").write_text(
                execution["stdout"], encoding="utf-8")
            print("    Collecting agent changes and preparing grading evidence...", flush=True)
            result_grade, grader_trace = grade(
                scenario, criteria, execution, rubric_text, root, args.grader_model,
                args.grader_agent, args.grader_timeout, output / f"scenario-{scenario['id']}-grader.jsonl")
            item = {"scenario_id": scenario["id"], "title": scenario["title"],
                    "agent_output": execution["message"], "agent_exit_code": execution["exit_code"],
                    "git_status": execution["git_status"], "diff": execution["diff"],
                    "untracked_files": execution["untracked"], "grade": result_grade}
            failed |= result_grade["status"] != "pass" or execution["exit_code"] != 0
            print(f"  {result_grade['status'].upper()} — {result_grade['total']}/10", flush=True)
        except Exception as error:
            failed = True
            item = {"scenario_id": scenario["id"], "title": scenario["title"],
                    "error": str(error), "grade": {"status": "error", "human_review_required": True}}
            if execution is not None:
                item.update(agent_output=execution["message"], agent_exit_code=execution["exit_code"],
                            git_status=execution["git_status"], diff=execution["diff"],
                            untracked_files=execution["untracked"])
            if isinstance(error, subprocess.TimeoutExpired):
                print("  TIMEOUT — OpenCode invocation exceeded its configured limit; continuing to next scenario.", file=sys.stderr, flush=True)
            else:
                print(f"  ERROR — {error}", file=sys.stderr, flush=True)
        report["results"].append(item)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["summary"] = {s: sum(x.get("grade", {}).get("status") == s for x in report["results"])
                         for s in ("pass", "borderline", "fail", "error")}
    report["summary"]["human_review_required"] = True
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Local OpenCode behavioral evaluation", "", f"- Commit: {sha}", f"- Branch: {branch}",
             "- Mode: local OpenCode CLI; isolated Git worktrees", "", "| Scenario | Score | Result |",
             "|---|---:|---|"]
    for item in report["results"]:
        g = item["grade"]
        lines.append(f"| {item['scenario_id']}. {item['title']} | {g.get('total', '—')}/10 | {g['status']} |")
    s = report["summary"]
    lines += ["", f"**Summary:** {s['pass']} pass, {s['borderline']} borderline, {s['fail']} fail, {s['error']} error.",
              "", "Review the JSON report and CLI traces. Scores are advisory; human review is required."]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Reports written to {output}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
