import { runCompose, sanitizeMode } from "../lib/compose.js";
import { persistExecutionArtifacts } from "./shared.js";
export async function composeDown(args) {
    const repoRoot = args.repoRoot ?? process.cwd();
    const mode = sanitizeMode(args.mode ?? "live-bind");
    const result = await runCompose(mode, ["down"], repoRoot);
    const files = persistExecutionArtifacts({
        repoRoot,
        kind: "logs",
        prefix: "compose-down",
        body: result.combined,
        metadata: {
            command: result.command.join(" "),
            mode,
            exitCode: result.exitCode,
        },
    });
    return {
        ok: result.exitCode === 0,
        message: result.exitCode === 0 ? `Compose stack stopped for ${mode}` : `Compose down failed for ${mode}`,
        data: { mode, ...files, stdout: result.stdout, stderr: result.stderr },
    };
}
