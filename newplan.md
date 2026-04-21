Here is the clean plan to achieve exactly what you want:

**Claude stays on the host/workspace editor.
All execution, tests, logs, rebuilds, and risky tasks run inside Docker containers.
Code edits still happen in the real workspace, so container behavior reflects those edits.**

Claude Code supports the building blocks you need for this: it can read and edit your codebase, hooks can enforce workflow rules, MCP can connect Claude to external tools, and custom subagents can be restricted to specialized tasks. ([Claude][1])

# Final target architecture

You want 5 layers:

1. **Real workspace on host**

   * Claude edits code here.
   * Git remains normal.
   * Files are the real project files.

2. **App container**

   * Main runtime for the user application.
   * In live-bind mode, host code changes are reflected inside the container.
   * In rebuild mode, changes require rebuild.

3. **Task-runner container**

   * Separate isolated execution environment for:

     * tests
     * cron/jobs
     * migrations
     * scraping
     * integrations
     * “do this inside Docker, not on host”

4. **Docker MCP**

   * For image selection and container control.
   * This includes your current Docker Hub image-selection path plus runtime operations.

5. **Claude workflow control**

   * Skills for playbooks
   * Hooks for enforcement
   * Resolver for plan activation
   * Optional `container-exec` subagent for risky/container-only work

# Core principle

Split behavior like this:

* **Claude edits files on host**
* **Containers execute everything**
* **Logs and outputs come back through mounted host-visible paths**
* **Hooks prevent host-side execution drift**
* **MCP becomes the only execution/control path Claude is allowed to use for runtime actions**

That is the safest and cleanest model.

# Phase 1 — Lock the operating model

## Goal

Freeze the “host edits, container executes” contract.

## Decisions to make now

Adopt these as hard rules:

* Claude may edit files in the real workspace.
* Claude must not run app/test/job commands directly on the host.
* All execution must go through:

  * `app` container
  * `task-runner` container
* Logs and outputs must be visible to Claude through mounted host directories.
* Image selection remains MCP-backed.
* Runtime control must go through your custom Docker runtime MCP.

## Deliverables

Create/update:

* `ARCHITECTURE.md`
* root `CLAUDE.md`
* `.claude/skills/dockerize_project/SKILL.md`

## Done when

The docs clearly say:

* code changes happen in workspace
* runtime effects happen in containers
* Claude should not execute project commands on host
* observation must come back through mounted output dirs or MCP log tools

# Phase 2 — Define the two MCPs

## Goal

Separate image selection from runtime control.

## MCP 1 — image/docker-hub MCP

Keep it focused on image lookup and validation.

Use it for:

* official image discovery
* variant comparison
* final application image choice
* final service image choice

## MCP 2 — custom Docker runtime MCP

Build this as your operational runtime bridge.

### Tools to implement

Exactly these:

* `resolve_images(target_id, mode, roles)`
* `compose_up(mode)`
* `compose_down()`
* `compose_ps()`
* `compose_logs(service, tail)`
* `exec_app(cmd)`
* `exec_task_runner(cmd)`
* `rebuild(mode)`
* `read_container_output(kind, path)`
* `copy_from_container(container, src, dest)`

## Recommended extension set

Add these too:

* `compose_config(mode)`
  to inspect effective compose merge output

* `container_health(service)`
  to know whether service is healthy before exec/tests

* `exec_app_json(cmd)` / `exec_task_runner_json(cmd)`
  to return structured output when possible

* `tail_output(kind, path, lines)`
  easier than full file reads for logs

* `list_outputs(kind)`
  to discover available logs/results/output artifacts

## Done when

Claude can:

* choose images through MCP
* bring containers up/down through MCP
* run commands only through MCP
* read logs/results only through MCP or mounted output dirs

MCP is the right abstraction for connecting Claude to external workflows and systems. ([Claude API Docs][2])

# Phase 3 — Define the container execution contract

