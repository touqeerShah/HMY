import { runCommand } from "./commandRunner.js";
export async function dockerExec(repoRoot, service, shellCommand) {
    return await runCommand(["docker", "compose", "exec", "-T", service, "sh", "-lc", shellCommand], repoRoot);
}
export async function dockerCp(container, src, dest, repoRoot) {
    return await runCommand(["docker", "cp", `${container}:${src}`, dest], repoRoot);
}
