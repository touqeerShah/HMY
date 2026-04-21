export async function resolveImages(args: { target_id: string; mode: string; roles?: string[] }) {
  return {
    ok: true,
    message: "Runtime MCP image resolution placeholder",
    data: {
      targetId: args.target_id,
      mode: args.mode,
      roles: args.roles ?? [],
      note: "Wire this tool to your existing docker-hub MCP or image selection report. Keep final image lookup logic outside runtime execution handlers.",
    },
  };
}
