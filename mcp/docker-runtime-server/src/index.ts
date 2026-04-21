import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

import { composeDown } from "./tools/composeDown.js";
import { composeLogs } from "./tools/composeLogs.js";
import { composePs } from "./tools/composePs.js";
import { composeUp } from "./tools/composeUp.js";
import { copyFromContainer } from "./tools/copyFromContainer.js";
import { execApp } from "./tools/execApp.js";
import { execScratch } from "./tools/execScratch.js";
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
  exec_scratch: execScratch,
  rebuild,
  read_container_output: readContainerOutput,
  copy_from_container: copyFromContainer,
} as const;

type ToolName = keyof typeof tools;

const toolDefinitions = [
  {
    name: "resolve_images",
    description: "Resolve application and service images for a target and mode.",
    inputSchema: {
      type: "object",
      properties: {
        target_id: { type: "string" },
        mode: { type: "string" },
        roles: {
          type: "array",
          items: { type: "string" },
        },
        repoRoot: { type: "string" },
      },
      additionalProperties: true,
    },
  },
  {
    name: "compose_up",
    description: "Start the compose stack in detached mode.",
    inputSchema: {
      type: "object",
      properties: {
        mode: { type: "string" },
        repoRoot: { type: "string" },
      },
      additionalProperties: true,
    },
  },
  {
    name: "compose_down",
    description: "Stop and remove the compose stack.",
    inputSchema: {
      type: "object",
      properties: {
        mode: { type: "string" },
        repoRoot: { type: "string" },
      },
      additionalProperties: true,
    },
  },
  {
    name: "compose_ps",
    description: "Show compose service status.",
    inputSchema: {
      type: "object",
      properties: {
        mode: { type: "string" },
        repoRoot: { type: "string" },
      },
      additionalProperties: true,
    },
  },
  {
    name: "compose_logs",
    description: "Read compose logs for a service or the full stack.",
    inputSchema: {
      type: "object",
      properties: {
        mode: { type: "string" },
        service: { type: "string" },
        tail: { type: "number" },
        repoRoot: { type: "string" },
      },
      additionalProperties: true,
    },
  },
  {
    name: "exec_app",
    description: "Run a command in the app container.",
    inputSchema: {
      type: "object",
      properties: {
        cmd: {
          oneOf: [
            { type: "string" },
            { type: "array", items: { type: "string" } },
          ],
        },
        mode: { type: "string" },
        repoRoot: { type: "string" },
      },
      required: ["cmd"],
      additionalProperties: true,
    },
  },
  {
    name: "exec_task_runner",
    description: "Run a command in the task-runner container.",
    inputSchema: {
      type: "object",
      properties: {
        cmd: {
          oneOf: [
            { type: "string" },
            { type: "array", items: { type: "string" } },
          ],
        },
        mode: { type: "string" },
        repoRoot: { type: "string" },
      },
      required: ["cmd"],
      additionalProperties: true,
    },
  },
  {
    name: "exec_scratch",
    description:
      "Run a one-off command in a temporary scratch container for non-project experiments.",
    inputSchema: {
      type: "object",
      properties: {
        cmd: {
          oneOf: [
            { type: "string" },
            { type: "array", items: { type: "string" } },
          ],
        },
        image: { type: "string" },
        repoRoot: { type: "string" },
        mountOutput: { type: "boolean" },
        workdir: { type: "string" },
      },
      required: ["cmd"],
      additionalProperties: true,
    },
  },
  {
    name: "rebuild",
    description: "Rebuild docker images for the selected mode.",
    inputSchema: {
      type: "object",
      properties: {
        mode: { type: "string" },
        repoRoot: { type: "string" },
      },
      additionalProperties: true,
    },
  },
  {
    name: "read_container_output",
    description: "Read a saved output artifact from the container/output area.",
    inputSchema: {
      type: "object",
      properties: {
        kind: { type: "string" },
        path: { type: "string" },
        repoRoot: { type: "string" },
      },
      additionalProperties: true,
    },
  },
  {
    name: "copy_from_container",
    description: "Copy a file from a container path to a local destination.",
    inputSchema: {
      type: "object",
      properties: {
        container: { type: "string" },
        src: { type: "string" },
        dest: { type: "string" },
        repoRoot: { type: "string" },
      },
      required: ["container", "src", "dest"],
      additionalProperties: true,
    },
  },
];

const server = new Server(
  {
    name: "docker-runtime",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: toolDefinitions };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const name = request.params.name as ToolName;
  const args = (request.params.arguments ?? {}) as Record<string, unknown>;

  if (!(name in tools)) {
    throw new Error(`Unknown tool: ${name}`);
  }

  try {
    const result = await tools[name](args as never);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            { ok: false, error: formatError(error) },
            null,
            2
          ),
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

void main();