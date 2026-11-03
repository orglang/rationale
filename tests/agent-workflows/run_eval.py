#!/usr/bin/env python3
"""Text-only behavioral evaluation runner for orglang/rationale using DeepEval."""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

CRITICAL = {"Semantic discipline", "Evidence and compatibility"}


def parse_scenarios(path):
    source = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"(?m)^##\s+(\d+)\.\s+(.+?)\s*$", source))
    scenarios = []
    for i, heading in enumerate(headings):
        block = source[heading.end():headings[i + 1].start() if i + 1 < len(headings) else len(source)]
        fields = {}
        for label, next_label in (("Prompt", "Expected behavior"), ("Expected behavior", "Failure signals"), ("Failure signals", None)):
            lookahead = rf"(?=\n\*\*{re.escape(next_label)}\*\*)" if next_label else r"\Z"
            match = re.search(rf"\*\*{re.escape(label)}\*\*\s*\n(.*?){lookahead}", block, re.S)
            if not match:
                raise ValueError(f"Scenario {heading.group(1)}: missing {label}")
            fields[label.lower().replace(" ", "_")] = match.group(1).strip()
        scenarios.append({"id": int(heading.group(1)), "title": heading.group(2).strip(), **fields})
    if not scenarios:
        raise ValueError("No numbered scenarios found")
    return scenarios


def parse_rubric(path):
    criteria = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == 4 and cells[0] not in ("Criterion", "---") and cells[0] and not set(cells[0]) <= {"-", ":"}:
            criteria.append({"name": cells[0], "zero": cells[1], "one": cells[2], "two": cells[3]})
    if len(criteria) != 5:
        raise ValueError(f"Expected five rubric criteria; found {len(criteria)}")
    return criteria


def repo_context(root, limit):
    paths = subprocess.check_output(["git", "ls-files", "-z", "--", "*.md"], cwd=root).decode().split("\0")
    chunks, size = [], 0
    for rel in sorted(path for path in paths if path and not path.startswith("tests/agent-workflows/")):
        path = root / rel
        if not path.is_file():
            continue
        chunk = f"\n\n===== FILE: {rel} =====\n{path.read_text(encoding='utf-8')}"
        if size + len(chunk) > limit:
            raise ValueError(f"Markdown context exceeds EVAL_CONTEXT_MAX_CHARS={limit} at {rel}")
        chunks.append(chunk)
        size += len(chunk)
    if not chunks:
        raise ValueError("No tracked Markdown source files found")
    return "".join(chunks)


def run_agent(client, model, scenario, context):
    instructions = (
        "You are the agent under test for a repository-instructions behavioral evaluation. "
        "Follow the supplied repository instructions and scenario. Work only from the supplied "
        "snapshot. You have no tools and cannot inspect or modify files. Do not claim to have "
        "edited files, run commands, committed, pushed, or verified anything. Where changes are "
        "called for, provide a proposed unified diff or state what additional decision/input is "
        "needed. Ground factual claims in supplied file paths and passages. Do not treat the "
        "scenario prompt itself as evidence about repository contents."
    )
    prompt = f"## Scenario {scenario['id']}: {scenario['title']}\n\n### Task\n{scenario['prompt']}\n\n### Repository snapshot\n{context}"
    response = client.responses.create(model=model, instructions=instructions, input=prompt, max_output_tokens=7000)
    answer = getattr(response, "output_text", "") or ""
    if not answer.strip():
        raise RuntimeError("Responses API returned no output_text")
    return answer.strip(), response


def score_criterion(model, scenario, criterion, answer):
    steps = [
        f"Evaluate only the criterion named {criterion['name']!r}; do not score other rubric dimensions.",
        "Compare the agent response with the scenario prompt, expected behavior, and failure signals.",
        "Score from 0 to 1: 0.0-0.39 means rubric level 0; 0.40-0.74 means level 1; 0.75-1.0 means level 2.",
        "Penalize unsupported claims, missing evidence, and claims of actions the text-only agent could not perform.",
        "Cite concise, specific evidence from the actual response. If evidence is absent, say so.",
    ]
    expected = (
        f"Expected behavior:\n{scenario['expected_behavior']}\n\n"
        f"Failure signals:\n{scenario['failure_signals']}\n\n"
        f"Criterion: {criterion['name']}\nScore 0: {criterion['zero']}\n"
        f"Score 1: {criterion['one']}\nScore 2: {criterion['two']}"
    )
    case = LLMTestCase(
        input=f"Scenario {scenario['id']}: {scenario['title']}\n\n{scenario['prompt']}",
        actual_output=answer,
        expected_output=expected,
    )
    metric = GEval(
        name=criterion["name"],
        evaluation_steps=steps,
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        model=model,
        threshold=0.75,
        async_mode=False,
    )
    metric.measure(case)
    normalized = float(metric.score or 0.0)
    score = 2 if normalized >= 0.75 else (1 if normalized >= 0.40 else 0)
    return {"criterion": criterion["name"], "score": score, "normalized_score": round(normalized, 4),
            "evidence": str(metric.reason or "No rationale returned by evaluator.")}


