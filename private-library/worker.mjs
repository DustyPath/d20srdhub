const PDF_KEY = "Spell Compendium.pdf";

const SECURITY_HEADERS = {
  "Cache-Control": "private, no-store",
  "Content-Security-Policy":
    "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'; frame-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
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
        <p>Personal reference copy · PDF</p>
        <a class="button" href="/spell-compendium.pdf">Open PDF</a>
      </article>
      <footer>Private personal library · Do not share this address or downloaded files.</footer>
    </section>
  </main>
</body>
</html>`;

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

  return securedResponse("Not found", {
    status: 404,
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}

export default {
  fetch: handleRequest,
};
