---
name: makefile_only
description: Generate or update only the Makefile for the selected packaging target using cached packaging plans.
---

# Makefile Only

Generate or update only `Makefile` for the selected target.

## Read first

Always read:
- `.claude/cache/packaging_plan.json`

Read when present:
- `.claude/cache/project_targets.json`
- `.claude/cache/project_facts.json`
- `.claude/cache/image_selection_report.json`

## Goal

Generate or update:
- `Makefile`

Do not generate:
- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `docker/entrypoint.sh`

## Required behavior

1. Use cached files only.
2. Require a valid `packaging_plan.json`.
3. Require that `Makefile` is approved by `artifacts_to_generate`.
4. Generate only useful Docker workflow targets.
5. Write `Makefile` as an actual repository file.
6. Verify the file exists after writing.

## Makefile rules

Include only useful targets such as:
- build
- up
- down
- logs
- shell
- test
- clean

Keep it minimal and aligned with the selected target and compose usage.

## Output behavior

Return only:
1. `selected_target`
2. `generated_artifacts`
3. `short_reasoning`

## Forbidden behavior

Do not:
- generate unrelated helper scripts
- include targets for artifacts not approved in the packaging plan
- print the full file in chat instead of writing it