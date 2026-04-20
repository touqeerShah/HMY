---
name: dockerize_project
description: Orchestrate Docker packaging for the selected target using cached project structure, draft packaging plans, resolver-owned activation, and MCP-backed image selection.
---

# Dockerize Project

Containerize the current repository by using cached project understanding, resolving the current user request into a concrete packaging plan, validating image choice through MCP, and generating only the resolved Docker artifacts.

## CRITICAL — do this first, nothing else

Before anything else, run these exact commands in order:

```bash
cat .claude/cache/project_facts.json
cat .claude/cache/packaging_plan.json
cat .claude/cache/image_selection_report.json
```

Do NOT run `find`, broad `ls`, or file discovery commands before this.
Do NOT scan the repository manually.
The cache files are the source of truth for structure and draft packaging scope.

If a required cache file is missing, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode bootstrap
```

Then re-read the cache files above.

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

Do not use manual repository discovery as a substitute for reading cache.

---

## Role

This is the full orchestration skill.

Use it when the user wants the complete Docker packaging flow.

If the user only wants one artifact or one operation, prefer a focused skill:

- `docker_plan`
- `dockerfile_only`
- `compose_only`
- `makefile_only`
- `entrypoint_only`

This skill must support the full resolver lifecycle, including isolated runtime behavior when the request justifies it.

---

## Source of truth model

Use cache as the source of truth for:

- repo structure
- runtime facts
- target selection
- packaging draft
- capabilities
- defaults
- suggested artifact families
- current resolved plan state
- task-runner support
- workflow mode support

Use `docker-hub` MCP as the source of truth for:

- final application image selection
- final service image selection
- final task-runner image selection if separately planned

Do not blindly trust old image selections stored in:

- `.claude/cache/image_selection_report.json`
- `.claude/cache/packaging_plan.json`

Before writing artifacts, re-check image selection through MCP.
If image selection changes materially, refresh report state and re-resolve before writing artifacts.

---

## Draft vs resolved plan

`packaging_plan.json` is no longer assumed to be a final packaging-ready plan.

It contains:

- `capabilities` = what the repo supports
- `defaults` = safe preference hints
- `suggested_artifacts` / `suggested_modes` / `suggested_roles` = draft hints only
- `resolved_plan` = the only active packaging plan for this specific request

Rules:

- do not generate artifacts from `suggested_artifacts`
- do not activate modes from `suggested_modes`
- do not activate roles from `suggested_roles`
- only `resolved_plan` may drive actual artifact generation

---

## Packaging model

This system no longer assumes a single-container app flow.

The packaging model supports first-class container roles:

- `app`
- `task-runner`
- infra services required by the target

The packaging model supports official workflow modes:

- `live-bind`
- `rebuild-image`

Definitions:

- **role** = what the container does
- **mode** = how the container is maintained and executed

The `task-runner` role is first-class in the architecture, but it is only activated when the resolver determines it is needed for the current request.

It is used for isolated execution such as:

- tests
- jobs
- cron-like work
- scripts
- integrations
- scraping
- Google or third-party connected actions
- Claude actions that should run inside Docker instead of on the host

---

## Resolver lifecycle

This skill must follow the resolver lifecycle, not the old planner-only flow.

### Required lifecycle

1. Read cache files first
2. Ensure a draft plan exists
3. Rebuild a fresh draft for comparison
4. Run stale-plan detection
5. Classify the current request
6. Decide lifecycle action:
   - preserve
   - wipe and re-resolve
   - re-resolve
   - ask
   - reject
7. If needed, write a fresh `resolved_plan`
8. Re-check images through MCP
9. If image selection conflicts materially, stop and re-resolve before writing
10. Generate only `resolved_plan.artifacts_to_generate`
11. Verify written files
12. Return only the execution summary

---

## Planning requirements

Before any artifact is written, ensure these files exist:

- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

If `packaging_plan.json` is missing, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode plan-packaging
```

