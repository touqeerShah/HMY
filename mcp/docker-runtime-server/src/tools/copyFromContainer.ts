import path from "node:path";
import fs from "node:fs";
import { dockerCp } from "../lib/docker.js";

export async function copyFromContainer(args: { container: string; src: string; dest: string; repoRoot?: string }) {
  const repoRoot = args.repoRoot ?? process.cwd();
  const dest = path.resolve(repoRoot, args.dest);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  const result = await dockerCp(args.container, args.src, dest, repoRoot);

  return {
    ok: result.exitCode === 0,
    message: result.exitCode === 0 ? `Copied ${args.src} from ${args.container}` : `Failed to copy ${args.src} from ${args.container}`,
    data: {
      container: args.container,
      src: args.src,
      dest,
      stdout: result.stdout,
      stderr: result.stderr,
      exitCode: result.exitCode,
    },
  };
}
