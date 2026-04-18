---
name: image_select_only
description: Refresh only image_selection_report.json for the selected packaging target using cached structure and docker-hub MCP.
---

# Image Select Only

Refresh or update only `.claude/cache/image_selection_report.json` for the selected target.

## Read first

Always read:

- `.claude/cache/project_facts.json`
- `.claude/cache/project_targets.json`

Read when present:

- `.claude/cache/project_graph.json`
- `.claude/cache/project_closure.json`
- `.claude/cache/packaging_plan.json`
- `.claude/cache/project_chunks.jsonl`
- `.claude/cache/project_fingerprint.json`

## Goal

Generate or refresh only:

- `.claude/cache/image_selection_report.json`

Do not generate:

- `Dockerfile`
- `.dockerignore`
- `compose.yml`
- `Makefile`
- `docker/entrypoint.sh`

## Required behavior

1. Use cached files only.
2. Select the packaging target.
3. Scope image selection to the selected target and its closure.
4. Use `docker-hub` MCP for:
   - the main application image
   - any service images required by the target
5. Write `.claude/cache/image_selection_report.json` as an actual file.
6. Verify the file exists after writing.

## Target rules

- If exactly one dockerizable target exists, select it automatically.
- If multiple dockerizable targets exist, infer the target from the user request if possible.
- Ask only if the target is genuinely ambiguous.

## Image rules

### Application images

- Prefer official images.
- Avoid `latest`.
- Prefer compatibility and maintainability over smallest size.
- For Next.js production, prefer Debian slim or bookworm-slim unless there is a strong, target-specific reason not to.

### Service images

- Prefer official service images.
- Select only services actually required by the target.
- Do not invent extra services.

## Required report fields

The generated `.claude/cache/image_selection_report.json` must contain:

- `target_id`
- `mcp_required`
- `mcp_used`
- `mcp_server`
- `application_image`
- `service_images`
- `fallback_used`
- `reasoning`

If MCP is unavailable:

- set `mcp_used` to `false`
- set `fallback_used` to `true`
- use cached candidates or target hints
- still write the report

## Output behavior

Return only:

1. `selected_target`
2. `selected_images`
3. `written_files`
4. `short_reasoning`

## Forbidden behavior

Do not:

- rescan the full repository when cache is usable
- generate Docker artifacts
- invent additional apps, services, or environments
- silently skip MCP when image selection is required
- print the report only in chat instead of writing the file
