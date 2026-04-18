---
name: dockerize_project
description: Orchestrate Docker packaging for the selected target using cached project structure, packaging plans, and MCP-backed image selection.
---

# Dockerize Project

Containerize the current repository by using cached project understanding, validating image choice through MCP, and generating only the approved Docker artifacts.

## CRITICAL — do this first, nothing else

Before anything else, run these exact commands in order:

```bash
cat .claude/cache/project_facts.json
cat .claude/cache/packaging_plan.json
cat .claude/cache/image_selection_report.json
```

Do NOT run `find`, broad `ls`, or file discovery commands before this.
Do NOT scan the repository manually.
The cache files are the source of truth for structure and packaging scope.

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

---

## Source of truth model

Use cache as the source of truth for:
- repo structure
- runtime facts
- packaging scope
- target selection
- approved artifact list

Use `docker-hub` MCP as the source of truth for:
- final application image selection
- final service image selection

Do not blindly trust old image selections stored in:
- `.claude/cache/image_selection_report.json`
- `.claude/cache/packaging_plan.json`

Before writing artifacts, re-check image selection through MCP.
If image selection changes, refresh the planning/report outputs before writing.

---

## Workflow

1. Read cache files first.
2. Select target from cache.
3. Ensure planning files exist.
4. Re-check selected images through MCP.
5. Refresh planning/report outputs if image selection changed.
6. Generate only the artifacts listed in `packaging_plan.json`.
7. Write them as real repository files.
8. Verify each written file exists.
9. Return only the execution summary.

Do not stop after planning when the task is packaging.

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

If the MCP-revalidated image choice differs from cached planning outputs, refresh the report and plan before artifact creation.

---

## Target selection

Read `.claude/cache/project_targets.json`.

- If only one target exists, select it automatically.
- Do not ask for confirmation in that case.
- If multiple targets exist, choose the one matching the packaging plan if already specified.
- Only ask the user when multiple valid targets remain ambiguous.

---

## Allowed artifacts

Generate only approved artifacts listed in `.claude/cache/packaging_plan.json`.

Allowed artifact paths:
- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `Makefile`
- `docker/entrypoint.sh`

Do not generate anything else unless explicitly requested.

---

## Create vs update behavior

For each approved artifact:

1. determine whether the file already exists
2. create it if missing
3. update it if present
4. verify it exists after the operation

Rules:
- treat missing approved files as creation work
- treat existing approved files as update work
- do not delete or replace unrelated files
- do not recreate all Docker artifacts when only one needs updating

Treat the task as:
- **initial packaging** when most approved files are missing
- **update packaging** when one or more approved files already exist

---

## Tool usage — mandatory

You must use tools, not chat output.

Required tool behavior:
- use the Read tool to read all required cache files
- use the Write tool to create or update every approved artifact
- use the Bash tool to run `ls -la <file>` after each write to confirm it exists
- never print file contents in chat as a substitute for writing them
- never stop after planning when the request includes artifact generation

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
6. Re-check image selection through `docker-hub` MCP
7. Refresh planning/report outputs if image selection changed
8. Write each approved artifact
9. Verify each file exists with:
   ```bash
   ls -la <file>
   ```
10. Report what was created or updated

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
- image selection has been re-checked through MCP
- approved artifacts have been written as real files
- each written file has been verified to exist on disk

Do not claim success before all of the above are true.

---

## Policy notes

- Prefer official images selected through `docker-hub` MCP.
- For Next.js, prefer `bookworm-slim` over Alpine unless there is a strong reason not to.
- Never substitute generic image advice when MCP is available.
- Never generate extra deployment files unless the user explicitly asks for them.
