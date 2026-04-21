# Docker Packaging Policy

## Operating model — host edits, container executes

This project uses a strict operating model:

- Claude may edit files in the real workspace.
- Claude must not run application, test, or job commands directly on the host.
- All execution must go through containers.
- Normal runtime execution goes through the `app` container.
- Isolated execution goes through the `task-runner` container.
- Logs and execution outputs must come back through:
  - mounted host-visible output directories, or
  - runtime MCP tools that read container state, logs, and command output.

This means:

- **code changes happen in the workspace**
- **runtime effects happen in containers**
- **observation must come back through mounted output dirs or MCP log/output tools**

---

## MCP model — split image selection from runtime control

This project uses two MCP paths with different responsibilities.

### MCP 1 — image/docker-hub MCP

Use this MCP only for:

- official image discovery
- tag and variant comparison
- final application image choice
- final service image choice

Do not use this MCP for:

- compose lifecycle
- container exec
- logs
- rebuilds
- output reading

### MCP 2 — custom Docker runtime MCP

Use this MCP as the operational runtime bridge.

Use it for:

- runtime execution
- compose lifecycle
- app container control
- task-runner container control
- logs and output retrieval
- rebuild actions
- runtime health and inspection

Required runtime MCP tools:

- `resolve_images(target_id, mode, roles)`
- `compose_up(mode)`
- `compose_down()`
- `compose_ps()`
- `compose_logs(service, tail)`
- `exec_app(cmd)`
- `exec_task_runner(cmd)`
- `rebuild(mode)`
- `read_container_output(kind, path)`
- `copy_from_container(container, src, dest)`

Recommended runtime MCP extensions:

- `compose_config(mode)`
- `container_health(service)`
- `exec_app_json(cmd)`
- `exec_task_runner_json(cmd)`
- `tail_output(kind, path, lines)`
- `list_outputs(kind)`

Rules:

- image lookup and validation belong to image MCP
- runtime execution and observation belong to runtime MCP
- do not collapse both MCP responsibilities into one undefined tool path
- use the runtime MCP tools exposed by the configured Docker runtime MCP server
- runtime tool identifiers must match the actual registered MCP server name

---

## STEP 1 — Read cache first

Before any Docker-related work, read these exact cache files first:

```bash
cat .claude/cache/project_facts.json
cat .claude/cache/packaging_plan.json
cat .claude/cache/image_selection_report.json
```

Do not run `find`, broad `ls`, or manual repo discovery before reading cache.
Do not scan the repository manually.
Use cache as the source of truth for project structure, draft packaging state, and resolved packaging scope.

If any required cache file is missing, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode bootstrap
```

Then re-read the cache files above.

---

## STEP 2 — Select target from cache

Use cached target and packaging data.

- If only one target exists, select it automatically.
- Do not ask the user in that case.
- Do not rediscover targets by scanning the repository unless bootstrap failed.

---

## STEP 3 — Ensure planning files exist

Before writing any Docker artifact, ensure these files exist:

- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

If either is missing, run:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode plan-packaging
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode write-image-report
```

Then read them.

---

## STEP 4 — Resolve request before generation

`packaging_plan.json` is draft-first, not automatically packaging-ready.

Before generating Docker artifacts for a request, resolve the request into an active plan:

```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode resolve-packaging --request "<user request>"
```

Rules:

- Do not generate artifacts from draft hints alone.
- Do not treat `suggested_artifacts`, `suggested_modes`, or `suggested_roles` as active generation input.
- Only `resolved_plan` may drive final artifact generation.
- When present, use `resolved_plan.runtime_exec_role`, `resolved_plan.isolated_exec_role`, `resolved_plan.observability_enabled`, and `resolved_plan.runtime_tools` as the execution-routing source of truth.
- Do not improvise execution routing when the resolved plan already specifies it.

---

## STEP 5 — Re-check image selection through image MCP before writing

Do not blindly trust cached image selections from:

- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Use cache for:

- project structure
- runtime facts
- target selection
- draft packaging scope
- resolved artifact scope
- container roles
- workflow modes

Use the image/docker-hub MCP as the source of truth for final image selection at execution time.

Rules:

- Re-check application and service images through MCP before writing artifacts.
- Refresh `image_selection_report.json` from MCP-backed selection logic before artifact generation.
- If the MCP-selected image differs materially from the cached plan/report, update:
  - `.claude/cache/image_selection_report.json`
  - `.claude/cache/packaging_plan.json`
- Re-resolve if image changes affect the active plan.
- Only then write Docker artifacts.

When MCP is available, do not proceed using stale cached image selections.

---

## STEP 6 — Runtime control must go through the runtime MCP

Claude must not run application, test, or job commands directly on the host.

All runtime control must go through the Docker runtime path and should be executed through the custom Docker runtime MCP.

### App container responsibilities

Use the `app` container for:

- app start
- app shell
- dev server
- build
- normal app-local tasks

This should map to:

- `exec_app(cmd)`

### Task-runner container responsibilities

Use the `task-runner` container for:

- tests
- cron-like jobs
- data scripts
- scraping
- integrations
- risky tasks
- anything user explicitly wants isolated from host

This should map to:

- `exec_task_runner(cmd)`

### Hard routing rule

If a task:

- mutates environment
- consumes secrets
- hits third-party services
- could hang or fail noisily
- should be isolated from host
- is explicitly requested to run “inside Docker”

then:

- prefer the `task-runner` container

Do not execute those actions on the host.

---

## STEP 7 — Write only resolved artifacts

Write only files approved by:

- `.claude/cache/packaging_plan.json` → `resolved_plan.artifacts_to_generate`

