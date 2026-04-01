import express from "express";
import { dirname, join, resolve } from "path";
import { fileURLToPath } from "url";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { runCopilotStream, findCopilotBin } from "./copilot.ts";
import { PRESETS, type PresetQuery } from "./presets.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || "3120", 10);

// Resolve the project root (parent of copilot-dash) as the working directory
const PROJECT_ROOT = resolve(__dirname, "..", "..");
const DASH_ROOT = resolve(__dirname, "..");
const SAVED_DIR = join(DASH_ROOT, "saved");
const CUSTOM_PRESETS_FILE = join(DASH_ROOT, "custom-presets.json");

// ─── Custom presets persistence ─────────────────────────────────
function loadCustomPresets(): PresetQuery[] {
  if (!existsSync(CUSTOM_PRESETS_FILE)) return [];
  try {
    return JSON.parse(readFileSync(CUSTOM_PRESETS_FILE, "utf-8"));
  } catch {
    return [];
  }
}

function saveCustomPresets(presets: PresetQuery[]): void {
  writeFileSync(CUSTOM_PRESETS_FILE, JSON.stringify(presets, null, 2));
}

let customPresets = loadCustomPresets();

const app = express();
app.use(express.json());

// Serve static UI
app.use(express.static(join(__dirname, "..", "public")));

// ─── API: Get presets (built-in + custom) ────────────────────────
app.get("/api/presets", (_req, res) => {
  res.json([...PRESETS, ...customPresets]);
});

// ─── API: Add custom preset ─────────────────────────────────────
app.post("/api/presets", (req, res) => {
  const { label, category, prompt, description, effort, tools } = req.body;

  if (
    !label ||
    typeof label !== "string" ||
    !prompt ||
    typeof prompt !== "string"
  ) {
    res.status(400).json({ error: "label and prompt are required" });
    return;
  }

  const validCategories = ["escalation", "qase", "jira", "analysis", "custom"];
  const cat = validCategories.includes(category) ? category : "custom";

  const preset: PresetQuery = {
    id: `custom-${Date.now()}`,
    label: label.trim(),
    category: cat,
    prompt: prompt.trim(),
    description: description?.trim() || undefined,
    effort: effort || undefined,
    tools: tools ?? true,
    custom: true,
  };

  customPresets.push(preset);
  saveCustomPresets(customPresets);
  res.json(preset);
});

// ─── API: Delete custom preset ──────────────────────────────────
app.delete("/api/presets/:id", (req, res) => {
  const { id } = req.params;
  if (!id.startsWith("custom-")) {
    res.status(403).json({ error: "Cannot delete built-in presets" });
    return;
  }

  const idx = customPresets.findIndex((p) => p.id === id);
  if (idx === -1) {
    res.status(404).json({ error: "Preset not found" });
    return;
  }

  customPresets.splice(idx, 1);
  saveCustomPresets(customPresets);
  res.json({ ok: true });
});

// ─── API: Save response to file ─────────────────────────────────
app.post("/api/save-response", (req, res) => {
  const { content, title } = req.body;

  if (!content || typeof content !== "string") {
    res.status(400).json({ error: "content is required" });
    return;
  }

  if (!existsSync(SAVED_DIR)) {
    mkdirSync(SAVED_DIR, { recursive: true });
  }

  const now = new Date();
  const ts = now.toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const slug = (title || "response")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 60);
  const filename = `${ts}_${slug}.md`;
  const filepath = join(SAVED_DIR, filename);

  const header = `# ${title || "Copilot Response"}\n\n_Saved: ${now.toLocaleString()}_\n\n---\n\n`;
  writeFileSync(filepath, header + content);

  res.json({ ok: true, path: filepath, filename });
});

// ─── API: Health check ──────────────────────────────────────────
app.get("/api/health", (_req, res) => {
  const bin = findCopilotBin();
  res.json({ ok: !!bin, copilotBin: bin, projectRoot: PROJECT_ROOT });
});

// ─── API: Run query (SSE streaming) ─────────────────────────────
app.post("/api/query", async (req, res) => {
  const { prompt, effort, model, tools, allowAll, json: jsonOutput } = req.body;

  if (!prompt || typeof prompt !== "string") {
    res.status(400).json({ error: "prompt is required" });
    return;
  }

  // Set up SSE
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  res.flushHeaders();

  try {
    const stream = runCopilotStream({
      prompt,
      effort: effort || undefined,
      model: model || undefined,
      tools: tools ?? true,
      allowAll: allowAll || false,
      json: jsonOutput || false,
      cwd: PROJECT_ROOT,
    });

    for await (const chunk of stream) {
      res.write(`data: ${JSON.stringify({ type: "chunk", text: chunk })}\n\n`);
    }

    res.write(`data: ${JSON.stringify({ type: "done" })}\n\n`);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    res.write(`data: ${JSON.stringify({ type: "error", text: message })}\n\n`);
  } finally {
    res.end();
  }
});

// ─── API: Run chained queries (SSE streaming) ───────────────────
app.post("/api/query-chain", async (req, res) => {
  const { queries } = req.body;

  if (!Array.isArray(queries) || queries.length === 0) {
    res.status(400).json({ error: "queries array is required" });
    return;
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  res.flushHeaders();

  let previousOutput = "";

  for (let i = 0; i < queries.length; i++) {
    const q = queries[i];
    const label = q.label || `Query ${i + 1}`;

    res.write(
      `data: ${JSON.stringify({ type: "chain-start", index: i, label })}\n\n`,
    );

    // Inject previous output as context if chaining
    let prompt = q.prompt;
    if (i > 0 && previousOutput) {
      prompt = `Context from previous query:\n\n${previousOutput}\n\n---\n\nNow: ${prompt}`;
    }

    try {
      const chunks: string[] = [];
      const stream = runCopilotStream({
        prompt,
        effort: q.effort || undefined,
        model: q.model || undefined,
        tools: q.tools ?? true,
        cwd: PROJECT_ROOT,
      });

      for await (const chunk of stream) {
        chunks.push(chunk);
        res.write(
          `data: ${JSON.stringify({ type: "chunk", index: i, text: chunk })}\n\n`,
        );
      }

      previousOutput = chunks.join("");
      res.write(`data: ${JSON.stringify({ type: "chain-end", index: i })}\n\n`);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      res.write(
        `data: ${JSON.stringify({ type: "error", index: i, text: message })}\n\n`,
      );
      break;
    }
  }

  res.write(`data: ${JSON.stringify({ type: "done" })}\n\n`);
  res.end();
});

app.listen(PORT, () => {
  console.log(`\n  🚀 Copilot Dash running at http://localhost:${PORT}\n`);
  console.log(`  Project root: ${PROJECT_ROOT}`);
  console.log(`  Copilot CLI:  ${findCopilotBin() || "NOT FOUND"}\n`);
});
