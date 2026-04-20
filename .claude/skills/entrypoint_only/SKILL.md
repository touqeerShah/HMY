---
name: entrypoint_only
description: Generate or update only docker/entrypoint.sh for the selected packaging target when startup orchestration is required by the resolved plan.
---

# Entrypoint Only

Generate or update only `docker/entrypoint.sh` for the selected target.

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

- `.claude/cache/project_facts.json`
- `.claude/cache/project_targets.json`
- `.claude/cache/image_selection_report.json`
- `.claude/cache/project_fingerprint.json`

---

## Goal

Generate or update only:

- `docker/entrypoint.sh`

Do not generate:

- `Dockerfile`
- `.dockerignore`
- compose files
- `Makefile`

unless the user explicitly expands scope.

---

## Draft vs resolved plan rule

Do not generate `docker/entrypoint.sh` from draft hints alone.

Only generate it when both are true:

- it is present in `resolved_plan.artifacts_to_generate`
- startup orchestration is actually required by the resolved scope

If `resolved_plan` is missing or unusable for the current request, resolve the request first.

---

## Required behavior

1. Use cached files only.
2. Require a valid draft `packaging_plan.json`.
3. Require that `docker/entrypoint.sh` is active in the resolved artifact set.
4. Generate it only when startup orchestration is justified.
5. Write it as an actual repository file.
6. Verify the file exists after writing.

---

## Resolver requirement

If `resolved_plan` is missing or unusable for the current request, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "<user request>"
```

Then re-read `packaging_plan.json`.

If `docker/entrypoint.sh` is not present in `resolved_plan.artifacts_to_generate`, do not generate it unless the user explicitly overrides the resolved scope.

---

## Entrypoint rules

Generate only when startup orchestration is actually required, such as:

- waiting for dependencies
- migrations
- startup bootstrapping
- role-based process startup

Keep it minimal.
Do not invent startup logic not justified by the resolved plan.

---

## Tool usage — mandatory

- use the Read tool to read required cache files
- use the Write tool to create or update `docker/entrypoint.sh`
- use the Bash tool to run:
  ```bash
  ls -la docker/entrypoint.sh
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

- generate entrypoint scripts when not required
- invent extra startup logic not justified by the resolved plan
- print the full file in chat instead of writing it
