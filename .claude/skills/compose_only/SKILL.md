---
name: compose_only
description: Generate or update only compose.yml for the selected packaging target using cached plans and image selection.
---

# Compose Only

Generate or update only `compose.yml` for the selected target.

## Read first

Always read:
- `.claude/cache/project_targets.json`
- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Read when present:
- `.claude/cache/project_facts.json`
- `.claude/cache/project_graph.json`
- `.claude/cache/project_closure.json`

## Goal

Generate or update:
- `compose.yml`

Do not generate:
- `Dockerfile`
- `.dockerignore`
- `Makefile`
- `docker/entrypoint.sh`

## Required behavior

1. Use cached files only.
2. Require a valid `packaging_plan.json`.
3. Require that `compose.yml` is approved by `artifacts_to_generate`.
4. Use only services listed in `compose_services`.
5. Use only selected service images from `packaging_plan.json`.
6. Write `compose.yml` as an actual repository file.
7. Verify the file exists after writing.

## Compose rules

- Include only services actually required by the selected target.
- Use only selected service images from the plan/report.
- Define only necessary volumes, environment, ports, and dependencies.
- Do not invent extra infra or deployment layers.

## Output behavior

Return only:
1. `selected_target`
2. `selected_images`
3. `generated_artifacts`
4. `short_reasoning`

## Forbidden behavior

Do not:
- generate nginx configs
- generate CI/CD or production ops files
- invent extra services not present in the plan
- print the full file in chat instead of writing it