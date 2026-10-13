---
name: skill-creator
description: Create or update a LessChaos skill. Use for skill authoring, questions about Skill format and locations, or turning a repeated workflow into a skill.
---

# Skill Creator

Create skills that give the agent useful, non-obvious guidance for tasks that recur. SKILL.md contains instructions to read and follow. Supporting scripts use the normal approved tool execution path.

## What a skill is

One folder containing one `SKILL.md`:

```
<skills-root>/<skill-name>/SKILL.md
```

## Write the SKILL.md

Start with YAML frontmatter:

```yaml
---
name: my-skill
description: What this skill does and when to use it.
---
```

Rules:

- For portable names, match the folder name and use 1–64 lowercase letters, digits, or single hyphens, starting and ending with a letter or digit. Plugin skills require this format; independent skills may fall back to the folder name when `name` is missing.
- `description` must be non-empty. Keep it concise and state what the skill does and when it applies. Before opening the file, the model sees the name, description, and path.
- Omit `disable-model-invocation` for normal skills. Set it to `true` only for skills available solely through explicit `/name` invocation.
- Unrecognized frontmatter fields have no LessChaos runtime meaning. Preserve existing metadata when editing a skill.

Then write the body as direct instructions to the agent:

- Lead with what to do, not background. Cut anything a competent agent already knows.
- Prefer a short checklist or numbered steps over prose. Keep the whole file focused; it is read in full when used.
- Include one small example only when it removes ambiguity.
- Reference supporting files (scripts, templates) placed in the same folder by relative path.
- Describe required external capabilities and recovery steps in the body.

## Choose the location

Ask the user when intent is unclear; by default:

- Personal, reusable across chats and projects for the local user: `~/.agents/skills/<name>/`.
- Project-scoped, shared with everyone who clones the repo: `<project>/.agents/skills/<name>/`. The project must be trusted to load these skills.

An ordinary chat's working directory holds task files and is not a project skill root. Personal and project skills stay available across LessChaos account changes; plugin skills follow the current account's global plugin enablement in every chat.

Same-name precedence: project, personal, enabled plugin, then built-in. Never write into the built-in `~/.lesschaos/skills/.system` directory or a plugin's managed release.

## Explicit invocation (optional)

In LessChaos, a skill is invoked by naming it as a word starting with "/" anywhere in a message (message start or mid-sentence, whitespace-separated). The user's words stay verbatim and the loaded skill body is appended after them. Write direct instructions and let the model interpret the user's arguments; there is no placeholder substitution.

## After writing

Skills are rediscovered at the start of each Run; the current Run keeps its frozen catalog. Report the written path and suggest trying `/name` with a real task on the next Run. For a project skill, use a chat associated with that trusted project.
