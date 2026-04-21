import { runCompose, sanitizeMode } from "../lib/compose.js";
import { persistExecutionArtifacts } from "./shared.js";

export async function rebuild(args: { mode?: string; repoRoot?: string }) {
  const repoRoot = args.repoRoot ?? process.cwd();
  const mode = sanitizeMode(args.mode ?? "rebuild-image");
  const result = await runCompose(mode, ["build"], repoRoot);

  const files = persistExecutionArtifacts({
    repoRoot,
    kind: "logs",
    prefix: "rebuild",
    body: result.combined,
    metadata: {
      command: result.command.join(" "),
      mode,
      exitCode: result.exitCode,
    },
  });

  return {
    ok: result.exitCode === 0,
    message: result.exitCode === 0 ? `Rebuild completed in ${mode}` : `Rebuild failed in ${mode}`,
    data: { mode, ...files, stdout: result.stdout, stderr: result.stderr },
  };
}
