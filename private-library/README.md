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
