import type { Context } from "hono";
import type { BlankEnv, BlankInput } from "hono/types";

export async function updater(c: Context<BlankEnv, "/updater", BlankInput>): Promise<void | Response> {
    const fileName = './app.ts';
    const file = Bun.file(fileName);
    const text = await file.text();

    return c.text(`File: ${fileName}\n\n${text}`);
}
