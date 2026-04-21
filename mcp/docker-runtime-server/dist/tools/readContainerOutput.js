import fs from "node:fs";
import path from "node:path";
import { buildOutputContext, getOutputDir } from "../lib/outputPaths.js";
export async function readContainerOutput(args) {
    const repoRoot = args.repoRoot ?? process.cwd();
    const ctx = buildOutputContext(repoRoot);
    const baseDir = getOutputDir(ctx, args.kind);
    const targetPath = path.resolve(baseDir, args.path);
    if (!targetPath.startsWith(baseDir)) {
        return {
            ok: false,
            message: "Refusing to read outside allowed output directory",
        };
    }
    if (!fs.existsSync(targetPath)) {
        return {
            ok: false,
            message: `Output file not found: ${args.path}`,
        };
    }
    return {
        ok: true,
        message: `Read ${args.kind} output file`,
        data: {
            kind: args.kind,
            path: args.path,
            contents: fs.readFileSync(targetPath, "utf8"),
        },
    };
}
