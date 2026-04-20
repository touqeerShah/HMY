---
name: compose_only
description: Generate or update only resolved compose files for the selected packaging target using cached draft plans, resolver-owned activation, and MCP-backed image selection.
---

# Compose Only

Generate or update only compose files for the selected target.

## CRITICAL — read cache first

Before anything else, read these exact cache files first:

```bash
cat .claude/cache/project_facts.json
cat .claude/cache/packaging_plan.json
cat .claude/cache/image_selection_report.json
```

Do NOT run `find`, broad `ls`, or manual repository discovery before reading cache.
Do NOT scan the repository manually.
Use cache as the source of truth for structure, draft packaging state, and resolved activation state.

If a required cache file is missing, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode bootstrap
```

Then re-read the cache files above.

---

## Read first

Always read:

- `.claude/cache/project_targets.json`
- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Read when present:

- `.claude/cache/project_facts.json`
- `.claude/cache/project_graph.json`
- `.claude/cache/project_closure.json`
- `.claude/cache/project_fingerprint.json`

Do not use manual repository discovery as a substitute for reading cache.

---

## Goal

Generate or update only resolved compose files for the selected target.

Likely compose files may include:

- `compose.yml`
- `compose.live.yml`
- `compose.rebuild.yml`

Do not generate:

- `Dockerfile`
- `.dockerignore`
- `Makefile`
- `docker/entrypoint.sh`
- command wrapper scripts
- host output dirs

unless the user explicitly asks to expand scope.

---

## Draft vs resolved plan rule

`packaging_plan.json` is not assumed to be packaging-ready just because it exists.

It contains:

- draft sections:
  - `capabilities`
  - `defaults`
  - `suggested_artifacts`
  - `suggested_modes`
  - `suggested_roles`
- resolved section:
  - `resolved_plan`

Rules:

- do not generate compose files from draft hints alone
- only generate compose files from:
  - `resolved_plan.compose_files`
  - or `resolved_plan.artifacts_to_generate`

If `resolved_plan` is missing, stale, conflicted, or invalid for the current request, resolve the request first.

---

## Required behavior

1. Use cached files only.
2. Require a valid draft `packaging_plan.json`.
3. Require a valid `image_selection_report.json`.
4. If the request needs activation, run resolver mode first.
5. Generate only compose files present in the resolved plan.
6. Use only services actually required by the selected target.
7. Use only selected service images from the current image report / resolved image state.
8. Write compose files as actual repository files.
9. Verify each written compose file exists.

---

## Resolver requirement

If `resolved_plan` is missing or unusable for the current request, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "<user request>"
```

Then re-read:

- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Only generate compose files present in the resolved plan.

If no compose files are present in `resolved_plan.compose_files`, do not generate them unless the user explicitly overrides the resolved scope.

---

## Compose rules

- Include only services actually required by the selected target.
- Use only selected service images from the image report / resolved state.
- Define only necessary volumes, environment, ports, and dependencies.
- Do not invent extra infra, deployment layers, or unrelated profiles.
- Respect resolved workflow modes:
  - `live-bind` may justify `compose.live.yml`
  - `rebuild-image` may justify `compose.rebuild.yml`
- Do not generate mode overlays unless they are active in the resolved plan.

---

## Image selection rule

Do not blindly trust stale image state from cache.

Before writing compose files, re-check relevant application and service images through MCP when available.

If MCP-selected images materially differ from cached image state:

- refresh `image_selection_report.json`
- refresh or re-resolve packaging state if needed
- only then write compose files

When MCP is available, do not proceed using stale cached image selection.

---

## Create vs update behavior

For each resolved compose file:

1. determine whether it already exists
2. create it if missing
3. update it if present
4. verify it exists after the operation

Do not generate unrelated Docker artifacts in this skill.

---

## Tool usage — mandatory

You must use tools, not chat output.

Required tool behavior:

- use the Read tool to read all required cache files
- use the Write tool to create or update only resolved compose files
- use the Bash tool to run `ls -la <file>` after each write to confirm it exists
- never print full compose contents in chat as a substitute for writing them

---

## Output behavior

Return only:

1. `selected_target`
2. `selected_images`
3. `generated_artifacts`
4. `short_reasoning`

Keep the response brief and execution-focused.

---

## Forbidden behavior

Do not:

- generate nginx configs
- generate CI/CD or production ops files
- invent extra services not present in the resolved plan
- generate compose files from draft hints alone
- print the full file in chat instead of writing it
