# Docker Packaging Policy

## STEP 1 — Always read cache first (no exceptions)

When any Docker-related work is requested, immediately run:

```bash
cat .claude/cache/project_facts.json
cat .claude/cache/project_targets.json
cat .claude/cache/packaging_plan.json
cat .claude/cache/image_selection_report.json
```

Do NOT scan the repo. Do NOT run find or ls. The cache is the source of truth.

If any cache file is missing, run:
```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode bootstrap
```
Then re-read the cache.

## STEP 2 — Select target from cache

Read `project_targets.json`. If only one target exists, select it automatically. Do not ask.

## STEP 3 — Ensure planning files exist

Both must exist before writing any file:
- `.claude/cache/packaging_plan.json`
- `.claude/cache/image_selection_report.json`

If missing, run:
```bash
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode plan-packaging
python3 .claude/tools/project_detector.py --root "$(pwd)" --mode write-image-report
```

## STEP 4 — Write artifacts using Write tool

Write only files listed in `packaging_plan.json`. Allowed:
- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `Makefile`
- `docker/entrypoint.sh`

After each write, verify with:
```bash
ls -la <file>
```

Never print file contents in chat as a substitute for writing them.

## STEP 5 — Report what was done

Return only:
- selected_target
- selected_images  
- generated_artifacts
- short_reasoning

## Rules

- Use `docker-hub` MCP for image selection. Never substitute generic advice.
- For Next.js: prefer `bookworm-slim`, not Alpine.
- Create missing files. Update existing files. Never recreate all files when only one needs updating.
- Never stop after planning. Always proceed to writing.

## Skill locations

Skills are in `.claude/skills/`. Load them with:
```bash
cat .claude/skills/dockerize_project/SKILL.md
```

Never reference skills from any other path.