If `image_selection_report.json` is missing, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode write-image-report
```

Then read them.

If the current request requires activation, run resolver mode before artifact creation:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "<user request>"
```

Use `--target` when target selection is already known and necessary.

---

## Target selection

Read `.claude/cache/project_targets.json`.

- If only one target exists, select it automatically.
- Do not ask for confirmation in that case.
- If multiple targets exist, choose the one matching the current draft or resolved plan if already specified.
- Only ask the user when multiple valid targets remain materially ambiguous.

---

## Artifact derivation rules

Artifact generation must be reproducible from `resolved_plan`.

### Base artifacts

Always start from the minimal base set:

- `Dockerfile`
- `.dockerignore`

Add only when justified:

- `Makefile`
- `docker/entrypoint.sh`

### Compose derivation

If compose support exists:

- always include `compose.yml`

If `live-bind` is enabled:

- include `compose.live.yml`

If `rebuild-image` is enabled:

- include `compose.rebuild.yml`

### Task-runner derivation

If `task-runner` is active:

- likely include task-runner wrapper scripts

If `task-runner` is not active:

- do not generate task-runner wrappers

### Host output dir derivation

Enable host output dirs only when the request implies:

- logs
- test results
- command output
- runtime inspection
- isolated execution with observable results

Standard output dirs:

- `.docker-data/logs`
- `.docker-data/test-results`
- `.docker-data/command-output`

### Productionization rule

For production-oriented requests, prefer the smallest valid artifact set.

Likely include:

- `Dockerfile`
- `.dockerignore`
- `compose.yml` if needed
- `compose.rebuild.yml` if rebuild-image mode is active

Do not automatically include:

- `compose.live.yml`
- task-runner wrappers
- host output dirs
- generic execution wrappers

---

## Allowed artifacts

Generate only resolved artifacts listed in:

- `.claude/cache/packaging_plan.json` → `resolved_plan.artifacts_to_generate`

Allowed artifact paths may include:

Core artifacts:

- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `compose.live.yml`
- `compose.rebuild.yml`
- `Makefile`
- `docker/entrypoint.sh`

Command wrapper artifacts:

- `docker/commands/run-in-container.sh`
- `docker/commands/test-in-container.sh`
- `docker/commands/logs.sh`
- `docker/commands/run-in-task-runner.sh`
- `docker/commands/exec-in-task-runner.sh`

Host-visible output paths:

- `.docker-data/logs/`
- `.docker-data/test-results/`
- `.docker-data/command-output/`

Do not generate anything else unless explicitly requested.

---

## Compose model

Do not assume one generic compose file.

Use:

- `compose.yml` for shared services and shared definitions
- `compose.live.yml` for live-bind behavior
- `compose.rebuild.yml` for rebuild-image behavior

### Live-bind rule

If `live-bind` is enabled, likely include:

- `compose.yml`
- `compose.live.yml`

Do not automatically include:

- task-runner wrappers
- host output dirs

unless separately justified.

### Live-bind observability rule

Live-bind changes how code reaches the container, but it does not by itself guarantee visibility into what happened inside the container.

If the user needs to observe execution effects inside the container, the resolver should additionally enable one or more of the following, but only when justified by the request:

- host-visible output dirs
- command wrapper scripts
- task-runner execution paths

Use these rules:

- enable host output dirs when the request implies logs, test results, command output, job output, or runtime inspection
- enable command wrapper scripts when the user wants repeatable in-container commands or Claude is expected to run actions inside the container
- enable task-runner wrappers only when `task-runner` is active in the resolved plan

In live-bind mode, host code changes affect the running container, but Claude should not assume those effects are observable unless the resolved plan also enables an observation path.

### Rebuild-image rule

If `rebuild-image` is enabled, likely include:

- `compose.yml`
- `compose.rebuild.yml`

Do not automatically include:

- `compose.live.yml`
- host output dirs
- task-runner wrappers

unless separately justified.

### Rebuild-image observability rule

Rebuild-image changes how code reaches the container, but it does not by itself guarantee visibility into what happened inside the container.

