#!/usr/bin/env python3
"""Run repository-instruction scenarios against the local Codex CLI."""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
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
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(event)
        item = event.get("item") or {}
        if item.get("type") in ("agent_message", "message") and item.get("text"):
            messages.append(item["text"])
    return events, "\n\n".join(messages).strip()


def codex(prompt, cwd, model=None, read_only=False, timeout=3600):
    args = ["codex", "exec", "--json"]
    args += ["--sandbox", "read-only"] if read_only else ["--full-auto"]
    if model:
        args += ["--model", model]
    result = command(args + [prompt], cwd, timeout, check=False)
    events, message = events_and_message(result.stdout)
    return result, events, message


def run_scenario(root, scenario, model, timeout):
    parent = Path(tempfile.mkdtemp(prefix=f"codex-eval-{scenario['id']}-"))
    tree = parent / "repo"
    try:
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
        result, events, message = codex(prompt, tree, model, timeout=timeout)
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


def grade(scenario, criteria, execution, rubric, root, model, timeout, trace_path):
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
    result, events, message = codex(prompt, root, model, read_only=True, timeout=timeout)
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
    p.add_argument("--model", help="Optional Codex model override")
    p.add_argument("--grader-model", help="Optional read-only grader model override")
    p.add_argument("--timeout", type=int, default=3600)
    args = p.parse_args()
    root = args.repo_root.resolve()
    if not (root / ".git").exists() and not (root / ".git").is_file():
        p.error("--repo-root must be a Git checkout")
    try:
        command(["codex", "--version"], root, 30)
    except (FileNotFoundError, RuntimeError) as error:
        p.error(f"Install and authenticate Codex CLI first: {error}")
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
              "mode": "local Codex CLI; isolated detached Git worktree per scenario",
              "agent_model_override": args.model, "grader_model_override": args.grader_model,
              "scenario_count": len(scenarios), "results": [],
              "limitations": ["Codex grading is advisory; human review is required.",
                              "Unless --grader-model is set, agent and grader may use the same configured model.",
                              "Runs start from HEAD; uncommitted changes in the caller's checkout are excluded.",
                              "Agent edits are captured as patches and never applied to the caller's checkout."]}
    failed = False
    for i, scenario in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] {scenario['title']}...", flush=True)
        execution = None
        try:
            execution = run_scenario(root, scenario, args.model, args.timeout)
            (output / f"scenario-{scenario['id']}-agent.jsonl").write_text(
                execution["stdout"], encoding="utf-8")
            result_grade, grader_trace = grade(
                scenario, criteria, execution, rubric_text, root, args.grader_model,
                args.timeout, output / f"scenario-{scenario['id']}-grader.jsonl")
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
            print(f"  ERROR — {error}", file=sys.stderr, flush=True)
        report["results"].append(item)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["summary"] = {s: sum(x.get("grade", {}).get("status") == s for x in report["results"])
                         for s in ("pass", "borderline", "fail", "error")}
    report["summary"]["human_review_required"] = True
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Local Codex behavioral evaluation", "", f"- Commit: {sha}", f"- Branch: {branch}",
             "- Mode: local Codex CLI; isolated Git worktrees", "", "| Scenario | Score | Result |",
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
