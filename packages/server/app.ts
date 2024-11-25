import { Hono } from "hono";
import { updater } from "./updater";
import { chat } from "./chat";

const app = new Hono();
app.get("/", (c) => {
  return c.text("Repo Chat!");
});

app.get("/chat", (c) => chat(c));
app.get("/updater", (c) => updater(c));

export default app;
