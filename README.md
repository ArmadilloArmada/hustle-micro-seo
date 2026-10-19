# hustle-micro-seo

Micro-SEO **content pack** CLI for one local service business. Feed NAP + review blurbs in YAML; get a blog draft, Google Business Profile post drafts, and FAQ JSON-LD for **human edit and manual publish**.

Part of Project Hustle Tier 0 §5 — barter → paid local SEO help without auto-posting.

## What it produces

| File | Purpose |
|------|---------|
| `out/blog-draft.md` | Local blog article + meta fields + editor checklist |
| `out/gbp-posts.md` | Four GBP post drafts (paste manually) |
| `out/faq-schema.json` | FAQPage JSON-LD (verify before embedding) |

**No auto-publish** to WordPress, Google Business Profile, or anywhere else.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp config.example.yaml config.yaml
# edit NAP / services / reviews for your client

python -m src --config config.yaml --out out
```

Dry-run with the bundled demo plumber config:

```bash
cp config.example.yaml config.yaml
python -m src --template-only
```

Optional LLM rewrite (still requires human edit):

```bash
export OPENAI_API_KEY=sk-...
# optional: export OPENAI_MODEL=gpt-4o-mini
python -m src
```

Without `OPENAI_API_KEY`, the CLI writes **full template drafts** (not empty stubs) from the config facts.

## Config

`config.example.yaml` includes a **fictional** Austin plumber (Clearflow Plumbing Co.) with NAP, services, and sample review blurbs. Replace with real client intake before any live use. Never invent licenses, awards, or testimonials.

## Compliance / quality caution

- **Google spam policies:** Thin, scaled, or unedited AI pages can hurt the site and the GBP. Publish only after a human edit with real experience signals (photos, specifics, accurate NAP).
- **E-E-A-T:** Experience, Expertise, Authoritativeness, Trust — AI drafts are a starting point. Add original photos, verified credentials, and client-approved quotes.
- **Reviews:** Only use testimonials the business is allowed to republish. Do not fabricate ratings.
- **No review gating / keyword stuffing** in GBP posts.

## Layout

```
config.example.yaml
requirements.txt
pyproject.toml
src/
  cli.py
  config.py
  generate.py
  llm.py
  templates.py
out/
  .gitkeep
```

## License

MIT — see `LICENSE`.
