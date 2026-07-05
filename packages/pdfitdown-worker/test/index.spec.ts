import { env, createExecutionContext, waitOnExecutionContext, SELF } from 'cloudflare:test';
import { describe, it, expect } from 'vitest';
import worker from '../src/index';

// For now, you'll need to do something like this to get a correctly-typed
// `Request` to pass to `worker.fetch()`.
const IncomingRequest = Request<unknown, IncomingRequestCfProperties>;

function isPdf(fd: Buffer): boolean {
	return (
		fd[0] === 0x25 && // %
		fd[1] === 0x50 && // P
		fd[2] === 0x44 && // D
		fd[3] === 0x46 // F
	);
}

describe('PdfItDown worker', () => {
	it('responds PDF binary data', async () => {
		const buf = new TextEncoder().encode('# Hello\nThis is some **markdown** text.');
		const request = new IncomingRequest('http://localhost', {
			method: 'POST',
			headers: { 'Content-Type': 'application/octet-stream' },
			body: buf,
		});
		// Create an empty context to pass to `worker.fetch()`.
		const ctx = createExecutionContext();
		const response = await worker.fetch(request, env, ctx);
		// Wait for all `Promise`s passed to `ctx.waitUntil()` to settle before running test assertions
		await waitOnExecutionContext(ctx);
		expect(isPdf(Buffer.from(await response.arrayBuffer()))).toBe(true);
	});
});
