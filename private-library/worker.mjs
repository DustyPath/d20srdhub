const PDF_KEY = "Spell Compendium.pdf";
const SPELL_INDEX_KEY = "spell-compendium-index.json";
const PDF_V2_KEY = "Spell Compendium v2.pdf";
const SPELL_V2_INDEX_KEY = "spell-compendium-v2-index.json";

const SECURITY_HEADERS = {
  "Cache-Control": "private, no-store",
  "Content-Security-Policy":
    "default-src 'none'; style-src 'unsafe-inline'; script-src 'self'; connect-src 'self'; img-src 'self'; frame-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
  "Referrer-Policy": "no-referrer",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
};

const LIBRARY_HTML = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Private Rules Library | d20 SRD Hub</title>
  <style>
    :root {
      color-scheme: dark;
      --ink: #e8dcc1;
      --muted: #b8a98d;
      --gold: #d7ae5d;
      --gold-dark: #78582a;
      --stone: #1e1a16;
      --panel: #29231c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at top, rgb(122 80 35 / 28%), transparent 42rem),
        repeating-linear-gradient(90deg, rgb(255 255 255 / 2%) 0 1px, transparent 1px 5px),
        #100e0c;
      font-family: Georgia, "Times New Roman", serif;
    }
    header {
      padding: 2.5rem 1.25rem 2rem;
      text-align: center;
      border-bottom: 1px solid var(--gold-dark);
      background: linear-gradient(#241d15e8, #15120fee);
    }
    header a { color: var(--gold); text-decoration: none; }
    h1 { margin: .35rem 0; color: var(--gold); font-size: clamp(2rem, 7vw, 4rem); }
    .eyebrow { margin: 0; color: var(--muted); letter-spacing: .16em; text-transform: uppercase; }
    main { width: min(900px, calc(100% - 2rem)); margin: 3rem auto; }
    .shelf {
      padding: clamp(1.5rem, 5vw, 3rem);
      border: 1px solid var(--gold-dark);
      box-shadow: 0 12px 36px #0009, inset 0 0 30px #0004;
      background: linear-gradient(135deg, #30271e, var(--panel));
    }
    h2 { margin-top: 0; color: var(--gold); font-size: 2rem; }
    p { line-height: 1.7; }
    .book {
      display: grid;
      gap: .6rem;
      margin-top: 2rem;
      padding: 1.35rem;
      border-left: 6px solid #8e3a2b;
      background: #171411;
    }
    .book h3 { margin: 0; color: #f2d48d; font-size: 1.4rem; }
    .book p { margin: 0; color: var(--muted); }
    .button {
      justify-self: start;
      margin-top: .75rem;
      padding: .75rem 1.15rem;
      border: 1px solid #b88a3c;
      color: #21170a;
      background: linear-gradient(#e3c173, #ad7e31);
      font-weight: 700;
      text-decoration: none;
      box-shadow: 0 3px 0 #5c401c;
    }
    .search {
      margin-top: 2rem;
      padding: 1.35rem;
      border: 1px solid var(--gold-dark);
      background: #171411;
    }
    .search label {
      display: block;
      margin-bottom: .55rem;
      color: #f2d48d;
      font-weight: 700;
    }
    .search input {
      width: 100%;
      padding: .85rem 1rem;
      border: 1px solid var(--gold-dark);
      border-radius: 3px;
      color: var(--ink);
      background: #0f0d0b;
      font: inherit;
    }
    .search select {
      width: 100%;
      margin-bottom: .8rem;
      padding: .75rem 1rem;
      border: 1px solid var(--gold-dark);
      border-radius: 3px;
      color: var(--ink);
      background: #0f0d0b;
      font: inherit;
    }
    .search-status { color: var(--muted); }
    .results { display: grid; gap: .65rem; padding: 0; list-style: none; }
    .result {
      padding: .85rem 1rem;
      border-left: 4px solid var(--gold-dark);
      background: #211c17;
    }
    .result a { color: #f2d48d; font-weight: 700; }
    .result-meta { margin: .2rem 0 0; color: var(--muted); font-size: .9rem; }
    footer { margin-top: 2rem; color: var(--muted); font-size: .9rem; }
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">d20 SRD Hub</p>
    <h1>Private Rules Library</h1>
    <a href="https://d20srdhub.com/">Return to the public SRD</a>
  </header>
  <main>
    <section class="shelf">
      <h2>Your Bookshelf</h2>
      <p>This private area contains material you purchased for personal reference. It is available only through your protected account.</p>
      <article class="book">
        <h3>Spell Compendium</h3>
        <p>Personal reference copy · searchable index · PDF</p>
        <a class="button" href="/spell-compendium.pdf">Open PDF</a>
      </article>
      <article class="book">
        <h3>Spell Compendium v2</h3>
        <p>Second personal reference copy · searchable index · PDF</p>
        <a class="button" href="/spell-compendium-v2.pdf">Open PDF</a>
      </article>
      <section class="search" aria-labelledby="spell-search-heading">
        <h3 id="spell-search-heading">Search non-SRD spells</h3>
        <p>Results include only spells not already available in the public SRD. Open a result to jump to its page in your private PDF.</p>
        <label for="book-filter">Book</label>
        <select id="book-filter">
          <option value="">All private books</option>
          <option value="Spell Compendium">Spell Compendium</option>
          <option value="Spell Compendium v2">Spell Compendium v2</option>
        </select>
        <label for="spell-search">Spell name, school, class, or level</label>
        <input id="spell-search" type="search" autocomplete="off" placeholder="Try: shadow, cleric 3, transmutation">
        <p class="search-status" data-search-status>Loading your private spell index…</p>
        <ul class="results" data-search-results></ul>
      </section>
      <footer>Private personal library · Do not share this address or downloaded files.</footer>
    </section>
  </main>
  <script src="/library.js" defer></script>
</body>
</html>`;

const LIBRARY_JS = `
const input = document.querySelector("#spell-search");
const bookFilter = document.querySelector("#book-filter");
const status = document.querySelector("[data-search-status]");
const results = document.querySelector("[data-search-results]");
let spells = [];

function render() {
  const query = input.value.trim().toLocaleLowerCase();
  const selectedBook = bookFilter.value;
  const tokens = query.split(/\\s+/).filter(Boolean);
  const matches = spells.filter((spell) => {
    if (selectedBook && spell.book !== selectedBook) return false;
    if (!tokens.length) return false;
    const haystack = [spell.name, spell.school, spell.levels].join(" ").toLocaleLowerCase();
    return tokens.every((token) => haystack.includes(token));
  });

  results.replaceChildren();
  const visible = matches.slice(0, 100);
  for (const spell of visible) {
    const item = document.createElement("li");
    item.className = "result";
    const link = document.createElement("a");
    link.href = spell.pdf + "#page=" + spell.page;
    link.textContent = spell.name;
    const meta = document.createElement("p");
    meta.className = "result-meta";
    meta.textContent = [spell.book, spell.school, spell.levels, "PDF page " + spell.page]
      .filter(Boolean)
      .join(" · ");
    item.append(link, meta);
    results.append(item);
  }

  if (!tokens.length) {
    status.textContent = spells.length + " private, non-SRD spells indexed. Start typing to search.";
  } else if (!matches.length) {
    status.textContent = "No private spells matched your search.";
  } else {
    status.textContent = matches.length + " match" + (matches.length === 1 ? "" : "es") +
      (matches.length > visible.length ? "; showing the first " + visible.length : "") + ".";
  }
}

const libraries = [
  { api: "/api/spells", pdf: "/spell-compendium.pdf", name: "Spell Compendium" },
  { api: "/api/spells-v2", pdf: "/spell-compendium-v2.pdf", name: "Spell Compendium v2" },
];

Promise.all(libraries.map((library) =>
  fetch(library.api).then((response) => {
    if (!response.ok) throw new Error("Spell index unavailable");
    return response.json().then((payload) =>
      (Array.isArray(payload.spells) ? payload.spells : []).map((spell) => ({
        ...spell,
        book: library.name,
        pdf: library.pdf,
      }))
    );
  })
))
  .then((collections) => {
    spells = collections.flat();
    render();
    input.addEventListener("input", render);
    bookFilter.addEventListener("change", render);
  })
  .catch(() => {
    status.textContent = "The private spell index is not available yet.";
  });
`;

function securedResponse(body, init = {}) {
  const headers = new Headers(init.headers);
  for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
    headers.set(name, value);
  }
  return new Response(body, { ...init, headers });
}

function isAuthorized(request, env) {
  const email = request.headers
    .get("Cf-Access-Authenticated-User-Email")
    ?.trim()
    .toLowerCase();
  const assertion = request.headers.get("Cf-Access-Jwt-Assertion");
  return (
    Boolean(assertion) &&
    Boolean(env.ALLOWED_EMAIL) &&
    email === env.ALLOWED_EMAIL.trim().toLowerCase()
  );
}

export async function handleRequest(request, env) {
  if (!isAuthorized(request, env)) {
    return securedResponse("Forbidden", {
      status: 403,
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }

  const url = new URL(request.url);

  if (url.pathname === "/" && (request.method === "GET" || request.method === "HEAD")) {
    return securedResponse(request.method === "HEAD" ? null : LIBRARY_HTML, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  }

  if (
    url.pathname === "/library.js" &&
    (request.method === "GET" || request.method === "HEAD")
  ) {
    return securedResponse(request.method === "HEAD" ? null : LIBRARY_JS, {
      headers: { "Content-Type": "text/javascript; charset=utf-8" },
    });
  }

  if (
    url.pathname === "/api/spells" &&
    (request.method === "GET" || request.method === "HEAD")
  ) {
    const object = await env.PRIVATE_LIBRARY.get(SPELL_INDEX_KEY);
    if (!object) {
      return securedResponse('{"error":"Spell index not found"}', {
        status: 503,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      });
    }

    return securedResponse(request.method === "HEAD" ? null : object.body, {
      headers: {
        "Content-Length": String(object.size),
        "Content-Type": "application/json; charset=utf-8",
      },
    });
  }

  if (
    url.pathname === "/api/spells-v2" &&
    (request.method === "GET" || request.method === "HEAD")
  ) {
    const object = await env.PRIVATE_LIBRARY.get(SPELL_V2_INDEX_KEY);
    if (!object) {
      return securedResponse('{"error":"Spell Compendium v2 index not found"}', {
        status: 503,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      });
    }

    return securedResponse(request.method === "HEAD" ? null : object.body, {
      headers: {
        "Content-Length": String(object.size),
        "Content-Type": "application/json; charset=utf-8",
      },
    });
  }

  if (
    url.pathname === "/spell-compendium.pdf" &&
    (request.method === "GET" || request.method === "HEAD")
  ) {
    const object = await env.PRIVATE_LIBRARY.get(PDF_KEY);
    if (!object) {
      return securedResponse("Book not found", {
        status: 404,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    }

    return securedResponse(request.method === "HEAD" ? null : object.body, {
      headers: {
        "Content-Disposition": 'inline; filename="Spell-Compendium.pdf"',
        "Content-Length": String(object.size),
        "Content-Type": "application/pdf",
      },
    });
  }

  if (
    url.pathname === "/spell-compendium-v2.pdf" &&
    (request.method === "GET" || request.method === "HEAD")
  ) {
    const object = await env.PRIVATE_LIBRARY.get(PDF_V2_KEY);
    if (!object) {
      return securedResponse("Book not found", {
        status: 404,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    }

    return securedResponse(request.method === "HEAD" ? null : object.body, {
      headers: {
        "Content-Disposition": 'inline; filename="Spell-Compendium-v2.pdf"',
        "Content-Length": String(object.size),
        "Content-Type": "application/pdf",
      },
    });
  }

  return securedResponse("Not found", {
    status: 404,
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}

export default {
  fetch: handleRequest,
};
