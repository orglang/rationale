---
name: semantic-spec
description: Facilitate iterative, user-guided development of a technical specification by identifying consequential semantic decisions, resolving ambiguity, updating the canonical document, and repeating. Use when a user is defining or revising system behavior, domain rules, protocols, requirements, or technical semantics—not for routine proofreading or documentation-only edits.
---

# Specification workflow

Use this workflow to make an incomplete behavior model precise enough to review. Activate it when the task matches the description above or the user explicitly asks for it; repository-wide instructions alone do not activate it.

Read [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md) for documentation quality criteria and [`SEMANTIC-RULES.md`](SEMANTIC-RULES.md) for questions that may reveal missing behavior.

## Steps

1. **Read the context.** Start with `AGENTS.md` and `DOCUMENTATION_STANDARDS.md`. Read the target document and relevant sources. Identify the canonical location for the behavior and any existing decisions or conflicts.
2. **Choose a consequential question.** Look for unresolved choices that could change behavior, constraints, ownership, ordering, error handling, or compatibility. Usually ask one focused question at a time; combine independent questions when helpful and offer options when they clarify trade-offs.
3. **Resolve uncertainty.** Ask a focused follow-up rather than guessing. If the user defers a decision, record it as an open question and continue with independent work. If an answer conflicts with an earlier decision or source, explain the conflict and ask how to resolve it.
4. **Update the canonical specification.** Record agreed decisions and open questions in the section that owns the concept. Update examples, summaries, and tables when they become inaccurate or during a consistency review. Do not append a conversation transcript or duplicate a definition. Editing a file, recording a decision, and committing changes are separate actions; report each accurately. Commit related changes together when they form a coherent unit, at a useful milestone, or when requested. Review the diff and remove unrelated edits before committing.
5. **Check the consequences.** Check relevant items in [`SEMANTIC-RULES.md`](SEMANTIC-RULES.md). Look for contradictions, missing dependencies, and consequential edge cases. Distinguish behavior that does not apply from behavior that remains undefined. Keep implementation observations, published claims, and intended behavior distinct.
6. **Continue or wrap up.** Repeat with the next consequential question until the user stops or the specification is ready for review. Summarize decisions captured, open questions and their impact, and remaining validation work.

## Interaction rules

- Prioritize decisions that change behavior over wording or minor details.
- Do not reopen an agreed decision unless new evidence reveals a meaningful conflict.
- State assumptions clearly. Ask before relying on an assumption that could materially change the design.
- Keep open questions visible, but continue with work that does not depend on them.
- Use the existing document structure, terminology, status labels, and section ownership. Do not create parallel standards or taxonomies.
- When reporting a commit, include its GitHub URL or a descriptive Markdown link, not just its hash. Link each relevant commit.

## Efficiency and decision discipline

- **Derive before asking.** Apply consequences of agreed decisions and established rules by analogy where their scope permits. Ask only when materially different interpretations remain.
- **Separate semantics from implementation evidence.** Track unresolved language behavior separately from unverified implementation behavior. Missing code or tests do not make an agreed semantic contract undecided.
- **Use a minimal research plan.** Read required instructions and canonical sources first. Search related files in batches around explicit hypotheses; repeat searches only when new evidence warrants them.
- **Report at decision boundaries.** Summarize decisions, changes, verification, and remaining questions at meaningful milestones; avoid repeating unchanged findings.
- **Prefer the smallest sufficient process.** Do not add checklists or documents when existing guidance covers the need. Match validation effort to the change and automate mechanical checks where practical.

## Ready for review

The specification is ready for review when:
- Its goal and scope are clear.
- Important behavior and constraints can be checked against examples, tests, or acceptance criteria.
- Known conflicts are resolved or explicitly recorded.
- Open questions that could change the design remain visible, along with their impact.
- Definitions and links are consistent, with a clear canonical location for each concept.
- Remaining evidence gathering or implementation validation is distinguished from semantic decisions.

If any criterion is unmet, state what remains and why instead of claiming the work is finished.
