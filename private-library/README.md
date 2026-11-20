# Private Spell Compendium library

This Cloudflare Worker keeps the purchased PDF and its search index behind
Cloudflare Access. The public SRD never receives the book text or index.

## Build the private non-SRD index

Run from the repository root on macOS:

```bash
python3 private-library/build_spell_index.py \
  "/Users/thomaspaddenmacbookair/Documents/D&D/3E Books/Spell_Compendium_FR.pdf"
```

The generator extracts spell headings with macOS PDFKit, removes titles already
present under `public/spells/`, and writes:

```text
private-library/generated/spell-compendium-index.json
```

The generated file is intentionally ignored by Git.

To build the second private volume:

```bash
python3 private-library/build_spell_index.py \
  "/Users/thomaspaddenmacbookair/Documents/D&D/3E Books/Spell Compendium copy.pdf" \
  --book-name "Spell Compendium v2" \
  --output private-library/generated/spell-compendium-v2-index.json
```

## Upload the private files

```bash
npx wrangler r2 object put \
  "d20srdhub-private-library/Spell Compendium.pdf" \
  --file="/Users/thomaspaddenmacbookair/Documents/D&D/3E Books/Spell_Compendium_FR.pdf"

npx wrangler r2 object put \
  "d20srdhub-private-library/spell-compendium-index.json" \
  --file="private-library/generated/spell-compendium-index.json"
```

Then deploy from `private-library/`:

```bash
npx wrangler deploy
```

Cloudflare Access must protect the library hostname. Configure the Worker secret
`ALLOWED_EMAIL` to match the owner's email.

## One-time Forgotten Realms Wiki import

The GM Secrets worker serves a self-hosted, text-only archive at
`/gm-secrets/forgotten-realms/`. The presentation follows the compact,
old-school map-and-content navigation of Maldin's Greyhawk without copying its
copyrighted artwork or page assets.

The reviewed source import used Fandom's October 21, 2026 current-pages dump:

```text
https://s3.amazonaws.com/wikia_xml_dumps/f/fo/forgottenrealms_pages_current.xml.7z
SHA-256 1b8e3fc7639e28315ecbe58bce7f184bbe57c66390899110fc4cab3d823535b8
```

The XML was converted with revision `669feb9f0c15ee53a3a3ae2f090a00d56371d862`
of `ObsidianTTRPGProject/Obsidian-TTRPG-Atlas`'s MIT-licensed
`Forgotten Realms Wiki/fr_to_obsidian.py` (script SHA-256
`327b4365c9ad80018dfa57a761c8dc9854069c613c524201f1b2248797b33c1f`).
Then build the R2 payload:

```bash
python3 private-library/build_forgotten_realms_archive.py \
  /path/to/FR-Vault \
  private-library/generated-forgotten-realms
```

The build creates 70,973 article objects, search shards, a manifest, and a
checksum. It rewrites wiki links to local GM Secrets paths and records the
source URL and CC BY-SA 3.0 license on every article. It never imports images;
Fandom's XML dump has none, and individual wiki files use varying rights terms.

After the pull request is approved, upload the generated payload once and then
deploy the worker:

```bash
python3 private-library/upload_forgotten_realms_archive.py \
  private-library/generated-forgotten-realms

cd private-library
npx wrangler deploy
```

The generated archive is intentionally gitignored: the repository contains the
reviewable import, serving, attribution, and test code, while the existing
private R2 bucket holds the 384 MB generated corpus.
