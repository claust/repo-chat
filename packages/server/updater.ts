import type { Context } from "hono";
import { readdir } from "node:fs/promises";
import type { BlankEnv, BlankInput } from "hono/types";

export async function updater(c: Context<BlankEnv, "/updater", BlankInput>): Promise<void | Response> {
    const includeText = c.req.query('includeText');
    const files = await readdir('./', { recursive: true });
    let result = '';
    for (const file of files) {
        const text = await handleFile(file);
        result += `File: ${file}\n\n`;
        if (includeText === 'true') {
            result += `${text}\n\n`;
        }
    }
    return c.text(result);
}

async function handleFile(fileName: string) {
    const file = Bun.file(fileName);
    const text = await file.text();
    return text;
}

