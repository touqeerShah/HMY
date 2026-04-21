import path from "node:path";
import { runCommand } from "./commandRunner.js";
import { ComposeMode } from "../types/runtime.js";

export function buildComposeCommand(mode: ComposeMode, subcommand: string[]): string[] {
  const command = ["docker", "compose", "-f", "compose.yml"];

  if (mode === "live-bind") {
    command.push("-f", "compose.live.yml");
  } else {
    command.push("-f", "compose.rebuild.yml");
  }

  return [...command, ...subcommand];
}

export async function runCompose(mode: ComposeMode, subcommand: string[], repoRoot: string) {
  return await runCommand(buildComposeCommand(mode, subcommand), repoRoot);
}

export function sanitizeMode(input: string): ComposeMode {
  return input === "rebuild-image" ? "rebuild-image" : "live-bind";
}

export function resolveRepoRoot(explicitRoot?: string): string {
  return explicitRoot ? path.resolve(explicitRoot) : process.cwd();
}
