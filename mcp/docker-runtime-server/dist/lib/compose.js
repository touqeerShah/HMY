import path from "node:path";
import { runCommand } from "./commandRunner.js";
export function buildComposeCommand(mode, subcommand) {
    const command = ["docker", "compose", "-f", "compose.yml"];
    if (mode === "live-bind") {
        command.push("-f", "compose.live.yml");
    }
    else {
        command.push("-f", "compose.rebuild.yml");
    }
    return [...command, ...subcommand];
}
export async function runCompose(mode, subcommand, repoRoot) {
    return await runCommand(buildComposeCommand(mode, subcommand), repoRoot);
}
export function sanitizeMode(input) {
    return input === "rebuild-image" ? "rebuild-image" : "live-bind";
}
export function resolveRepoRoot(explicitRoot) {
    return explicitRoot ? path.resolve(explicitRoot) : process.cwd();
}
