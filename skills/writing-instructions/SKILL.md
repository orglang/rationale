---
name: writing-instructions
description: Refactor or create agent-facing instructions, skills, and instruction routing in this repository. Use when changing AGENTS.md, skill frontmatter or descriptions, instruction boundaries, shared rules, or cross-references.
---

# Instruction design

Use this workflow when changing instructions consumed by coding agents. Keep the rules here; repository-wide behavior belongs in `AGENTS.md`, technical-documentation quality criteria in `DOCUMENTATION_STANDARDS.md`, and task-specific workflows in their owning skills.

## Refactor by behavior

1. Inventory instruction files and the conditions that make each one load.
2. Assign each rule one canonical home. Replace repeated explanations with a link when the target is reliably reachable; keep a short summary only when it changes behavior at the point of use.
3. Split a document only when a distinct task branch needs different guidance, or when a sequence boundary meaningfully reduces premature completion. Every new module adds navigation and maintenance cost.
4. Keep always-loaded instructions short. Put specialized procedures behind explicit, task-matched pointers; state both what the target contains and when to read it.
5. Co-locate a concept's rules, exceptions, and completion criteria. Do not scatter one concept across multiple modules.
6. Prefer direct positive instructions that name the desired behavior. Retain prohibitions only for hard guardrails, paired with the required alternative when possible.
7. Remove stale rules, repeated meanings, and statements that do not change agent behavior. Do not remove meaningful constraints merely to reduce word count.

## Module boundaries

- `AGENTS.md` owns repository-wide rules and routing. It should identify the right module, not reproduce its contents.
- `DOCUMENTATION_STANDARDS.md` owns recurring standards for technical and research documentation.
- A skill owns its specific workflow and the conditions for invoking it.
- Subject-matter documents own domain facts and semantics; instruction refactoring must not silently rewrite them.
- Put genuinely shared reference in one reachable canonical file. Do not create a skill solely to hold a few generic sentences or to mirror another module.

## Validation

Before reporting completion:

- Review the full diff against the branch base; confirm only intended instruction files changed.
- Follow every changed local link and verify its target and heading.
- Search edited rules for duplicate or conflicting statements in other instruction modules.
- Check that every specialized module has a clear invocation trigger and that its pointer is specific enough to reach it when needed.
- Report checks actually performed; do not imply behavioral testing when only text and links were reviewed.
