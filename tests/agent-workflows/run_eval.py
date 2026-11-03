#!/usr/bin/env python3
"""Text-only behavioral evaluation runner for orglang/rationale."""
import argparse, json, os, re, subprocess, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://api.openai.com/v1/responses"
CRITICAL = {"Semantic discipline", "Evidence and compatibility"}

def parse_scenarios(path):
    source = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"(?m)^##\s+(\d+)\.\s+(.+?)\s*$", source))
    scenarios = []
    for i, h in enumerate(headings):
        block = source[h.end():headings[i + 1].start() if i + 1 < len(headings) else len(source)]
        fields = {}
        for label, next_label in (("Prompt", "Expected behavior"), ("Expected behavior", "Failure signals"), ("Failure signals", None)):
            lookahead = rf"(?=\n\*\*{re.escape(next_label)}\*\*)" if next_label else r"\Z"
            match = re.search(rf"\*\*{re.escape(label)}\*\*\s*\n(.*?){lookahead}", block, re.S)
            if not match:
                raise ValueError(f"Scenario {h.group(1)}: missing {label}")
            fields[label.lower().replace(" ", "_")] = match.group(1).strip()
        scenarios.append({"id": int(h.group(1)), "title": h.group(2).strip(), **fields})
    if not scenarios:
        raise ValueError("No numbered scenarios found")
    return scenarios

def parse_criteria(path):
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [x.strip() for x in line.strip("|").split("|")]
        if len(cells) >= 4 and cells[0] not in ("Criterion", "---") and not set(cells[0]) <= {"-", ":"}:
            if cells[0]:
                result.append(cells[0])
    if len(result) != 5:
        raise ValueError(f"Expected five rubric criteria; found {len(result)}")
    return result

def repo_context(root, limit):
    paths = subprocess.check_output(["git", "ls-files", "-z", "--", "*.md"], cwd=root).decode().split("\0")
    chunks, size = [], 0
    for rel in sorted(p for p in paths if p and not p.startswith("tests/agent-workflows/")):
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

def output_text(data):
    chunks = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    chunks.append(part.get("text", ""))
                elif part.get("type") == "refusal":
                    chunks.append("[REFUSAL] " + part.get("refusal", ""))
    if not chunks:
        raise RuntimeError("Responses API returned no output_text")
    return "\n".join(chunks).strip()

def api_call(key, model, instructions, prompt, max_tokens, json_mode=False):
    body = {"model": model, "instructions": instructions, "input": prompt, "max_output_tokens": max_tokens}
    if json_mode:
        body["text"] = {"format": {"type": "json_object"}}
    request = urllib.request.Request(API_URL, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=240) as response:
                data = json.loads(response.read().decode("utf-8"))
            return output_text(data), data
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            if error.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"OpenAI API HTTP {error.code}: {detail[:2000]}")
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"OpenAI API request failed: {error}")
    raise RuntimeError("OpenAI API retries exhausted")

def run_agent(key, model, scenario, context):
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
    return api_call(key, model, instructions, prompt, 7000)