## Goal

Make every runtime action go through Docker.

## App container responsibilities

Use for:

* app start
* app shell
* dev server
* build
* normal app-local tasks

## Task-runner container responsibilities

Use for:

* tests
* cron-like jobs
* data scripts
* scraping
* integrations
* anything “risky”
* anything user explicitly wants isolated from host

## Rule

If a task mutates environment, consumes secrets, hits third-party services, or could hang/fail noisily:

* prefer `task-runner`

## Done when

Every runtime action maps clearly to one of:

* `exec_app(cmd)`
* `exec_task_runner(cmd)`

# Phase 4 — Add mounted observation paths

## Goal

Claude must be able to know what happened inside containers.

Mode alone is not enough. You need explicit observation paths.

## Standard host-visible dirs

Mount these into both containers where appropriate:

* `.docker-data/logs`
* `.docker-data/test-results`
* `.docker-data/command-output`

## What each should contain

### `.docker-data/logs`

* application logs
* task-runner logs
* compose service snapshots
* rolling debug logs

### `.docker-data/test-results`

* junit xml
* pytest output
* jest/mocha summaries
* coverage summaries if needed

### `.docker-data/command-output`

* one-off command results
* migration logs
* job summaries
* structured JSON outputs if your wrappers emit them

## Done when

Claude can inspect container-side effects either by:

* reading mounted files in the workspace, or
* calling runtime MCP tools like `compose_logs` / `read_container_output`

# Phase 5 — Create wrapper scripts

## Goal

Make container execution consistent and observable.

Create these wrappers:

* `docker/commands/run-in-container.sh`
* `docker/commands/test-in-container.sh`
* `docker/commands/logs.sh`
* `docker/commands/run-in-task-runner.sh`
* `docker/commands/exec-in-task-runner.sh`

## What wrappers should do

Each wrapper should:

1. route command to the correct container
2. capture stdout/stderr
3. write outputs to `.docker-data/...`
4. return non-zero exit code correctly
5. write small metadata file if useful:

   * timestamp
   * command
   * exit code
   * container name
   * mode

## Example behavior

`run-in-task-runner.sh "pytest -q"`

Should:

* call `docker compose run --rm task-runner ...`
* save output to `.docker-data/test-results/...`
* save summary/metadata to `.docker-data/command-output/...`

## Done when

Claude does not need to improvise shell behavior for common runtime tasks.

# Phase 6 — Hook enforcement

## Goal

Stop Claude from running app/test tasks directly on host.

Hooks are the right enforcement mechanism for project rules and pre/post tool control. ([Claude][1])

## Hook set to add

### 1. `project_bootstrap.sh`

Runs when Docker-related work starts:

* bootstrap if needed
* refresh project facts
* ensure draft exists

### 2. `resolve_packaging.sh`

Runs before Docker packaging work:

* `plan-packaging`
* `resolve-packaging --request "<user request>"`

### 3. `enforce_container_exec.sh`

Runs before shell/tool execution.

Behavior:

* inspect attempted command
* if it is app/test/job/runtime-related and not Docker-routed:

  * block it
  * instruct Claude to use MCP or wrapper script instead

### 4. `sync_runtime_state.sh`

Optional post-edit hook.

Behavior:

* detect whether changed files affect:

  * Dockerfile
  * package manager files
  * lockfiles
  * runtime config
* mark rebuild-needed state, or stale plan state

## Done when

Claude cannot casually do:

* `npm test`
* `python manage.py test`
* `npm run dev`

on the host for this project.

Instead it is forced into:

* task-runner
* app exec
* MCP runtime command

# Phase 7 — Add `container-exec` subagent

## Goal

Give Claude a specialized executor for risky or isolated tasks.

Claude Code supports custom subagents and tool scoping, which fits this well. ([Claude API Docs][3])

## Subagent name

`container-exec`

## Purpose

Use it for:

