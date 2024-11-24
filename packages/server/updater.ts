import type { Context } from "hono";
import { readdir } from "node:fs/promises";
import type { BlankEnv, BlankInput } from "hono/types";

export async function updater(c: Context<BlankEnv, "/updater", BlankInput>): Promise<void | Response> {
    const includeText = c.req.query('includeText');
    const folder = './../..';
    var { files, log } = await getFilesToProcess(folder);

    for (const file of files) {
        if (!await Bun.file(file).exists()) {
            console.log('Skipping folder', file);
            continue;
        }
        const text = await handleFile(file);
        log += `File: ${file}\n\n`;
        if (includeText === 'true') {
            log += `${text}\n\n`;
        }
    }

    return c.text(log);
}

async function getFilesToProcess(folder: string) {
    const filesAndDirs = await readdir(folder, { recursive: true });
    let log = '';
    console.log('Found', filesAndDirs.length, 'folders/files');
    log += `Found ${filesAndDirs.length} folders/files\n\n`;
    const files = filesAndDirs.filter(f => !f.includes('node_modules') && !f.startsWith('.git')).map(f => `${folder}/${f}`);
    console.log('Found', files.length, 'files (excluding ignored folders)');
    log += `Found ${files.length} files (excluding ignored folders)\n\n`;
    return { files, log };
}

async function handleFile(fileName: string) {
    const file = Bun.file(fileName);
    const text = await file.text();
    return text;
}

