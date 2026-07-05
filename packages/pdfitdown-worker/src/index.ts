/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Bind resources to your worker in `wrangler.jsonc`. After adding bindings, a type definition for the
 * `Env` object can be regenerated with `npm run cf-typegen`.
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */

import { convert, initSync } from '@cle-does-things/pdfitdown-wasm';
import wasmModule from '../pdfitdown_wasm_bg.wasm';

let initialized = false;

export default {
	async fetch(request, env, ctx): Promise<Response> {
		if (!initialized) {
			initSync({ module: wasmModule });
			initialized = true;
		}
		const buf = await request.arrayBuffer();
		const converted = convert(new Uint8Array(buf));

		return new Response(converted, {
			headers: { 'Content-Type': 'application/octet-stream' },
		});
	},
} satisfies ExportedHandler<Env>;