* risky commands
* long tests
* migrations
* scraping
* third-party integrations
* browser automation
* cron/job simulations

## Allowed tools for subagent

Restrict it to:

* Docker runtime MCP tools
* reading mounted output dirs
* limited file reads/writes if necessary

Do **not** allow unrestricted host shell commands.

## Done when

The main agent can delegate:

* “run this in task-runner”
* “capture logs”
* “rerun after rebuild”
  to a specialized container-only helper.

# Phase 8 — Update resolver logic

## Goal

Resolver should decide not just artifacts, but also execution path.

Add these resolved fields:

```json
{
  "execution_policy": "container-first",
  "runtime_exec_role": "app",
  "isolated_exec_role": "task-runner",
  "observability_enabled": true,
  "host_output_dirs": [
    ".docker-data/logs",
    ".docker-data/test-results",
    ".docker-data/command-output"
  ],
  "runtime_tools": {
    "app_exec": "mcp.exec_app",
    "task_exec": "mcp.exec_task_runner",
    "logs": "mcp.compose_logs"
  }
}
```

## New resolver rules

* if request says “run”, “test”, “check”, “debug”, “migrate”, “scrape”, “cron”, “inside docker”, “not on host”:

  * resolve execution to container path
* if request implies isolation:

  * use `task-runner`
* if request is routine app interaction:

  * use `app`
* if request needs logs/results:

  * enable observation paths

## Done when

Runtime execution routing is plan-driven, not improvised.

# Phase 9 — Compose and Docker design

## Goal

Make the containers support both live-bind and rebuild-image execution.

## Compose files

### `compose.yml`

Shared:

* app
* task-runner
* infra services
* common networks
* common env
* mounted output dirs

### `compose.live.yml`

Adds:

* bind mounts
* dev commands
* live reload behavior
* task-runner bind mount if needed

### `compose.rebuild.yml`

Adds:

* image-built execution
* no source bind for app unless explicitly needed
* task-runner image execution path

## Important rule

`task-runner` must be available in both modes.

That gives you:

* live iterative testing/jobs
* rebuild-image isolated production-like runs

## Done when

Both of these work:

* `compose_up("live-bind")`
* `compose_up("rebuild-image")`

and both support app + task-runner.

# Phase 10 — Runtime state and rebuild policy

## Goal

Claude should know when edits require:

* no action
* restart
* rebuild

## Simple initial policy

### No rebuild

Changes in:

* application source
* templates
* non-image configs
* tests

In live-bind mode, these should just reflect in container/runtime.

### Restart maybe needed

Changes in:

* app startup config
* env usage
* process manager config

### Rebuild required

Changes in:

* `Dockerfile`
* `package.json` / lockfiles
* `requirements.txt`
* system packages
* image base settings

## Implementation

Have the hook or runtime MCP write a small state file like:

```json
{
  "mode": "live-bind",
  "rebuild_required": true,
  "restart_required": false,
  "reasons": ["package-lock.json changed"]
}
```

## Done when

Claude can make a code change and then know whether to:

* do nothing
* restart service
* rebuild image

# Phase 11 — Testing plan

## Test 1 — Host edits, container execution

Edit a real source file on host.
Run app/test through container.
Confirm:

* host file changed
* container sees change
* no host runtime command was used

## Test 2 — Task-runner isolation

Ask Claude to run tests.
Confirm:

* it routes to `task-runner`
* results land in `.docker-data/test-results`
* no host-side `pytest`/`npm test` is run

## Test 3 — Logs visibility

Trigger an app failure.
Confirm:

* logs available through MCP and/or `.docker-data/logs`
* Claude can summarize failure from those artifacts

## Test 4 — Rebuild trigger

Edit dependency file.
Confirm:

* system marks rebuild needed
* Claude uses rebuild path before rerunning task

## Test 5 — Hook enforcement

Try a host-side command like `npm test`.
Confirm:

* hook blocks it
* Claude reroutes to container path

