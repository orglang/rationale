---
name: semantic-spec
description: Facilitate iterative, user-guided development of a technical specification by choosing the next consequential semantic decision, resolving ambiguity, updating the canonical document, and repeating. Use when a user is defining or revising system behavior, domain rules, protocols, requirements, or technical semantics—not for routine proofreading or documentation-only edits.
---

# Specification workflow

Use this workflow to turn an incomplete model into a specification that others can review. It is activated explicitly; repository-wide instructions do not activate it automatically. Follow [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md) for writing quality and [SEMANTIC-RULES.md](SEMANTIC-RULES.md) for questions to consider when defining behavior.

## Steps

1. **Read the project guidance.** Start with `AGENTS.md` and `DOCUMENTATION_STANDARDS.md`. Read the target document and related files. Follow existing decisions and keep each concept in its established location.
2. **Choose the next important question.** Find unresolved choices that could change behavior, constraints, ownership, ordering, error handling, or compatibility. Usually ask one focused question at a time. Combine independent questions when that makes them easier to answer, and offer options when they clarify the trade-offs.
3. **Clarify the decision.** If the answer is unclear, ask a specific follow-up instead of guessing. If the user defers it, record it as an open question and continue with unrelated work. If it conflicts with an earlier decision or source, explain the conflict and ask how to resolve it.
4. **Update the main specification.** Keep track of agreed decisions and open questions. Editing files, recording a decision in the specification, and creating a Git commit are separate actions; do not imply one happened when only another did. Update the section that explains the concept. Treat examples, summaries, and tables as supporting material: change them when they become inaccurate or during a consistency review, not after every decision. Commit when a coherent set of changes is ready, when the user asks, or at a useful milestone. Before committing, review the diff and remove unrelated changes. Do not append a conversation transcript or duplicate an existing definition.
5. **Check consistency and edge cases.** Make sure the decision fits the existing model and does not create contradictions, missing dependencies, or unhandled edge cases. Use [SEMANTIC-RULES.md](SEMANTIC-RULES.md) to check relevant aspects of the behavior. Distinguish between something that does not apply and behavior that remains undefined. Follow the documentation standards for evidence, terminology, structure, and review.
6. **Continue or wrap up.** Repeat until the user stops or the specification is ready for review. Summarize agreed decisions, open questions and their impact, and any remaining checks.

## Interaction rules

- Prioritize decisions that change behavior over wording or minor details.
- Do not reopen an agreed decision unless new evidence reveals a real conflict.
- State assumptions clearly. Ask before relying on one that could significantly change the design.
- Keep open questions visible, but continue with work that does not depend on them.
- **Group related changes into commits.** Resolve important decisions deliberately, but commit related edits together. Follow `DOCUMENTATION_STANDARDS.md` before committing. Do not rewrite Git history just to reduce the number of commits.
- **Link to commits in updates.** When mentioning a commit, include its GitHub URL or a descriptive Markdown link, not just its hash. Link each relevant commit.
- Keep implementation observations, claims from published sources, and intended language behavior distinct. Do not infer language rules from code structure alone.
- Use the existing structure, terms, status labels, and section ownership. Do not create a competing set of standards or labels.

## Ready for review

The specification is ready for review when:
- The goal and scope of the behavior being specified are clear.
- Important behavior and constraints are clear enough to check against examples, tests, or acceptance criteria.
- Known conflicts are resolved or explicitly recorded.
- Open questions that could change the design remain visible with their impact.
- Definitions and links are consistent, and each concept has a clear home.
- Remaining evidence or implementation validation is clearly distinguished from semantic decisions.

If any item is incomplete, say what remains and why instead of claiming the work is finished.
