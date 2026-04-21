import { composeDown } from "./tools/composeDown.js";
import { composeLogs } from "./tools/composeLogs.js";
import { composePs } from "./tools/composePs.js";
import { composeUp } from "./tools/composeUp.js";
import { copyFromContainer } from "./tools/copyFromContainer.js";
import { execApp } from "./tools/execApp.js";
import { execTaskRunner } from "./tools/execTaskRunner.js";
import { readContainerOutput } from "./tools/readContainerOutput.js";
import { rebuild } from "./tools/rebuild.js";
import { resolveImages } from "./tools/resolveImages.js";
import { formatError } from "./lib/errors.js";

const tools = {
  resolve_images: resolveImages,
  compose_up: composeUp,
  compose_down: composeDown,
  compose_ps: composePs,
  compose_logs: composeLogs,
  exec_app: execApp,
  exec_task_runner: execTaskRunner,
  rebuild,
  read_container_output: readContainerOutput,
  copy_from_container: copyFromContainer,
} as const;

type ToolName = keyof typeof tools;

async function main() {
  const [, , rawToolName, rawArgs] = process.argv;

  if (!rawToolName) {
    console.error(JSON.stringify({
      ok: false,
      message: "Provide a tool name as the first argument",
      availableTools: Object.keys(tools),
    }, null, 2));
    process.exit(1);
  }

  if (!(rawToolName in tools)) {
    console.error(JSON.stringify({
      ok: false,
      message: `Unknown tool: ${rawToolName}`,
      availableTools: Object.keys(tools),
    }, null, 2));
    process.exit(1);
  }

  try {
    const args = rawArgs ? JSON.parse(rawArgs) : {};
    const result = await tools[rawToolName as ToolName](args as never);
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(JSON.stringify({ ok: false, error: formatError(error) }, null, 2));
    process.exit(1);
  }
}

void main();