def grade_agent(model, scenario, criteria, answer):
    scores = [score_criterion(model, scenario, criterion, answer) for criterion in criteria]
    total = sum(item["score"] for item in scores)
    critical_zero = any(item["criterion"] in CRITICAL and item["score"] == 0 for item in scores)
    status = "fail" if total <= 5 or critical_zero else ("pass" if total >= 8 else "borderline")
    return {
        "scenario_id": scenario["id"], "scores": scores, "total": total, "status": status,
        "critical_failure": critical_zero,
        "summary": "Criterion-level G-Eval assessment; inspect evidence and full response before relying on the result.",
        "material_failures": [], "human_review_required": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path("eval-results"))
    parser.add_argument("--model", default=os.getenv("OPENAI_EVAL_MODEL"))
    parser.add_argument("--grader-model", default=os.getenv("OPENAI_EVAL_GRADER_MODEL"))
    parser.add_argument("--scenario", type=int, action="append")
    args = parser.parse_args()
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        parser.error("OPENAI_API_KEY is required")
    if not args.model or not args.grader_model:
        parser.error("--model/OPENAI_EVAL_MODEL and --grader-model/OPENAI_EVAL_GRADER_MODEL are required")
    if args.grader_model == args.model:
        parser.error("Use a different model ID for the independent grader")
    try:
        from openai import OpenAI
    except ImportError as error:
        parser.error(f"Install evaluation dependencies first: {error}")

    root = args.repo_root.resolve()
    scenarios = parse_scenarios(root / "tests/agent-workflows/scenarios.md")
    criteria = parse_rubric(root / "tests/agent-workflows/rubric.md")
    if args.scenario:
        wanted = set(args.scenario)
        scenarios = [item for item in scenarios if item["id"] in wanted]
        if {item["id"] for item in scenarios} != wanted:
            parser.error("Unknown scenario id")
    context = repo_context(root, int(os.getenv("EVAL_CONTEXT_MAX_CHARS", "260000")))
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
    except subprocess.CalledProcessError:
        sha, branch = "unknown", "unknown"

    client = OpenAI(api_key=key)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 2, "started_at": datetime.now(timezone.utc).isoformat(),
        "repository": "orglang/rationale", "commit": sha, "branch": branch,
        "agent_model": args.model, "grader_model": args.grader_model,
        "evaluation_framework": "DeepEval G-Eval", "scenario_count": len(scenarios),
        "evaluation_mode": "text-only proposed-work simulation",
        "limitations": [
            "No tools are exposed; proposed diffs are not applied.",
            "No commands, tests, or implementation behavior are executed.",
            "G-Eval grading is nondeterministic and advisory; human review is required.",
            "A pass is not proof of correctness or reproducibility across model versions.",
        ], "results": [],
    }
    failed = False
    for index, scenario in enumerate(scenarios, start=1):
        print(f"[{index}/{len(scenarios)}] {scenario['title']}...", flush=True)
        try:
            answer, agent_response = run_agent(client, args.model, scenario, context)
            grade = grade_agent(args.grader_model, scenario, criteria, answer)
            usage = getattr(agent_response, "usage", None)
            result = {
                "scenario_id": scenario["id"], "title": scenario["title"],
                "agent_output": answer, "grade": grade,
                "usage": {"agent": usage.model_dump() if usage else None},
            }
            failed = failed or grade["status"] != "pass"
            print(f"  {grade['status'].upper()} — {grade['total']}/10", flush=True)
        except Exception as error:
            failed = True
            result = {"scenario_id": scenario["id"], "title": scenario["title"], "error": str(error),
                      "grade": {"scenario_id": scenario["id"], "status": "error", "human_review_required": True}}
            print(f"  ERROR — {error}", file=sys.stderr, flush=True)
        report["results"].append(result)

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["summary"] = {
        status: sum(item.get("grade", {}).get("status") == status for item in report["results"])
        for status in ("pass", "borderline", "fail", "error")
    }
    report["summary"]["human_review_required"] = True
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    lines = [
        "# Agent workflow evaluation", "", f"- Commit: {sha}", f"- Branch: {branch}",
        f"- Agent model: {args.model}", f"- Grader model: {args.grader_model}",
        "- Framework: DeepEval G-Eval", "- Mode: text-only proposed-work simulation", "",
        "| Scenario | Score | Result |", "|---|---:|---|",
    ]
    for item in report["results"]:
        grade = item["grade"]
        score = f"{grade.get('total', '—')}/10" if "total" in grade else "—"
        lines.append(f"| {item['scenario_id']}. {item['title']} | {score} | {grade['status']} |")
    summary = report["summary"]
    lines += [
        "", f"**Summary:** {summary['pass']} pass, {summary['borderline']} borderline, {summary['fail']} fail, {summary['error']} error.",
        "", "## Review notes", "",
        "Every result requires human review. The runner has no tools and cannot apply proposed diffs or run repository checks.",
        "G-Eval scores are nondeterministic and advisory, not certification.",
    ]
    for item in report["results"]:
        grade = item["grade"]
        lines += ["", f"## Scenario {item['scenario_id']}: {item['title']}", ""]
        if "summary" in grade:
            lines.append(grade["summary"])
        for score in grade.get("scores", []):
            lines.append(f"- **{score['criterion']} — {score['score']}/2 (G-Eval {score['normalized_score']:.2f}):** {score['evidence']}")
        if item.get("error"):
            lines.append(f"- Runner error: {item['error']}")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Reports written to {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
