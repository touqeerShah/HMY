import { dockerExec } from "../lib/docker.js";
import { persistExecutionArtifacts } from "./shared.js";
export async function execApp(args) {
    const repoRoot = args.repoRoot ?? process.cwd();
    const result = await dockerExec(repoRoot, "app", args.cmd);
    const files = persistExecutionArtifacts({
        repoRoot,
        kind: "command-output",
        prefix: "app-exec",
        body: result.combined,
        metadata: {
            command: args.cmd,
            mode: args.mode === "rebuild-image" ? "rebuild-image" : "live-bind",
            service: "app",
            exitCode: result.exitCode,
        },
    });
    return {
        ok: result.exitCode === 0,
        message: result.exitCode === 0 ? "App command executed" : "App command failed",
        data: {
            service: "app",
            command: args.cmd,
            ...files,
            stdout: result.stdout,
            stderr: result.stderr,
            exitCode: result.exitCode,
        },
    };
}
