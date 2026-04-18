---
name: dockerfile_only
description: Generate or update only the Dockerfile for the selected packaging target using cached plans and image selection.
---

# Dockerfile Only

Generate or update only `Dockerfile` for the selected target.

## Read first

Always read:
- `.claude/cache/project_facts.json`
- `.claude/cache/project_targets.json`
- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Read when present:
- `.claude/cache/project_graph.json`
- `.claude/cache/project_closure.json`

## Goal

Generate or update:
- `Dockerfile`

Do not generate:
- `.dockerignore`
- `compose.yml`
- `Makefile`
- `docker/entrypoint.sh`

## Required behavior

1. Use cached files only.
2. Require a valid `packaging_plan.json`.
3. Require a valid `image_selection_report.json`.
4. Generate only the `Dockerfile`.
5. Write it as an actual repository file.
6. Verify the file exists after writing.

## Dockerfile rules

- Tailor it only to the selected target.
- Use the selected application image from `packaging_plan.json`.
- Respect target runtime, framework, and run/build commands from cache.
- Keep it production-oriented.
- Use non-root runtime users where practical.
- Expose the correct port from cached packaging data.

## Output behavior

Return only:
1. `selected_target`
2. `selected_image`
3. `generated_artifacts`
4. `short_reasoning`

## Forbidden behavior

Do not:
- generate any other Docker-related files
- rescan the full repository when cache is usable
- invent extra services or environments
- print the full file in chat instead of writing it