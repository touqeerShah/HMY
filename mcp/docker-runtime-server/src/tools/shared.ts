import path from "node:path";
import { buildOutputContext, ensureOutputDirs, writeMetadataFile, writeOutputFile } from "../lib/outputPaths.js";
import { OutputKind } from "../types/runtime.js";

export function nowStamp(): string {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

export function ensureRuntimeOutput(repoRoot: string) {
  const ctx = buildOutputContext(repoRoot);
  ensureOutputDirs(ctx);
  return ctx;
}

export function persistExecutionArtifacts(args: {
  repoRoot: string;
  kind: OutputKind;
  prefix: string;
  body: string;
  metadata: {
    command: string;
    service?: string;
    mode?: "live-bind" | "rebuild-image";
    exitCode: number;
  };
}) {
  const ctx = ensureRuntimeOutput(args.repoRoot);
  const stamp = nowStamp();
  const outputFileName = `${args.prefix}-${stamp}.log`;
  const metadataFileName = `${args.prefix}-${stamp}.json`;
  const outputPath = writeOutputFile(ctx, args.kind, outputFileName, args.body);
  const metadataPath = writeMetadataFile(ctx, args.kind, metadataFileName, {
    ...args.metadata,
    timestamp: new Date().toISOString(),
    outputFile: path.relative(args.repoRoot, outputPath),
  });

  return {
    outputPath,
    metadataPath,
  };
}
