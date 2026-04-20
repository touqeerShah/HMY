---
name: dockerfile_only
description: Generate or update only the Dockerfile for the selected packaging target using cached draft plans, resolver-owned activation, and MCP-backed image selection.
---

# Dockerfile Only

Generate or update only `Dockerfile` for the selected target.

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

- `.claude/cache/project_facts.json`
- `.claude/cache/project_targets.json`
- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Read when present:

- `.claude/cache/project_graph.json`
- `.claude/cache/project_closure.json`
- `.claude/cache/project_fingerprint.json`

Do not use manual repository discovery as a substitute for reading cache.

---

## Goal

Generate or update only:

- `Dockerfile`

Do not generate:

- `.dockerignore`
- `compose.yml`
- `compose.live.yml`
- `compose.rebuild.yml`
- `Makefile`
- `docker/entrypoint.sh`
- command wrapper scripts
- host output dirs

---

## Draft vs resolved plan rule

`packaging_plan.json` is not assumed to be a final packaging-ready plan.

It contains:

- `capabilities`
- `defaults`
- `suggested_artifacts`
- `suggested_modes`
- `suggested_roles`
- `resolved_plan`

Rules:

- do not generate `Dockerfile` directly from `suggested_artifacts`
- do not treat draft hints as active generation input
- only use `resolved_plan` to determine whether `Dockerfile` should be generated in the current request scope

If the request is packaging-relevant and `resolved_plan` is missing or stale, resolve the request first.

---

## Required behavior

1. Use cached files only.
2. Require a valid draft `packaging_plan.json`.
3. Require a valid `image_selection_report.json`.
4. If the request needs activation, run resolver mode first.
5. Generate or update only `Dockerfile`.
6. Write it as an actual repository file.
7. Verify the file exists after writing.

---

## Resolver requirement

If `resolved_plan` is missing, stale, conflicted, or invalid for the current request, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "<user request>"
```

Then re-read:

- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Use `resolved_plan` as the only valid source for active artifact generation.

If `Dockerfile` is not present in:

- `resolved_plan.artifacts_to_generate`

do not generate it unless the user explicitly overrides the resolved scope.

---

## Dockerfile rules

- Tailor it only to the selected target.
- Use the selected application image from the image report / resolved image state.
- Respect target runtime, framework, and runtime hints from cache.
- Keep it production-oriented unless the resolved mode clearly requires otherwise.
- Use non-root runtime users where practical.
- Expose the correct port from cached runtime hints or resolved plan context.
- Do not invent extra services, modes, or environments.
- Do not activate task-runner behavior inside the Dockerfile unless the resolved plan requires it.
- Do not generate compose-specific behavior in this skill.

---

## Image selection rule

Do not blindly trust stale image state from cache.

Before writing `Dockerfile`, re-check the application image through MCP when available.

If the MCP-selected application image materially differs from cached image state:

- refresh `image_selection_report.json`
- refresh or re-resolve packaging state if needed
- only then write `Dockerfile`

When MCP is available, do not proceed using stale cached image selection.

---

## Create vs update behavior

For `Dockerfile`:

1. determine whether it already exists
2. create it if missing
3. update it if present
4. verify it exists after the operation

Rules:

- treat missing `Dockerfile` as creation work
- treat existing `Dockerfile` as update work
- do not rewrite unrelated Docker artifacts
- do not regenerate the full packaging set in this skill

---

## Tool usage — mandatory

You must use tools, not chat output.

Required tool behavior:

- use the Read tool to read all required cache files
- use the Write tool to create or update `Dockerfile`
- use the Bash tool to run:
  ```bash
  ls -la Dockerfile
  ```
  after writing to confirm it exists
- never print the full Dockerfile in chat as a substitute for writing it

Do not treat prose output as task completion.

---

## Execution order

1. Read cache files
2. If cache is incomplete, run bootstrap
3. Read cache again
4. Ensure `packaging_plan.json` exists
5. Ensure `image_selection_report.json` exists
6. If `resolved_plan` is missing or unusable for the request, run resolver mode
7. Re-read updated plan/report
8. Re-check application image through MCP
9. Write only `Dockerfile`
10. Verify it exists with:
   ```bash
   ls -la Dockerfile
   ```
11. Return only the execution summary

Do not stop after planning when the user asked for Dockerfile generation or update.

---

## Output behavior

Return only:

1. `selected_target`
2. `selected_image`
3. `generated_artifacts`
4. `short_reasoning`

Keep the response brief and execution-focused.

---

## Completion standard

The task is not complete unless:

- cache has been read first
- draft packaging state exists
- `resolved_plan` exists or has been refreshed for the current request
- application image has been re-checked through MCP
- `Dockerfile` has been written as a real file
- `Dockerfile` has been verified to exist on disk

Do not claim success before all of the above are true.

---

## Forbidden behavior

Do not:

- generate any other Docker-related files
- rescan the full repository when cache is usable
- invent extra services, roles, modes, or environments
- generate `Dockerfile` from draft hints alone
- print the full file in chat instead of writing it

---

## Policy notes

- Prefer official images selected through `docker-hub` MCP.
- For Next.js, prefer `bookworm-slim` over Alpine unless there is a strong project-specific reason not to.
- Draft hints are not generation input.
- Only resolved activation may drive artifact generation.
