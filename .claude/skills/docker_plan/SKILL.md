---
name: docker_plan
description: Generate or refresh the draft packaging plan and image selection report from cached project structure and docker-hub MCP without generating Docker artifact files.
---

# Docker Plan

Plan Docker packaging for the current repository without generating Docker artifact files.

## CRITICAL — read cache first

Before anything else, read these exact cache files first:

```bash
cat .claude/cache/project_facts.json
cat .claude/cache/packaging_plan.json
cat .claude/cache/image_selection_report.json
```

If a required cache file is missing, run bootstrap and re-read them.

---

## Read first

Always read:

- `.claude/cache/project_facts.json`
- `.claude/cache/project_graph.json`
- `.claude/cache/project_targets.json`

Read when present:

- `.claude/cache/project_closure.json`
- `.claude/cache/project_chunks.jsonl`
- `.claude/cache/project_fingerprint.json`
- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

---

## Goal

Refresh and validate:

- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Do not generate Docker artifact files.

---

## Draft-plan rule

`packaging_plan.json` is now a draft-first document unless resolver mode has been run.

This skill should primarily:

- generate or refresh the draft packaging plan
- generate or refresh the image selection report
- not generate final Docker artifacts
- not activate final artifact output on its own

If the user explicitly asks for planning only, stop at draft/report refresh.

If the user asks for full packaging, use `dockerize_project` instead.

---

## Workflow

1. Start from cached structure only.
2. Select the packaging target.
3. Scope work to the selected target and its closure.
4. Refresh draft packaging state:
   - `plan-packaging`
5. Refresh image report:
   - `write-image-report`
6. Verify both files match the selected target.
7. Do not generate Docker artifacts.

---

## Target rules

- If exactly one dockerizable target exists, select it automatically.
- If multiple dockerizable targets exist, infer the target from the request if possible.
- Ask only if the target is genuinely ambiguous.

---

## Image rules

- Prefer official images.
- Avoid `latest`.
- Prefer compatibility and maintainability over smallest size.
- For Next.js production, prefer Debian slim or bookworm-slim unless there is a strong, target-specific reason not to.
- Image report must separate support from activation.

---

## Output behavior

Return only:

1. `selected_target`
2. `selected_images`
3. `written_plan_files`
4. `short_reasoning`

---

## Forbidden behavior

Do not:

- rescan the full repository when cache is usable
- generate Docker artifact files
- invent additional apps, services, roles, or environments
- silently skip MCP when image selection is required