Approved artifact paths may include:

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

Rules:
- Create resolved files if missing.
- Update resolved files if present.
- Do not create unrelated deployment files.
- Do not recreate all artifacts when only one needs updating.
- Do not print file contents in chat as a substitute for writing them.

---

## STEP 8 — Observation must come back from containers

Container execution visibility is not implied by mode alone.

If the user needs to inspect what happened inside the container, the resolved plan must explicitly enable an observation path such as:

- mounted host-visible output dirs
- wrapper scripts that write output to those dirs
- runtime MCP log/output tools

Standard host-visible output dirs:

- `.docker-data/logs`
- `.docker-data/test-results`
- `.docker-data/command-output`

These are the primary path for Claude to inspect:

- logs
- test results
- command output
- job output
- runtime inspection artifacts

Rules:

- no runtime action is complete unless its result is observable
- observation must come back through host-mounted outputs or runtime MCP tools
- do not assume compose mode alone makes effects visible

---

## STEP 9 — Wrapper and output contract

Wrapper scripts are part of the container execution contract.

Expected wrapper scripts:

- `docker/commands/run-in-container.sh`
- `docker/commands/test-in-container.sh`
- `docker/commands/logs.sh`
- `docker/commands/run-in-task-runner.sh`
- `docker/commands/exec-in-task-runner.sh`

Each wrapper should:

- route to the correct container
- capture stdout and stderr
- write output to `.docker-data/...`
- preserve exit codes
- optionally write metadata such as:
  - timestamp
  - command
  - exit code
  - container name
  - mode

Do not rely on ephemeral terminal output alone when persistent observation is needed.

---

## STEP 10 — Verify after every write

After writing each artifact, verify it exists with:

```bash
ls -la <file>
```

This command is allowed only for post-write verification of an expected artifact.
Do not claim success unless the file exists on disk.

---

## STEP 11 — Never stop after planning

If the request is to dockerize, package, create, or update Docker files:

- do not stop after planning
- do not stop after generating cache files
- do not stop after generating only the draft plan
- proceed to resolving the request and writing the resolved artifacts immediately unless the user explicitly asked for planning only

Planning alone is not completion.

---

## STEP 12 — Runtime state awareness

Before rerunning runtime work after edits, check runtime state if available.

If `.claude/cache/runtime_state.json` indicates:

- `rebuild_required: true` → rebuild before rerun
- `restart_required: true` → restart or re-up containers before rerun

Do not rerun stale containers blindly after dependency or runtime-config changes.

`.claude/cache/runtime_state.json` is runtime state, not a packaging artifact. It may be updated by hooks or runtime tooling but is not part of `resolved_plan.artifacts_to_generate`.

---

## STEP 13 — Report only execution summary

Return only:

- `selected_target`
- `selected_images`
- `generated_artifacts`
- `short_reasoning`

Do not dump full file contents unless explicitly requested.

---

## Rules

- Cache is the source of truth for structure, runtime facts, targets, draft packaging scope, and current resolved scope.
- The image MCP is the source of truth for final image selection at execution time.
- The runtime MCP is the source of truth for container execution, compose control, logs, output retrieval, and rebuild actions.
- Runtime control must go through the Docker runtime path, not host execution.
- Code edits happen in the workspace.
- Runtime effects happen in containers.
- Use the image/docker-hub MCP for image selection whenever available.
- Never substitute generic image advice when MCP is available.
- For Next.js, prefer Debian `bookworm-slim` over Alpine unless there is a strong project-specific reason not to.
- The packaging system must support:
  - `app`
  - `task-runner`
  - `live-bind`
  - `rebuild-image`
- Host-visible logs and outputs are part of the packaging contract.
- Create missing resolved files.
- Update existing resolved files.
- Never recreate all Docker artifacts blindly.
- Never stop after planning when artifact generation was requested.
- Draft hints are not generation input.
- Only `resolved_plan` may drive final artifact generation.
- Stale-plan state must be checked before generation.
- Runtime state must be checked when rerunning after edits.

---

## Skill path

Read the orchestration skill only from:

```bash
cat .claude/skills/dockerize_project/SKILL.md
```

Do not reference skills from any other path.

Delegate isolated or risky runtime work to the `container-exec` subagent. Do not handle those execution flows in the main agent unless the subagent is unavailable.

## Container-first execution policy

For this project, code edits may happen in the workspace, but execution must default to Docker.

Any request that implies execution should automatically be routed into Docker containers, even if the user does not explicitly say “inside Docker”.

Treat the following as execution requests and route them into containers automatically:
- install
- run
- start
- build
- test
- check
- debug
- migrate
- scrape
- cron or job execution
- integration runs
- browser automation
- any request that asks to verify behavior by running the project

Do not run those actions directly on the host.

Execution routing rules:
- Use the `app` container for normal application execution such as install, build, start, dev, and ordinary runtime checks.
- Use the `task-runner` container for isolated, risky, test, migration, scraping, integration, browser automation, cron, or job-style execution.
- If the user explicitly asks for isolation, asks to avoid host execution, or the task may mutate environment, consume secrets, hit third-party services, or fail noisily, prefer `task-runner`.

Examples:
- “install dependencies” → run in container
- “test this” → run in container
- “check if it works” → run in container
- “build the app” → run in container
- “run migration” → run in container
- “debug this issue” → use container execution and container-visible logs/output

When a request says “check”, “verify”, or “see if it works”, treat that as runtime validation and execute it through the appropriate container.

A plain file edit does not require automatic execution unless the user also asks to run, test, check, verify, or debug it.
