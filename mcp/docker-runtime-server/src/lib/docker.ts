import { runCommand } from "./commandRunner.js";

export async function dockerExec(repoRoot: string, service: string, shellCommand: string) {
  return await runCommand(["docker", "compose", "exec", "-T", service, "sh", "-lc", shellCommand], repoRoot);
}

export async function dockerCp(container: string, src: string, dest: string, repoRoot: string) {
  return await runCommand(["docker", "cp", `${container}:${src}`, dest], repoRoot);
}