## Test 6 — Live-bind behavior

Change code in live-bind mode.
Confirm:

* app container reflects change without rebuild
* logs/output visible

## Test 7 — Rebuild-image behavior

Change code in rebuild-image mode.
Confirm:

* rebuild required
* rerun uses rebuilt image
* results visible

# Phase 12 — Delivery order

Do it in this order:

1. **Docs freeze**

   * finalize `ARCHITECTURE.md`
   * finalize `CLAUDE.md`
   * finalize `dockerize_project/SKILL.md`

2. **Custom Docker runtime MCP**

   * implement core runtime tools first:

     * `compose_up`
     * `compose_down`
     * `compose_logs`
     * `exec_app`
     * `exec_task_runner`
     * `rebuild`

3. **Wrapper scripts + mounted output dirs**

   * make runtime observable

4. **Hooks**

   * bootstrap
   * resolve
   * enforce container execution

5. **Task-runner service**

   * add to compose base + both modes

6. **Subagent**

   * add `container-exec`

7. **Rebuild detection**

   * add runtime-state rules

8. **Full end-to-end testing**

# Recommended first concrete milestone

Build this smallest usable version first:

* task-runner container
* mounted output dirs
* runtime MCP with:

  * `exec_app`
  * `exec_task_runner`
  * `compose_logs`
  * `rebuild`
* hook that blocks host test/app commands
* resolver rule: tests/jobs/integrations default to `task-runner`

That gives you immediate value fast.

# Final result you are aiming for

Claude behaves like this:

* edits your real files in the workspace
* never runs project runtime tasks directly on host
* always routes execution through app/task-runner containers
* reads logs/results from mounted output dirs or runtime MCP
* rebuilds only when needed
* uses task-runner for isolated/risky work
* stays deterministic because hooks and resolver enforce the policy

That is the clean path to the system you described. ([Claude][1])

If you want, I’ll turn this into a ready-to-save `PLUGIN_IMPLEMENTATION_PLAN.md` file.

[1]: https://code.claude.com/docs/en/overview?utm_source=chatgpt.com "Claude Code overview - Claude Code Docs"
[2]: https://docs.anthropic.com/ja/docs/build-with-claude/mcp?utm_source=chatgpt.com "What is the Model Context Protocol (MCP)?"
[3]: https://docs.anthropic.com/en/docs/claude-code/slash-commands?utm_source=chatgpt.com "Extend Claude with skills - Claude Code Docs"


Here is the clean split.

# Already done

## Architecture and policy direction

Done conceptually and mostly written.

You now have:

* draft vs resolved plan model
* stale-plan guard model
* request lifecycle model
* resolver-owned activation
* support vs activation image report model
* artifact derivation rules
* test strategy in `ARCHITECTURE.md`

## Core Python pieces

Done enough as first working version.

You already have or drafted:

* `common.py` with structured error helpers
* `plan_staleness.py`
* `request_lifecycle.py`
* `plan_resolver.py`
* updated `image_report.py`
* updated `project_detector.py` with:

  * `plan-packaging`
  * `write-image-report`
  * `resolve-packaging`

## Skills rewritten

Done as `.md` outputs.

You now have updated versions for:

* `dockerize_project`
* `dockerfile_only`
* `compose_only`
* `makefile_only`
* `entrypoint_only`
* `docker_plan`
* `image_select_only`

## Main docs rewritten

Done as generated files.

You now have updated content for:

* `CLAUDE.md`
* `ARCHITECTURE.md`

---

# Partially done

## Resolver integration

Partially done.

Why partial:

* `project_detector.py` now calls:

  * stale check
  * request classifier
  * lifecycle action
  * resolver
* but this is still controller-side integration, not yet fully enforced by hooks/skills in real runtime behavior

So logic exists, but the whole workflow is not yet fully operational in Claude usage.

## Artifact derivation

Partially done.

Why partial:

