import fs from "node:fs";
import path from "node:path";
export function buildOutputContext(repoRoot) {
    return {
        repoRoot,
        dockerDataRoot: path.join(repoRoot, ".docker-data"),
    };
}
export function ensureOutputDirs(ctx) {
    for (const dir of ["logs", "test-results", "command-output"]) {
        fs.mkdirSync(path.join(ctx.dockerDataRoot, dir), { recursive: true });
    }
}
export function getOutputDir(ctx, kind) {
    return path.join(ctx.dockerDataRoot, kind);
}
export function writeOutputFile(ctx, kind, fileName, contents) {
    const filePath = path.join(getOutputDir(ctx, kind), fileName);
    fs.writeFileSync(filePath, contents, "utf8");
    return filePath;
}
export function writeMetadataFile(ctx, kind, fileName, metadata) {
    const filePath = path.join(getOutputDir(ctx, kind), fileName);
    fs.writeFileSync(filePath, JSON.stringify(metadata, null, 2), "utf8");
    return filePath;
}
export function listOutputFiles(ctx, kind) {
    const dir = getOutputDir(ctx, kind);
    if (!fs.existsSync(dir))
        return [];
    return fs.readdirSync(dir).sort();
}
