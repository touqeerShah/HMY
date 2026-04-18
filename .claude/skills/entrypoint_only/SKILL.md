---
name: entrypoint_only
description: Generate or update only docker/entrypoint.sh for the selected packaging target when startup orchestration is required.
---

# Entrypoint Only

Generate or update only `docker/entrypoint.sh` for the selected target.

## Read first

Always read:
- `.claude/cache/packaging_plan.json`

Read when present:
- `.claude/cache/project_facts.json`
- `.claude/cache/project_targets.json`
- `.claude/cache/image_selection_report.json`

## Goal

Generate or update:
- `docker/entrypoint.sh`

Do not generate:
- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `Makefile`

## Required behavior

1. Use cached files only.
2. Require a valid `packaging_plan.json`.
3. Require that `docker/entrypoint.sh` is approved by `artifacts_to_generate`.
4. Generate it only if `entrypoint_required` is true.
5. Write it as an actual repository file.
6. Verify the file exists after writing.

## Entrypoint rules

Generate only when startup orchestration is actually required, such as:
- waiting for dependencies
- migrations
- startup bootstrapping
- role-based process startup

Keep it minimal.

## Output behavior

Return only:
1. `selected_target`
2. `generated_artifacts`
3. `short_reasoning`

## Forbidden behavior

Do not:
- generate entrypoint scripts when not required
- invent extra startup logic not justified by the plan
- print the full file in chat instead of writing it