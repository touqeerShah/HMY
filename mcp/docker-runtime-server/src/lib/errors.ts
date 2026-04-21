export class RuntimeMcpError extends Error {
  public readonly code: string;
  public readonly details?: Record<string, unknown>;

  constructor(code: string, message: string, details?: Record<string, unknown>) {
    super(message);
    this.name = "RuntimeMcpError";
    this.code = code;
    this.details = details;
  }
}

export function formatError(error: unknown): { code: string; message: string; details?: Record<string, unknown> } {
  if (error instanceof RuntimeMcpError) {
    return {
      code: error.code,
      message: error.message,
      details: error.details,
    };
  }

  if (error instanceof Error) {
    return {
      code: "UNEXPECTED_ERROR",
      message: error.message,
    };
  }

  return {
    code: "UNKNOWN_ERROR",
    message: "Unknown runtime MCP error",
  };
}
