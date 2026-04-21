import path from "node:path";
import { buildOutputContext, ensureOutputDirs, writeMetadataFile, writeOutputFile } from "../lib/outputPaths.js";
export function nowStamp() {
    return new Date().toISOString().replace(/[:.]/g, "-");
}
export function ensureRuntimeOutput(repoRoot) {
    const ctx = buildOutputContext(repoRoot);
    ensureOutputDirs(ctx);
    return ctx;
}
export function persistExecutionArtifacts(args) {
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
