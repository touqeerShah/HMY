import { runCompose, sanitizeMode } from "../lib/compose.js";
export async function composePs(args) {
    const repoRoot = args.repoRoot ?? process.cwd();
    const mode = sanitizeMode(args.mode ?? "live-bind");
    const result = await runCompose(mode, ["ps"], repoRoot);
    return {
        ok: result.exitCode === 0,
        message: result.exitCode === 0 ? `Compose services listed for ${mode}` : `Compose ps failed for ${mode}`,
        data: {
            mode,
            stdout: result.stdout,
            stderr: result.stderr,
        },
    };
}