* rules are now documented clearly
* resolver derives artifacts
* but derivation is still relatively simple and heuristic
* needs more exact mapping for:

  * Makefile inclusion
  * entrypoint inclusion
  * wrapper/output dir activation nuances
  * mode-specific edge cases

## Image re-check behavior

Partially done.

Why partial:

* policy says MCP must re-check before write
* image report semantics are updated
* but real runtime orchestration with MCP-triggered re-resolve is not fully implemented yet

---

# New work introduced

These are the new major pieces you decided to add later.

## Host-edits, container-exec model

New.

This was not part of the earlier simpler packaging-only design.

Now the system must support:

* Claude edits real workspace files on host
* runtime effects happen only in containers
* logs/results come back through mounted output dirs or MCP

## Task-runner as operational runtime

New and bigger than before.

Earlier:

* task-runner was mostly planning architecture

Now:

* it is part of execution policy
* used for tests/jobs/integrations/risky tasks
* must exist in both `live-bind` and `rebuild-image`

## Custom Docker runtime MCP

New.

This is a major addition.

You now want a second MCP for:

* `compose_up`
* `compose_down`
* `compose_ps`
* `compose_logs`
* `exec_app`
* `exec_task_runner`
* `rebuild`
* `read_container_output`
* `copy_from_container`
* `resolve_images`

This is not done yet.

## Hook enforcement for container-only execution

New.

This is also not done yet.

You want hooks that:

* bootstrap and refresh packaging state
* resolve before execution
* block host-side runtime/test commands
* force Docker/container execution path

## `container-exec` subagent

New.

This is not done yet.

It is a later enhancement for:

* isolated/risky execution
* controlled Docker-only runtime actions

---

# Left to do

## 1. Real plugin packaging

Not done.

You still need to assemble the actual reusable project package with:

* skills in project paths
* hooks in project paths
* MCP server(s)
* optional subagent definition
* install/setup instructions

## 2. Custom Docker runtime MCP implementation

Not done.

This is one of the biggest remaining tasks.

You need to build:

* server structure
* tool schemas
* Docker compose integration
* output handling
* error handling
* auth/env strategy

## 3. Hook scripts and hook config

Not done.

Still needed:

* `resolve_packaging.sh`
* `enforce_container_exec.sh`
* maybe `sync_runtime_state.sh`
* actual Claude hook config wiring

## 4. Wrapper scripts

Not done.

Still needed:

* `run-in-container.sh`
* `test-in-container.sh`
* `logs.sh`
* `run-in-task-runner.sh`
* `exec-in-task-runner.sh`

## 5. Compose/task-runner implementation

Not done.

Still needed in actual artifacts:

* `task-runner` service in `compose.yml`
* mode-aware behavior in:

  * `compose.live.yml`
  * `compose.rebuild.yml`
* mounted output dirs
* shared networks/depends_on rules

## 6. Runtime-state / rebuild detection

Not done.

Still needed:

* identify when file edits require:

  * no action
  * restart
  * rebuild
* persist that state
* make Claude obey it

## 7. End-to-end testing

Not done.

You now have the test plan in docs, but not the actual executed test suite or scripts.

---

# What is old and now invalid

These earlier assumptions are now invalid:

* planner decides final artifacts
* `packaging_plan.json` is packaging-ready by default
* support implies activation
* one generic compose file is enough
* task-runner is always active
* Claude can just run runtime/test commands on host

These should now be treated as obsolete.

---

# Current state in one line

## Done

* architecture, schema, lifecycle, resolver design, rewritten docs/skills, first-pass controller code

## Partial

* actual resolver workflow behavior in practice, artifact derivation depth, MCP re-check orchestration

## New but not built

* container-only execution enforcement, runtime MCP, task-runner execution model, hooks, wrappers, plugin bundle

---

# Best next milestone

The best next practical milestone is:

**build the runtime execution layer first**, meaning:

