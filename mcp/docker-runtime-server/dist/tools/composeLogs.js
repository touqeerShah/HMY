import { runCompose, sanitizeMode } from "../lib/compose.js";
import { persistExecutionArtifacts } from "./shared.js";
export async function composeLogs(args) {
    const repoRoot = args.repoRoot ?? process.cwd();
    const mode = sanitizeMode(args.mode ?? "live-bind");
    const tail = Number.isFinite(args.tail) ? String(args.tail) : "200";
    const result = await runCompose(mode, ["logs", "--tail", tail, args.service], repoRoot);
    const files = persistExecutionArtifacts({
        repoRoot,
        kind: "logs",
        prefix: `${args.service}-logs`,
        body: result.combined,
        metadata: {
            command: result.command.join(" "),
            mode,
            service: args.service,
            exitCode: result.exitCode,
        },
    });
    return {
        ok: result.exitCode === 0,
        message: result.exitCode === 0 ? `Fetched logs for ${args.service}` : `Failed to fetch logs for ${args.service}`,
        data: {
            service: args.service,
            mode,
            ...files,
            logs: result.combined,
        },
    };
}