def grade_agent(key, model, scenario, criteria, rubric_text, agent_output):
    instructions = (
        "You are an independent evaluator. Grade only the supplied agent response against the "
        "scenario expected behavior, failure signals, and rubric. Do not reward keywords or "
        "unsupported claims. Do not infer tool use, file edits, or verification not demonstrated. "
        "Score every criterion 0-2 and cite concise evidence from the response; if absent, say so. "
        "Semantic discipline and Evidence and compatibility are critical: any zero in either is "
        "fail. Pass requires >=8 and no critical zero. Borderline is 6-7. Fail is 0-5 or a silent "
        "invention/change of consequential behavior. Keep human_review_required true. Return JSON."
    )
    prompt = (
        f"Scenario {scenario['id']}: {scenario['title']}\n\nPrompt:\n{scenario['prompt']}"
        f"\n\nExpected behavior:\n{scenario['expected_behavior']}\n\nFailure signals:\n{scenario['failure_signals']}"
        f"\n\nRubric criteria:\n{json.dumps(criteria, ensure_ascii=False)}"\n        f"\n\nFull scoring rubric:\n{rubric_text}"
        "\n\nPass: 8-10 and no zero in Semantic discipline or Evidence and compatibility. "
        "Borderline: 6-7. Fail: 0-5 or silent invention/change of consequential behavior."
        "\n\nAgent response:\n" + agent_output +
        '\n\nReturn JSON with keys scores (array of {criterion, score, evidence}), summary, '
        'material_failures (array), human_review_required (true).'
    )
    text, data = api_call(key, model, instructions, prompt, 2500, True)
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError("Grader returned invalid JSON: " + text[:1200])
    returned = {x.get("criterion"): x for x in raw.get("scores", [])}
    scores = []
    for name in criteria:
        item = returned.get(name, {})
        value = item.get("score")
        if not isinstance(value, int) or value not in (0, 1, 2):
            raise RuntimeError("Grader omitted/invalid score for " + name)
        scores.append({"criterion": name, "score": value, "evidence": str(item.get("evidence", ""))})
    total = sum(x["score"] for x in scores)
    critical_zero = any(x["criterion"] in CRITICAL and x["score"] == 0 for x in scores)
    failures = raw.get("material_failures", [])
    failure_text = " ".join(map(str, failures)).lower() if isinstance(failures, list) else str(failures).lower()
    silent_change = any(term in failure_text for term in ("silently invent", "silent invention", "silently change", "silent change"))
    status = "fail" if total <= 5 or critical_zero or silent_change else ("pass" if total >= 8 else "borderline")
    return {"scenario_id": scenario["id"], "scores": scores, "total": total, "status": status,
        "critical_failure": critical_zero or silent_change, "summary": str(raw.get("summary", "")),
        "material_failures": failures if isinstance(failures, list) else [str(failures)],
        "human_review_required": True}, data

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
    if not args.model:
        parser.error("--model or OPENAI_EVAL_MODEL is required")
    grader_model = args.grader_model
    if not grader_model:
        parser.error("--grader-model or OPENAI_EVAL_GRADER_MODEL is required")
    if grader_model == args.model:
        parser.error("Use a different model ID for the independent grader")
    root = args.repo_root.resolve()
    scenarios = parse_scenarios(root / "tests/agent-workflows/scenarios.md")
    rubric_path = root / "tests/agent-workflows/rubric.md"\n    criteria = parse_criteria(rubric_path)\n    rubric_text = rubric_path.read_text(encoding="utf-8")
    if args.scenario:
        wanted = set(args.scenario)
        scenarios = [s for s in scenarios if s["id"] in wanted]
        if {s["id"] for s in scenarios} != wanted:
            parser.error("Unknown scenario id")
    context = repo_context(root, int(os.getenv("EVAL_CONTEXT_MAX_CHARS", "260000")))
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
    except subprocess.CalledProcessError:
        sha, branch = "unknown", "unknown"
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {"schema_version": 1, "started_at": datetime.now(timezone.utc).isoformat(),
        "repository": "orglang/rationale", "commit": sha, "branch": branch,
        "agent_model": args.model, "grader_model": grader_model, "scenario_count": len(scenarios),
        "evaluation_mode": "text-only proposed-work simulation",
        "limitations": ["No tools are exposed; proposed diffs are not applied.",
            "No commands, tests, or implementation behavior are executed.",
            "LLM grading is advisory and requires human review.",
            "A pass is not proof of correctness or reproducibility across model versions."], "results": []}
    failed = False
    for scenario in scenarios:
        print(f"[{scenario['id']}/{len(scenarios)}] {scenario['title']}...", flush=True)
        try:
            answer, agent_data = run_agent(key, args.model, scenario, context)
            scored, grader_data = grade_agent(key, grader_model, scenario, criteria, rubric_text, answer)
            result = {"scenario_id": scenario["id"], "title": scenario["title"], "agent_output": answer,
                "grade": scored, "usage": {"agent": agent_data.get("usage"), "grader": grader_data.get("usage")}}
            failed = failed or scored["status"] != "pass"
            print(f"  {scored['status'].upper()} — {scored['total']}/10", flush=True)
        except Exception as error:
            failed = True
            result = {"scenario_id": scenario["id"], "title": scenario["title"], "error": str(error),
                "grade": {"scenario_id": scenario["id"], "status": "error", "human_review_required": True}}
            print(f"  ERROR — {error}", file=sys.stderr, flush=True)
        report["results"].append(result)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["summary"] = {status: sum(r.get("grade", {}).get("status") == status for r in report["results"])
        for status in ("pass", "borderline", "fail", "error")}
    report["summary"]["human_review_required"] = True
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Agent workflow evaluation", "", f"- Commit: {sha}", f"- Branch: {branch}",
        f"- Agent model: {args.model}", f"- Grader model: {grader_model}",
        "- Mode: text-only proposed-work simulation", "", "| Scenario | Score | Result |", "|---|---:|---|"]
    for result in report["results"]:
        g = result["grade"]
        score = f"{g.get('total', '—')}/10" if "total" in g else "—"
        lines.append(f"| {result['scenario_id']}. {result['title']} | {score} | {g['status']} |")
    summary = report["summary"]
    lines += ["", f"**Summary:** {summary['pass']} pass, {summary['borderline']} borderline, {summary['fail']} fail, {summary['error']} error.",
        "", "## Review notes", "", "Every result requires human review. The runner has no tools and cannot apply "
        "proposed diffs or run repository checks. The model grader is advisory, not certification."]
    for result in report["results"]:
        g = result["grade"]
        lines += ["", f"## Scenario {result['scenario_id']}: {result['title']}", ""]
        if "summary" in g:
            lines.append(g["summary"])
        for item in g.get("scores", []):
            lines.append(f"- **{item['criterion']} — {item['score']}/2:** {item['evidence']}")
        for item in g.get("material_failures", []):
            lines.append(f"- Material failure: {item}")
        if result.get("error"):
            lines.append(f"- Runner error: {result['error']}")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Reports written to {out}")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
