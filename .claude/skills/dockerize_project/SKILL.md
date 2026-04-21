---
name: dockerize_project
description: Orchestrate Docker packaging for the selected target using cached project structure, draft packaging plans, resolver-owned activation, MCP-backed image selection, and container-first runtime execution.
---

# Dockerize Project

Containerize the current repository by using cached project understanding, resolving the current user request into a concrete packaging plan, validating image choice through MCP, and generating only the resolved Docker artifacts.

This skill follows a strict operating model:

- Claude edits code in the real workspace.
- Claude must not run application, test, or job commands directly on the host.
- Runtime effects must happen inside containers.
- Normal runtime execution goes through the `app` container.
- Isolated execution goes through the `task-runner` container.
- Observation must come back through mounted host-visible output dirs or runtime MCP log/output tools.

---

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

This skill must support the full resolver lifecycle and container-first runtime behavior.

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

Use the custom Docker runtime MCP as the source of truth for:

- runtime execution
- app container control
- task-runner container control
- logs
- output retrieval
- rebuild actions

Use the runtime MCP tools exposed by the configured Docker runtime MCP server. Tool identifiers must match the actual registered MCP server name.

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

When present, use `resolved_plan.runtime_exec_role`, `resolved_plan.isolated_exec_role`, `resolved_plan.observability_enabled`, and `resolved_plan.runtime_tools` as the execution-routing source of truth.

Do not improvise execution routing when the resolved plan already specifies it.

---

## Packaging and execution model

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

Runtime rule:

- Claude may edit code in the workspace.
- Claude must not run application, test, or job commands directly on the host.
- Runtime effects must happen in containers.

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

## Runtime execution requirement

When the user wants runtime work, testing, jobs, or isolation:

- do not run those actions directly on the host
- route normal runtime actions through the `app` container
- route isolated or risky test or job actions through the `task-runner` container

Examples that should be container-routed:

- tests
- app startup
- build validation
- migrations
- cron-like jobs
- integrations
- scraping
- tool actions that affect runtime state
- risky or host-avoiding execution

Use the runtime MCP or approved wrapper scripts to perform these actions.

For isolated or risky runtime execution, delegate to the `container-exec` subagent. Do not handle those execution flows in the main agent unless the subagent is unavailable.

---

## Runtime state awareness

Before rerunning runtime work after edits, check runtime state if available.

If `.claude/cache/runtime_state.json` indicates:

- `rebuild_required: true` → rebuild before rerun
- `restart_required: true` → restart or re-up containers before rerun

Do not rerun stale containers blindly after dependency or runtime-config changes.

`.claude/cache/runtime_state.json` is runtime state, not a packaging artifact. It may be updated by hooks or runtime tooling but is not part of `resolved_plan.artifacts_to_generate`.

---

## Observation requirement

Container execution visibility is not implied by mode alone.

If the user needs to inspect what happened inside the container, the resolved plan must explicitly enable an observation path such as:

- mounted host-visible output dirs
- command wrapper scripts that write output there
- runtime MCP log/output tools

Standard host-visible output dirs:

- `.docker-data/logs`
- `.docker-data/test-results`
- `.docker-data/command-output`

These are the primary observation path for:

- logs
- test results
- command output
- job output
- runtime inspection artifacts

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

## Tool usage — mandatory

You must use tools, not chat output.

Required tool behavior:

- read all required cache files before Docker-related work
- create or update every resolved artifact as a real file
- verify each written file exists with:
  `ls -la <file>`
- use container-first execution paths for runtime, test, and job work
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

For runtime actions after generation:

- execute through `app` or `task-runner`
- read logs and outputs through mounted output dirs or runtime MCP
- do not run application, test, or job commands directly on host

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
- stale-plan state has been checked
- request lifecycle has been handled
- `resolved_plan` exists for packaging requests
- image selection has been re-checked through MCP
- resolved artifacts have been written as real files
- each written file has been verified to exist on disk

For runtime, test, or job actions, completion also requires:

- the action ran in a container, not on the host
- observation came back through mounted output dirs or runtime MCP log/output tools
- runtime state has been checked when rerunning after edits

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
- Code changes happen in the workspace.
- Runtime effects happen in containers.
