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
  assert.match(await response.text(), /Private Rules Library/);
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
  assert.match(await response.text(), /fetch\("\/api\/spells"\)/);
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