* task-runner container
* mounted output dirs
* wrapper scripts
* custom Docker runtime MCP with:

  * `exec_app`
  * `exec_task_runner`
  * `compose_logs`
  * `rebuild`
* hook that blocks host runtime/test commands

That is the point where the system stops being mostly architecture and starts behaving the way you want.


Good. These two phases are the first real bridge from architecture into a working plugin/runtime system.

Here is the clean implementation plan.

# Phase 2 — Define the two MCPs

## Goal

Split responsibilities cleanly:

* **MCP 1** = image discovery and validation
* **MCP 2** = runtime control and observation

This is the correct separation. Do not merge them.

---

## MCP 1 — image/docker-hub MCP

### Scope

Keep this MCP narrow.

It should only do:

* official image discovery
* tag/variant comparison
* runtime image suitability checks
* final application image choice
* final service image choice

### It should not do

Do not let it handle:

* container startup
* compose control
* logs
* exec
* rebuilds
* output file reads

That belongs to runtime MCP.

### Input sources

It should consume:

* target runtime
* framework
* selected roles
* selected mode
* service requirements
* planner image hints

### Output shape

It should return normalized image decisions like:

```json
{
  "application": {
    "image": "node:20-bookworm-slim",
    "reason": "compatible official image for Next.js production"
  },
  "services": {
    "postgres": {
      "image": "postgres:16",
      "reason": "official stable supported image"
    }
  }
}
```

### Files affected

Mostly documentation and policy only for now:

* `ARCHITECTURE.md`
* `CLAUDE.md`
* `.claude/skills/image_select_only/SKILL.md`
* `.claude/skills/docker_plan/SKILL.md`
* `.claude/skills/dockerize_project/SKILL.md`

No major Python refactor needed here yet if you still use existing image report flow.

---

## MCP 2 — custom Docker runtime MCP

## Goal

This becomes the **operational runtime bridge**.

Claude should use this MCP instead of host shell for:

* running app tasks
* running isolated tasks
* compose lifecycle
* logs
* output reads
* rebuilds

---

## Required tools

Implement these first exactly as named:

* `resolve_images(target_id, mode, roles)`
* `compose_up(mode)`
* `compose_down()`
* `compose_ps()`
* `compose_logs(service, tail)`
* `exec_app(cmd)`
* `exec_task_runner(cmd)`
* `rebuild(mode)`
* `read_container_output(kind, path)`
* `copy_from_container(container, src, dest)`

These are enough for the first usable runtime layer.

---

## Recommended extra tools

Add next:

* `compose_config(mode)`
* `container_health(service)`
* `exec_app_json(cmd)`
* `exec_task_runner_json(cmd)`
* `tail_output(kind, path, lines)`
* `list_outputs(kind)`

These make debugging and agent behavior much cleaner.

---

## MCP 2 ownership rules

### Runtime MCP should own

* compose orchestration
* container exec
* logs retrieval
* output retrieval
* rebuild/restart operations
* health inspection

### Runtime MCP should not own

* editing source files
* planning artifacts
* stale-plan logic
* lifecycle resolution
* image selection policy beyond direct resolution calls

That keeps it operational, not architectural.

---

## Suggested runtime MCP project structure

```text
mcp/docker-runtime-server/
├─ package.json
├─ tsconfig.json
├─ src/
│  ├─ index.ts
│  ├─ tools/
│  │  ├─ resolveImages.ts
│  │  ├─ composeUp.ts
│  │  ├─ composeDown.ts
│  │  ├─ composePs.ts
│  │  ├─ composeLogs.ts
│  │  ├─ execApp.ts
│  │  ├─ execTaskRunner.ts
│  │  ├─ rebuild.ts
│  │  ├─ readContainerOutput.ts
│  │  ├─ copyFromContainer.ts
│  │  ├─ composeConfig.ts
│  │  ├─ containerHealth.ts
│  │  ├─ execAppJson.ts
│  │  ├─ execTaskRunnerJson.ts
│  │  ├─ tailOutput.ts
│  │  └─ listOutputs.ts
│  ├─ lib/
│  │  ├─ docker.ts
│  │  ├─ compose.ts
│  │  ├─ outputPaths.ts
│  │  ├─ commandRunner.ts
│  │  ├─ jsonExec.ts
│  │  └─ errors.ts
│  └─ types/
│     └─ runtime.ts
```

