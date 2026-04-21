import { dockerExec } from "../lib/docker.js";
import { persistExecutionArtifacts } from "./shared.js";
function inferOutputKind(cmd) {
    return /(pytest|jest|mocha|vitest|npm test|pnpm test|yarn test)/i.test(cmd) ? "test-results" : "command-output";
}
export async function execTaskRunner(args) {
    const repoRoot = args.repoRoot ?? process.cwd();
    const result = await dockerExec(repoRoot, "task-runner", args.cmd);
    const kind = inferOutputKind(args.cmd);
    const files = persistExecutionArtifacts({
        repoRoot,
        kind,
        prefix: "task-runner-exec",
        body: result.combined,
        metadata: {
            command: args.cmd,
            mode: args.mode === "rebuild-image" ? "rebuild-image" : "live-bind",
            service: "task-runner",
            exitCode: result.exitCode,
        },
    });
    return {
        ok: result.exitCode === 0,
        message: result.exitCode === 0 ? "Task-runner command executed" : "Task-runner command failed",
        data: {
            service: "task-runner",
            command: args.cmd,
            outputKind: kind,
            ...files,
            stdout: result.stdout,
            stderr: result.stderr,
            exitCode: result.exitCode,
        },
    };
}
