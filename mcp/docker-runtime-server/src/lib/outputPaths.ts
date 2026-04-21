import fs from "node:fs";
import path from "node:path";
import { OutputKind, OutputMetadata } from "../types/runtime.js";

export interface OutputContext {
  repoRoot: string;
  dockerDataRoot: string;
}

export function buildOutputContext(repoRoot: string): OutputContext {
  return {
    repoRoot,
    dockerDataRoot: path.join(repoRoot, ".docker-data"),
  };
}

export function ensureOutputDirs(ctx: OutputContext): void {
  for (const dir of ["logs", "test-results", "command-output"]) {
    fs.mkdirSync(path.join(ctx.dockerDataRoot, dir), { recursive: true });
  }
}

export function getOutputDir(ctx: OutputContext, kind: OutputKind): string {
  return path.join(ctx.dockerDataRoot, kind);
}

export function writeOutputFile(ctx: OutputContext, kind: OutputKind, fileName: string, contents: string): string {
  const filePath = path.join(getOutputDir(ctx, kind), fileName);
  fs.writeFileSync(filePath, contents, "utf8");
  return filePath;
}

export function writeMetadataFile(ctx: OutputContext, kind: OutputKind, fileName: string, metadata: OutputMetadata): string {
  const filePath = path.join(getOutputDir(ctx, kind), fileName);
  fs.writeFileSync(filePath, JSON.stringify(metadata, null, 2), "utf8");
  return filePath;
}

export function listOutputFiles(ctx: OutputContext, kind: OutputKind): string[] {
  const dir = getOutputDir(ctx, kind);
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).sort();
}
