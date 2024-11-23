import { Hono } from "hono";
import { updater } from "./updater";

const app = new Hono();
app.get("/", (c) => {
    return c.text("Repo Chat!");
});

app.get("/updater", (c) => updater(c));

export default app;
