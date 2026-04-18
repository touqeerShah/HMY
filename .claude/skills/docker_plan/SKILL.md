---
name: docker_plan
description: Generate or refresh packaging_plan.json and image_selection_report.json from cached project structure and docker-hub MCP.
---

# Docker Plan

Plan Docker packaging for the current repository without generating Docker artifact files.

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

## Goal

Refresh and validate:
- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Do not generate:
- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `Makefile`
- `docker/entrypoint.sh`

## Workflow

1. Start from cached structure only.
2. Select the packaging target.
3. Scope work to the selected target and its closure.
4. Resolve image choices through `docker-hub` MCP.
5. Write or refresh:
   - `.claude/cache/image_selection_report.json`
   - `.claude/cache/packaging_plan.json`
6. Verify both files match the selected target.

## Target rules

- If exactly one dockerizable target exists, select it automatically.
- If multiple dockerizable targets exist, infer the target from the request if possible.
- Ask only if the target is genuinely ambiguous.

## Image rules

- Prefer official images.
- Avoid `latest`.
- Prefer compatibility and maintainability over smallest size.
- For Next.js production, prefer Debian slim or bookworm-slim unless there is a strong, target-specific reason not to.

## Output behavior

Return only:
1. `selected_target`
2. `selected_images`
3. `written_plan_files`
4. `short_reasoning`

## Forbidden behavior

Do not:
- rescan the full repository when cache is usable
- generate Docker artifact files
- invent additional apps, services, or environments
- silently skip MCP when image selection is required