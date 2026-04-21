import { runCompose, sanitizeMode } from "../lib/compose.js";
import { persistExecutionArtifacts } from "./shared.js";

export async function composeUp(args: { mode?: string; repoRoot?: string }) {
  const repoRoot = args.repoRoot ?? process.cwd();
  const mode = sanitizeMode(args.mode ?? "live-bind");
  const result = await runCompose(mode, ["up", "-d"], repoRoot);

  const files = persistExecutionArtifacts({
    repoRoot,
    kind: "logs",
    prefix: "compose-up",
    body: result.combined,
    metadata: {
      command: result.command.join(" "),
      mode,
      exitCode: result.exitCode,
    },
  });

  return {
    ok: result.exitCode === 0,
    message: result.exitCode === 0 ? `Compose stack started in ${mode}` : `Compose up failed in ${mode}`,
    data: { mode, ...files, stdout: result.stdout, stderr: result.stderr },
  };
}
