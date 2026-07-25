import { test } from "node:test";
import assert from "node:assert/strict";

test("Test-Läufer und ESM funktionieren", () => {
  assert.equal(typeof import.meta.url, "string");
});