If the user needs to observe execution effects inside the container, the resolver should additionally enable one or more of the following, but only when justified by the request:

- host-visible output dirs
- command wrapper scripts
- task-runner execution paths

Use these rules:

- enable host output dirs when the request implies logs, test results, command output, job output, or runtime inspection
- enable command wrapper scripts when the user wants repeatable in-container commands or Claude is expected to run actions inside the container
- enable task-runner wrappers only when `task-runner` is active in the resolved plan

In rebuild-image mode, host code changes do not affect the container until rebuild, and Claude should not assume execution effects are visible unless the resolved plan also enables an observation path.

---

## In-container execution requirement

When the resolved plan includes a `task-runner`, use it for isolated execution when appropriate.

Claude should prefer the containerized execution path for:

- tests
- jobs
- scripts
- integrations
- scraping
- tool actions
- cron-like work
- user requests to isolate execution from the host machine

Do not assume those actions should run on the host when the resolved plan supports in-container execution.

Container execution visibility is not implied by mode alone.
If the user needs to inspect what happened inside the container, the resolved plan must explicitly enable an observation path such as host output dirs, wrapper scripts, or task-runner execution.

---

## Create vs update behavior

For each resolved artifact:

1. determine whether the file already exists
2. create it if missing
3. update it if present
4. verify it exists after the operation

Rules:

- treat missing resolved files as creation work
- treat existing resolved files as update work
- do not delete or replace unrelated files
- do not recreate all Docker artifacts when only one needs updating

Treat the task as:

- **initial packaging** when most resolved files are missing
- **update packaging** when one or more resolved files already exist

---

## Tool usage — mandatory

You must use tools, not chat output.

Required tool behavior:

- use the Read tool to read all required cache files
- use the Write tool to create or update every resolved artifact
- use the Bash tool to run `ls -la <file>` after each write to confirm it exists
- never print file contents in chat as a substitute for writing them
- never stop after draft generation when the request includes artifact generation

Do not treat prose output as task completion.

---

## Execution order — do not stop early

1. Read cache files
2. If cache is incomplete, run bootstrap
3. Read cache again
4. If `packaging_plan.json` is missing, run:
   ```bash
   python3 .claude/tools/project_detector.py --root "$(pwd)" --mode plan-packaging
   ```
5. If `image_selection_report.json` is missing, run:
   ```bash
   python3 .claude/tools/project_detector.py --root "$(pwd)" --mode write-image-report
   ```
6. Run resolver mode for the current request:
   ```bash
   python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "<user request>"
   ```
7. Read the updated `packaging_plan.json`
8. Re-check image selection through `docker-hub` MCP
9. If image choice changes materially, refresh report and re-resolve before writing
10. Write each resolved artifact from `resolved_plan.artifacts_to_generate`
11. Verify each file exists with:
   ```bash
   ls -la <file>
   ```
12. Report what was created or updated

Do not pause between steps.
Do not ask for confirmation mid-flow unless there is genuine unresolved target ambiguity.

---

## Output behavior

Return only:

1. `selected_target`
2. `selected_images`
3. `generated_artifacts`
4. `short_reasoning`

Keep the response brief and execution-focused.

---

## Completion standard

The task is not complete unless:

- cache has been read first
- planning files exist
- stale state has been checked
- request lifecycle has been handled
- `resolved_plan` exists for packaging requests
- image selection has been re-checked through MCP
- resolved artifacts have been written as real files
- each written file has been verified to exist on disk

Do not claim success before all of the above are true.

---

## Policy notes

- Prefer official images selected through `docker-hub` MCP.
- For Next.js, prefer `bookworm-slim` over Alpine unless there is a strong reason not to.
- Never substitute generic image advice when MCP is available.
- Never generate extra deployment files unless the user explicitly asks for them.
- The task-runner is first-class in the architecture.
- Live-bind and rebuild-image are official modes.
- Host-visible logs, test results, and command output are part of the contract.
- Draft hints are not generation input.
- Only `resolved_plan` may drive final artifact generation.
