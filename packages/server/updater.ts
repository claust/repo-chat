import type { Context } from "hono";
import { readdir } from "node:fs/promises";
import type { BlankEnv, BlankInput } from "hono/types";
import { ChromaClient } from "chromadb";

export async function updater(c: Context<BlankEnv, "/updater", BlankInput>): Promise<void | Response> {
    const includeText = c.req.query('includeText');

    const client = new ChromaClient();
    const collection = await client.getOrCreateCollection({ name: 'repo-chat' });
    const countInitial = await collection.count();

    const folder = './../..';
    var { files, log } = await getFilesToProcess(folder);
    log += `Collection ${collection.name}, ${countInitial} documents\n\n`;
    var currentIds: string[] = [];
    var docs = [];
    for (const file of files) {
        if (!await Bun.file(file).exists()) {
            console.log('Skipping folder', file);
            continue;
        }
        const { text, id } = await handleFile(file);
        currentIds.push(id);
        docs.push(text);
        log += `File [${id}]: ${file}\n\n`;
        if (includeText === 'true') {
            log += `${text}\n\n`;
        }
    }
    console.log('Adding', docs.length, currentIds.length, 'docs to collection');
    await collection.upsert({ ids: currentIds, documents: docs });
    console.log('Added', docs.length, 'docs to collection');
    const countFinal = await collection.count();
    log += `Collection ${collection.name}, ${countInitial - countFinal} documents ${countInitial - countFinal < 0 ? 'removed' : 'added'}\n\n`;

    // Remove docs that are no longer in the repo
    const allIds = await collection.peek({ limit: 1000 });
    const idsToRemove = allIds.ids.filter(id => !currentIds.includes(id));
    log += `Removing ${idsToRemove.length} documents\n\n`;
    await collection.delete({ ids: idsToRemove });
    log += `Collection ${collection.name}, ${await collection.count()} documents\n\n`;
    return c.text(log);
}

const ignoredExtensions = ['.bin', '.sqlite3'];

async function getFilesToProcess(folder: string) {
    const filesAndDirs = await readdir(folder, { recursive: true });
    let log = '';
    console.log('Found', filesAndDirs.length, 'folders/files');
    log += `Found ${filesAndDirs.length} folders/files\n\n`;
    const files = filesAndDirs.filter(f =>
        !f.includes('node_modules') &&
        !f.startsWith('.git') &&
        !ignoredExtensions.some(ext => f.endsWith(ext))
    ).map(f => `${folder}/${f}`);
    log += `Found ${files.length} files (excluding ignored folders)\n\n`;
    return { files, log };
}

async function handleFile(fileName: string) {
    const file = Bun.file(fileName);
    const text = await file.text();
    const id = Bun.hash(`${fileName}${text}`).toString();
    return { id, text };
}
