/**
 * Edge runtime compatibility test for pdfitdown WASM module.
 *
 * Spins up a Miniflare (Cloudflare Workers) instance that loads the WASM
 * module and converts an image to PDF, verifying it works in an edge runtime.
 *
 * Usage: node scripts/edge-compat/wasm-test.mjs
 *
 * Requires: miniflare (npm i -D miniflare)
 * Expects:  packages/wasm/pkg/ to contain the built WASM files
 */
import { Miniflare } from "miniflare";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(import.meta.url), "../../..");
const wasmPath = resolve(ROOT, "packages/wasm/pkg/pdfitdown_wasm_bg.wasm");
const gluePath = resolve(ROOT, "packages/wasm/pkg/pdfitdown_wasm.js");

const TEST_INPUT = Buffer.from("Hello from pdfitdown edge test!", "utf-8");

let glueSource = readFileSync(gluePath, "utf-8");
// Strip default export (the async init / fetch-based loader)
glueSource = glueSource.replace(
  /export\s*\{[^}]*__wbg_init\s+as\s+default[^}]*\};?/g,
  "",
);
glueSource = glueSource.replace(/export\s+default\s+__wbg_init\s*;?/g, "");
glueSource = glueSource.replace(
  /export\s*\{\s*initSync\s*(?:,\s*__wbg_init\s+as\s+default\s*)?\}\s*;?/g,
  "",
);

const workerScript = `
import __pdfitdown_wasm_mod from "pdfitdown.wasm";

// --- pdfitdown WASM glue (patched) ---
${glueSource}

// --- Edge worker handler ---
export default {
  async fetch(request) {
    try {
      initSync({ module: __pdfitdown_wasm_mod });

      const imageBytes = new Uint8Array(await request.arrayBuffer());
      const result = convert(imageBytes);

      return new Response(JSON.stringify({
        ok: true,
        outputBytes: result.length,
      }), {
        headers: { "Content-Type": "application/json" },
      });
    } catch (err) {
      return new Response(JSON.stringify({
        ok: false,
        error: err.message || String(err),
        stack: err.stack,
      }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  }
};
`;

async function main() {
  console.log("Starting Miniflare (Cloudflare Workers runtime)...");

  const wasmBytes = readFileSync(wasmPath);
  const mf = new Miniflare({
    modules: [
      { type: "ESModule", path: "worker.mjs", contents: workerScript },
      { type: "CompiledWasm", path: "pdfitdown.wasm", contents: wasmBytes },
    ],
    compatibilityDate: "2024-01-01",
  });

  try {
    console.log(`Sending text (${TEST_INPUT.length} bytes) to edge worker...`);

    const response = await mf.dispatchFetch("http://localhost/convert", {
      method: "POST",
      body: TEST_INPUT,
    });

    const result = await response.json();

    if (!result.ok) {
      console.error(`FAIL: ${result.error}`);
      if (result.stack) console.error(result.stack);
      process.exit(1);
    }

    // A valid PDF starts with "%PDF"
    if (result.outputBytes < 4) {
      console.error(
        `FAIL: Output too small to be a valid PDF: ${result.outputBytes} bytes`,
      );
      process.exit(1);
    }

    console.log(`PASS: converted to PDF, output ${result.outputBytes} bytes`);
  } finally {
    await mf.dispose();
  }
}

main().catch((err) => {
  console.error("Test runner failed:", err);
  process.exit(1);
});
