---
name: makefile_only
description: Generate or update only the Makefile for the selected packaging target using cached draft plans and resolver-owned activation.
---

# Makefile Only

Generate or update only `Makefile` for the selected target.

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

- `.claude/cache/packaging_plan.json`

Read when present:

- `.claude/cache/project_targets.json`
- `.claude/cache/project_facts.json`
- `.claude/cache/image_selection_report.json`
- `.claude/cache/project_fingerprint.json`

---

## Goal

Generate or update only:

- `Makefile`

Do not generate:

- `Dockerfile`
- `.dockerignore`
- compose files
- `docker/entrypoint.sh`
- command wrapper scripts
- host output dirs

unless the user explicitly expands scope.

---

## Draft vs resolved plan rule

Do not generate `Makefile` from draft hints alone.

Only generate it when it is present in:

- `resolved_plan.artifacts_to_generate`

If `resolved_plan` is missing or unusable for the current request, resolve the request first.

---

## Required behavior

1. Use cached files only.
2. Require a valid draft `packaging_plan.json`.
3. Require that `Makefile` is active in the resolved artifact set.
4. Generate only useful Docker workflow targets aligned with the resolved scope.
5. Write `Makefile` as an actual repository file.
6. Verify the file exists after writing.

---

## Resolver requirement

If `resolved_plan` is missing or unusable for the current request, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "<user request>"
```

Then re-read `packaging_plan.json`.

If `Makefile` is not present in `resolved_plan.artifacts_to_generate`, do not generate it unless the user explicitly overrides the resolved scope.

---

## Makefile rules

Include only useful targets aligned with the resolved scope, such as:

- build
- up
- down
- logs
- shell
- test
- clean

Keep it minimal.
Do not include targets for artifacts or modes not active in the resolved plan.

---

## Tool usage — mandatory

- use the Read tool to read required cache files
- use the Write tool to create or update `Makefile`
- use the Bash tool to run:
  ```bash
  ls -la Makefile
  ```
  after writing to confirm it exists
- never print the full file in chat as a substitute for writing it

---

## Output behavior

Return only:

1. `selected_target`
2. `generated_artifacts`
3. `short_reasoning`

---

## Forbidden behavior

Do not:

- generate unrelated helper scripts
- include targets for artifacts not active in the resolved plan
- print the full file in chat instead of writing it
