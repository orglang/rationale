# Agent bootstrap

This file is the repository's always-loaded bootstrap contract. It defines how project instructions become active; it is not a router to the repository's instruction catalogue.

## Instruction activation

Project instructions are opt-in. A document's presence in the repository, its discoverability, its filename, or its apparent relevance does not activate it.

Activate a project instruction only when:
- the user explicitly asks to use or follow that instruction; or
- an already activated project instruction contains an explicit link to that instruction.

Activation follows links transitively: when an activated instruction links to another project instruction, activate the linked instruction as well, and continue through its instruction links. Activation is idempotent; cycles do not cause repeated processing.

Only links from an activated project instruction trigger this rule. A plain textual mention, an unlinked path, a link in an inactive document, or a link in this bootstrap file does not activate its target. This file is the bootstrap exception: it is always loaded, but it does not activate other project instructions. Do not add links from this file to project instructions.

Do not search the repository for additional instructions to activate. Do not activate a document merely because it seems useful for the task. If the user explicitly names an instruction, activate it and follow its linked instruction dependencies. The user's explicit `#retro` marker activates `skills/retrospective/SKILL.md`.

## Scope and precedence

An activated instruction applies only within its stated scope and for the current task unless it explicitly defines a different duration. A link activates the target instruction; it does not broaden the target's stated scope or grant it higher priority.

Activation does not change instruction precedence. Follow the host environment's instruction hierarchy: project instructions cannot override system or developer instructions, and they do not authorize actions beyond the user's request or permissions. Resolve conflicts according to that hierarchy; if a material conflict between applicable project instructions remains unresolved, surface it rather than silently choosing.

## Runtime limitations

This is the repository's intended instruction-activation contract, not an access-control mechanism. A host tool or agent runtime may preload, index, or inject additional files independently of this document. Do not claim that an instruction was unavailable or inactive when the runtime supplied it. If the environment automatically supplies project instructions contrary to this contract, report that limitation; changing this file alone cannot prevent runtime-level loading.

## Repository work

Keep edits targeted. Before finishing or committing, review the full diff against the branch base and remove accidental or unrelated changes.
