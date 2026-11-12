import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { generateCalendarIcs, parseEvents } from "./calendar.js";

const EVENTS_PATH = "data/events.json";
const OUTPUT_DIR = "public";
const OUTPUT_PATH = `${OUTPUT_DIR}/calendar.ics`;

const events = parseEvents(JSON.parse(await readFile(EVENTS_PATH, "utf8")));
const ics = generateCalendarIcs(events);

// Write to a temp file first so a failure never leaves a broken calendar.
await mkdir(OUTPUT_DIR, { recursive: true });
await writeFile(`${OUTPUT_PATH}.tmp`, ics);
await rename(`${OUTPUT_PATH}.tmp`, OUTPUT_PATH);

console.log(`Generated ${OUTPUT_PATH} with ${events.length} event(s).`);
