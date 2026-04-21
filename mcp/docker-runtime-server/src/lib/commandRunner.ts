import { spawn } from "node:child_process";
import { CommandExecutionResult } from "../types/runtime.js";

export async function runCommand(command: string[], cwd: string): Promise<CommandExecutionResult> {
  return await new Promise((resolve, reject) => {
    const child = spawn(command[0], command.slice(1), {
      cwd,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += String(chunk);
    });

    child.stderr.on("data", (chunk) => {
      stderr += String(chunk);
    });

    child.on("error", (error) => reject(error));
    child.on("close", (code) => {
      const exitCode = code ?? 1;
      resolve({
        command,
        exitCode,
        stdout,
        stderr,
        combined: [stdout, stderr].filter(Boolean).join("\n").trim(),
      });
    });
  });
}
