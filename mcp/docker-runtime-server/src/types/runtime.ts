export type ComposeMode = "live-bind" | "rebuild-image";
export type OutputKind = "logs" | "test-results" | "command-output";

export interface ToolResult {
  ok: boolean;
  message: string;
  data?: unknown;
}

export interface CommandExecutionResult {
  command: string[];
  exitCode: number;
  stdout: string;
  stderr: string;
  combined: string;
}

export interface OutputMetadata {
  command: string;
  mode?: ComposeMode;
  service?: string;
  exitCode: number;
  timestamp: string;
  outputFile?: string;
}
