import { spawn } from "child_process";
import { existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";
import { Readable } from "stream";

const COPILOT_BUNDLED = join(
  homedir(),
  "Library/Application Support/Code/User/globalStorage/github.copilot-chat/copilotCli/copilot",
);

export interface CopilotOptions {
  prompt: string;
  effort?: "low" | "medium" | "high" | "xhigh";
  model?: string;
  tools?: boolean;
  allowAll?: boolean;
  json?: boolean;
  cwd?: string;
}

export function findCopilotBin(): string | null {
  // Check bundled VS Code location
  if (existsSync(COPILOT_BUNDLED)) return COPILOT_BUNDLED;
  // Fallback: assume on PATH
  return "copilot";
}

export function buildArgs(opts: CopilotOptions): string[] {
  const args = ["-p", opts.prompt, "-s"];

  if (opts.effort) args.push("--effort", opts.effort);
  if (opts.model) args.push("--model", opts.model);
  if (opts.json) args.push("--output-format", "json");
  if (opts.tools) args.push("--allow-all-tools");
  if (opts.allowAll) args.push("--allow-all");

  return args;
}

/**
 * Run a copilot query and stream output chunks via an async generator.
 */
export async function* runCopilotStream(
  opts: CopilotOptions,
): AsyncGenerator<string> {
  const bin = findCopilotBin();
  if (!bin) throw new Error("copilot CLI not found");

  const args = buildArgs(opts);
  const cwd = opts.cwd || process.cwd();

  const child = spawn(bin, args, {
    cwd,
    stdio: ["ignore", "pipe", "pipe"],
  });

  const stdout = Readable.toWeb(child.stdout!) as ReadableStream<Uint8Array>;
  const decoder = new TextDecoder();

  const reader = stdout.getReader();
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      yield decoder.decode(value, { stream: true });
    }
  } finally {
    reader.releaseLock();
  }

  // Collect stderr
  const stderrChunks: Buffer[] = [];
  child.stderr?.on("data", (chunk: Buffer) => stderrChunks.push(chunk));

  const exitCode = await new Promise<number>((resolve) => {
    child.on("close", (code) => resolve(code ?? 1));
  });

  if (exitCode !== 0) {
    const stderr = Buffer.concat(stderrChunks).toString();
    throw new Error(`copilot exited with code ${exitCode}: ${stderr}`);
  }
}

/**
 * Run a copilot query and return full output as a string.
 */
export async function runCopilot(opts: CopilotOptions): Promise<string> {
  const chunks: string[] = [];
  for await (const chunk of runCopilotStream(opts)) {
    chunks.push(chunk);
  }
  return chunks.join("");
}