---

## Runtime MCP implementation order

### Step 1

Implement low-level helpers:

* compose command runner
* docker exec runner
* log reader
* output path resolver
* structured error wrapper

### Step 2

Implement core runtime tools:

* `compose_up`
* `compose_down`
* `compose_ps`
* `exec_app`
* `exec_task_runner`
* `compose_logs`
* `rebuild`

### Step 3

Implement observation tools:

* `read_container_output`
* `tail_output`
* `list_outputs`
* `copy_from_container`

### Step 4

Implement structured execution tools:

* `exec_app_json`
* `exec_task_runner_json`

### Step 5

Implement health and merged config tools:

* `container_health`
* `compose_config`

---

# Phase 3 — Define the container execution contract

## Goal

Every runtime action must route through Docker, not host shell.

This is the key contract.

---

## App container responsibilities

Use `app` for:

* app start
* app shell
* dev server
* build
* normal app-local tasks

This should be the default runtime container for ordinary app work.

### Examples

Use `exec_app(cmd)` for:

* `npm run dev`
* `npm run build`
* `python manage.py runserver`
* `python manage.py migrate` only if not isolated
* `node scripts/local-task.js` if it is app-local and safe

---

## Task-runner responsibilities

Use `task-runner` for:

* tests
* cron-like jobs
* data scripts
* scraping
* integrations
* risky tasks
* host-isolated work
* third-party connected work
* anything that may mutate environment or consume secrets noisily

This is the safer execution container.

### Examples

Use `exec_task_runner(cmd)` for:

* `pytest`
* `npm test`
* scraping jobs
* integration sync tasks
* cron simulations
* migration verification jobs
* browser automation
* Google-connected actions
* third-party API tasks

---

## Hard routing rule

If a task:

* mutates environment
* consumes secrets
* hits third-party services
* could hang/fail noisily
* should be isolated from host
* is explicitly requested to run “inside Docker”

then:

* prefer `task-runner`

This should be a hard resolver/runtime rule, not informal guidance.

---

## Execution contract shape

Add this conceptually to resolved execution metadata:

```json
{
  "execution_policy": "container-first",
  "default_exec_role": "app",
  "isolated_exec_role": "task-runner",
  "container_exec_rules": {
    "tests": "task-runner",
    "jobs": "task-runner",
    "integrations": "task-runner",
    "app_runtime": "app",
    "build": "app"
  }
}
```

You do not need to fully code this immediately, but this is the correct eventual shape.

---

## Observation contract

Every runtime action should produce observable output through one of these paths:

* MCP logs tool
* MCP output tool
* mounted host output dirs

### Standard output dirs

* `.docker-data/logs`
* `.docker-data/test-results`
* `.docker-data/command-output`

### Rule

No runtime action is considered complete unless its result is observable by Claude through:

* MCP output/log tools, or
* these mounted directories

---

## Wrapper script contract

Even if MCP runs the commands, wrapper scripts are still useful and should exist.

Create:

* `docker/commands/run-in-container.sh`
* `docker/commands/test-in-container.sh`
* `docker/commands/logs.sh`
* `docker/commands/run-in-task-runner.sh`
* `docker/commands/exec-in-task-runner.sh`

### Each wrapper should

* route to correct container
* capture stdout/stderr
* write outputs to `.docker-data/...`
* preserve exit code
* optionally write metadata file

That makes runtime results easier for Claude to inspect.

---

# What is done already for these phases

