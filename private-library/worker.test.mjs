import assert from "node:assert/strict";
import test from "node:test";

import { handleRequest } from "./worker.mjs";

const accessHeaders = {
  "Cf-Access-Authenticated-User-Email": "owner@example.test",
  "Cf-Access-Jwt-Assertion": "test-assertion",
};

const pdfBytes = new Uint8Array([37, 80, 68, 70]);
const spellIndex = JSON.stringify({
  spells: [
    {
      name: "Test Spell",
      page: 42,
      school: "Evocation",
      levels: "Sor/Wiz 3",
    },
  ],
});
const spellV2Index = JSON.stringify({
  spells: [
    {
      name: "Second Test Spell",
      page: 77,
      school: "Transmutation",
      levels: "Wizard 4",
    },
  ],
});
const env = {
  ALLOWED_EMAIL: "owner@example.test",
  PRIVATE_LIBRARY: {
    async get(key) {
      if (key === "Spell Compendium.pdf") {
        return { body: pdfBytes, size: pdfBytes.byteLength };
      }
      if (key === "spell-compendium-index.json") {
        return { body: spellIndex, size: spellIndex.length };
      }
      if (key === "Spell Compendium v2.pdf") {
        return { body: pdfBytes, size: pdfBytes.byteLength };
      }
      if (key === "spell-compendium-v2-index.json") {
        return { body: spellV2Index, size: spellV2Index.length };
      }
      return null;
    },
  },
};

test("rejects requests without Cloudflare Access identity", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/"),
    env,
  );
  assert.equal(response.status, 403);
  assert.equal(response.headers.get("Cache-Control"), "private, no-store");
});

test("serves the private library to the allowed email", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/", { headers: accessHeaders }),
    env,
  );
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Private Rules Library/);
  assert.match(html, /Spell Compendium v2/);
  assert.match(response.headers.get("Content-Security-Policy"), /frame-ancestors 'none'/);
});

test("serves the private client-side search script", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/library.js", {
      headers: accessHeaders,
    }),
    env,
  );
  assert.equal(response.status, 200);
  assert.match(response.headers.get("Content-Type"), /text\/javascript/);
  const script = await response.text();
  assert.match(script, /api: "\/api\/spells"/);
  assert.match(script, /api: "\/api\/spells-v2"/);
});

test("serves the Spell Compendium v2 index", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/api/spells-v2", {
      headers: accessHeaders,
    }),
    env,
  );
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), JSON.parse(spellV2Index));
});

test("serves the private non-SRD spell index", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/api/spells", {
      headers: accessHeaders,
    }),
    env,
  );
  assert.equal(response.status, 200);
  assert.match(response.headers.get("Content-Type"), /application\/json/);
  assert.deepEqual(await response.json(), JSON.parse(spellIndex));
});

test("streams the Spell Compendium v2 PDF", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/spell-compendium-v2.pdf", {
      headers: accessHeaders,
    }),
    env,
  );
  assert.equal(response.status, 200);
  assert.equal(
    response.headers.get("Content-Disposition"),
    'inline; filename="Spell-Compendium-v2.pdf"',
  );
});

test("streams the private PDF with safe headers", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/spell-compendium.pdf", {
      headers: accessHeaders,
    }),
    env,
  );
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("Content-Type"), "application/pdf");
  assert.equal(
    response.headers.get("Content-Disposition"),
    'inline; filename="Spell-Compendium.pdf"',
  );
  assert.deepEqual(
    new Uint8Array(await response.arrayBuffer()),
    pdfBytes,
  );
});

test("returns a private 404 for unknown paths", async () => {
  const response = await handleRequest(
    new Request("https://library.d20srdhub.com/missing", {
      headers: accessHeaders,
    }),
    env,
  );
  assert.equal(response.status, 404);
  assert.equal(response.headers.get("Cache-Control"), "private, no-store");
});
