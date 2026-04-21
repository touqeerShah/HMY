
import path from "node:path";
import { runCommand } from "../lib/commandRunner.js";

type ExecScratchArgs = {
  cmd: string | string[];
  image?: string;
  repoRoot?: string;
  mountOutput?: boolean;
  workdir?: string;
};

function normalizeCommand(cmd: string | string[]): string {
  if (Array.isArray(cmd)) {
    return cmd.map((part) => String(part)).join(" ");
  }
  return String(cmd);
}

export async function execScratch(args: ExecScratchArgs) {
  const cmd = normalizeCommand(args.cmd);
  const image = args.image || "python:3.12-slim";
  const repoRoot = args.repoRoot ? path.resolve(args.repoRoot) : process.cwd();
  const mountOutput = args.mountOutput ?? false;
  const workdir = args.workdir || "/workspace";

  const dockerArgs = ["run", "--rm", "-i"];

  if (mountOutput) {
    const outputDir = path.join(repoRoot, ".docker-data", "command-output");
    dockerArgs.push("-v", `${outputDir}:/output`);
  }

  dockerArgs.push("-w", workdir, image, "sh", "-lc", cmd);

  const result = await runCommand("docker", dockerArgs, { cwd: repoRoot });

  return {
    ok: result.exitCode === 0,
    exit_code: result.exitCode,
    image,
    cmd,
    stdout: result.stdout,
    stderr: result.stderr,
    container_mode: "scratch",
  };
}