## Already done conceptually

* You already decided the split:

  * image MCP
  * runtime MCP
* You already defined `app` vs `task-runner`
* You already defined host-edits / container-exec behavior
* You already defined mounted output dirs conceptually

## Already partially done in docs

* `ARCHITECTURE.md` and updated policy/skills already say:

  * host edits are allowed
  * runtime should happen in containers
  * task-runner exists
  * observation comes back through output dirs or MCP

---

# What is new in Phase 2/3

These are the genuinely new implementation items:

## New

* actual custom Docker runtime MCP server
* runtime MCP tool schema
* strict runtime routing contract
* app vs task-runner operational boundaries
* wrapper script design tied to mounted outputs

## Not built yet

* MCP server code
* wrapper scripts
* hook enforcement
* runtime-state file / rebuild detection
* `container-exec` subagent

---

# Files to update now

## Documentation / policy

Update or extend:

* `ARCHITECTURE.md`
* `CLAUDE.md`
* `.claude/skills/dockerize_project/SKILL.md`

Add explicit sections for:

* two MCP separation
* runtime MCP tool list
* app vs task-runner routing rules
* observation/output contract

## New implementation files

Create:

```text
mcp/docker-runtime-server/src/index.ts
mcp/docker-runtime-server/src/tools/resolveImages.ts
mcp/docker-runtime-server/src/tools/composeUp.ts
mcp/docker-runtime-server/src/tools/composeDown.ts
mcp/docker-runtime-server/src/tools/composePs.ts
mcp/docker-runtime-server/src/tools/composeLogs.ts
mcp/docker-runtime-server/src/tools/execApp.ts
mcp/docker-runtime-server/src/tools/execTaskRunner.ts
mcp/docker-runtime-server/src/tools/rebuild.ts
mcp/docker-runtime-server/src/tools/readContainerOutput.ts
mcp/docker-runtime-server/src/tools/copyFromContainer.ts
mcp/docker-runtime-server/src/lib/docker.ts
mcp/docker-runtime-server/src/lib/compose.ts
mcp/docker-runtime-server/src/lib/outputPaths.ts
mcp/docker-runtime-server/src/lib/errors.ts
```

Then later:

```text
mcp/docker-runtime-server/src/tools/composeConfig.ts
mcp/docker-runtime-server/src/tools/containerHealth.ts
mcp/docker-runtime-server/src/tools/execAppJson.ts
mcp/docker-runtime-server/src/tools/execTaskRunnerJson.ts
mcp/docker-runtime-server/src/tools/tailOutput.ts
mcp/docker-runtime-server/src/tools/listOutputs.ts
```

## New wrapper files

Create:

```text
docker/commands/run-in-container.sh
docker/commands/test-in-container.sh
docker/commands/logs.sh
docker/commands/run-in-task-runner.sh
docker/commands/exec-in-task-runner.sh
```

---

# Done criteria for these two phases

## Phase 2 is done when

Claude can:

* choose images through image MCP
* bring containers up/down through runtime MCP
* run commands only through runtime MCP
* read logs/results only through runtime MCP or mounted output dirs

## Phase 3 is done when

Every runtime action maps clearly to:

* `exec_app(cmd)`
* `exec_task_runner(cmd)`

and Claude no longer treats host shell as a normal runtime path.

---

# Best next concrete move

The best next move is:

## Step 1

Update docs first with:

* two MCP split
* app vs task-runner routing rules

## Step 2

Create runtime MCP skeleton with only these 6 tools first:

* `compose_up`
* `compose_down`
* `compose_logs`
* `exec_app`
* `exec_task_runner`
* `rebuild`

## Step 3

Create wrapper scripts and output dirs

That gives you the first working container-exec system.

If you want, I can next write the exact `PLUGIN_IMPLEMENTATION_PLAN.md` for Phase 2 and Phase 3, or generate the runtime MCP file skeleton.
