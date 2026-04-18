# Docker Packaging Policy

## STEP 1 — Read cache first

Before any Docker-related work, read these exact cache files first:

```bash
cat .claude/cache/project_facts.json
cat .claude/cache/packaging_plan.json
cat .claude/cache/image_selection_report.json
```

Do not run `find`, broad `ls`, or manual repo discovery before reading cache.
Do not scan the repository manually.
Use cache as the source of truth for project structure and packaging scope.

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

## STEP 4 — Re-check image selection through MCP before writing

Do not blindly trust cached image selections from:

- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

Use cache for:
- project structure
- runtime facts
- target selection
- packaging scope
- approved artifact list

Use `docker-hub` MCP as the source of truth for final image selection at execution time.

Rules:
- Re-check application and service images through MCP before writing artifacts.
- Refresh `image_selection_report.json` from MCP-backed selection logic before artifact generation.
- If the MCP-selected image differs from the cached plan/report, update:
  - `.claude/cache/image_selection_report.json`
  - `.claude/cache/packaging_plan.json`
- Only then write Docker artifacts.

When MCP is available, do not proceed using stale cached image selections.

---

## STEP 5 — Write only approved artifacts

Write only files approved by `.claude/cache/packaging_plan.json`.

Allowed artifacts:
- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `Makefile`
- `docker/entrypoint.sh`

Rules:
- Create approved files if missing.
- Update approved files if present.
- Do not create unrelated deployment files.
- Do not recreate all artifacts when only one needs updating.
- Do not print file contents in chat as a substitute for writing them.

---

## STEP 6 — Verify after every write

After writing each artifact, verify it exists with:

```bash
ls -la <file>
```

This command is allowed only for post-write verification of an expected artifact.
Do not claim success unless the file exists on disk.

---

## STEP 7 — Never stop after planning

If the request is to dockerize, package, create, or update Docker files:

- do not stop after planning
- do not stop after generating cache files
- proceed to writing the approved artifacts immediately unless the user explicitly asked for planning only

Planning alone is not completion.

---

## STEP 8 — Report only execution summary

Return only:

- `selected_target`
- `selected_images`
- `generated_artifacts`
- `short_reasoning`

Do not dump full file contents unless explicitly requested.

---

## Rules

- Cache is the source of truth for structure, runtime facts, targets, and packaging scope.
- MCP is the source of truth for final image selection at execution time.
- Use `docker-hub` MCP for image selection whenever available.
- Never substitute generic image advice when MCP is available.
- For Next.js, prefer Debian `bookworm-slim` over Alpine unless there is a strong project-specific reason not to.
- Create missing approved files.
- Update existing approved files.
- Never recreate all Docker artifacts blindly.
- Never stop after planning when artifact generation was requested.

---

## Skill path

Read the orchestration skill only from:

```bash
cat .claude/skills/dockerize_project/SKILL.md
```

Do not reference skills from any other path.
