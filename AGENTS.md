# Agent bootstrap

This file defines how repository instructions are activated. It is always loaded and does not activate other project instructions.

## Instruction activation

Project instructions are opt-in. Activate an instruction only when the user explicitly asks for it (including an unambiguous request to follow all project instructions in a stated scope), or when an already activated instruction links to it. Follow instruction links transitively and process each instruction once.

For an all-instructions request, inspect the designated instruction locations: this file, DOCUMENTATION_STANDARDS.md, and SKILL.md files under skills/. Supporting templates, rubrics, scenarios, and ordinary documentation are not instructions merely because they are present. A generic request to follow repository conventions does not activate every project instruction unless the scope is clear.

This bootstrap file is the exception: it is always loaded but does not activate other instructions. Do not add links from it to project instructions. A plain mention or an unlinked path does not activate an instruction.

## Retrospective note capture

When the user marks a note with #retro, immediately publish that note as its own top-level comment on the relevant pull request. Do not wait for a retrospective, combine notes, or put them in commit messages. If the relevant pull request is unclear, ask which one to use.

The marker authorizes note publication only. It does not activate the retrospective workflow skill or authorize repository changes.

## Scope and precedence

Instructions apply only within their stated scope and current task unless they explicitly say otherwise. Activation does not change instruction precedence or grant additional permissions. Follow the host instruction hierarchy. Surface unresolved material conflicts rather than silently choosing.

## Runtime limitations

This is an instruction-activation convention, not an access-control mechanism. A host runtime may preload or inject files independently. Do not claim an instruction was unavailable or inactive if the runtime supplied it; report the limitation instead.
