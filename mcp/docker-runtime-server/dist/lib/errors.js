export class RuntimeMcpError extends Error {
    code;
    details;
    constructor(code, message, details) {
        super(message);
        this.name = "RuntimeMcpError";
        this.code = code;
        this.details = details;
    }
}
export function formatError(error) {
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
