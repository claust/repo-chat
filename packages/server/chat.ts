import type { Context } from "hono";
import type { BlankEnv, BlankInput } from "hono/types";
import { ChromaClient } from "chromadb";

export async function chat(
  c: Context<BlankEnv, "/chat", BlankInput>,
): Promise<void | Response> {
  let log = "";
  const message = c.req.query("message") ?? "Hello";
  const client = new ChromaClient();
  const collection = await client.getOrCreateCollection({ name: "repo-chat" });
  const results = await collection.query({
    queryTexts: [message],
    nResults: 4,
    include: ["documents", "distances"],
  });

  const docs = results.documents[0];
  const ids = results.ids[0];
  const distances = results.distances ? results.distances[0] : [];
  // Sort the docs according to the distances
  const sortedDocs = docs
    .map((doc, index) => ({ doc, distance: distances[index] }))
    .sort((a, b) => a.distance - b.distance);
  log += `Found ${sortedDocs.length} source files\n\n`;
  log += `Ids: ${ids.length}\n\n`;
  sortedDocs.forEach((doc) => {
    log += `File [${doc.doc?.length}]: ${doc.distance}, content: ${doc.doc?.substring(0, 10)}\n`;
    // log += `Index: ${index}\n\n`;
    // log += `Metadata: ${results.metadatas[index]}\n\n`;
  });
  return c.text(log);
}
