# OpenRouter Free / 限免 (Limited-Free) Model Detection

Condensed recipe for monitoring OpenRouter for newly-launched **limited-time free** models
(the "限免" class — e.g. `tencent/hy3:free`, which ran free 2026-07-06 → 2026-07-21).

## Endpoint
`GET https://openrouter.ai/api/v1/models` -> `{ "data": [ <model>, ... ] }`
No auth required. ~520 KB, ~343 models as of 2026-07-15.

## Model object key fields
- `id` (e.g. `tencent/hy3:free`)
- `name`
- `context_length` (int, tokens)
- `pricing`: `{ prompt, completion, input_cache_read }` — **strings**, per-token USD.
- `expiration_date`: **ISO date STRING** (`"2026-07-21"`), NOT a millisecond timestamp.
  Can also be an ISO datetime or a numeric timestamp in other contexts — parse defensively.
- `architecture.modality`: `text->text`, `text+image->text` (vision), `text->image`, etc.
- `description`, `knowledge_cutoff`, `created` (unix seconds).

## Detection logic (verified against live API 2026-07-15)
1. **Free**: `pricing.prompt == "0"` AND `pricing.completion == "0"`.
   -> 23 of 343 models were free.
2. **Limited-free (限免)**: free AND `expiration_date` present AND parsed date > now.
   -> 7 of 23 at that time (hy3 + a batch expiring 2026-07-19).
3. **Permanent free pool**: free but `expiration_date is None` (gemma, nemotron, poolside…).
   -> Exclude these from "new launch" alerts (they are not limited-time).

Pitfall: `expiration_date` is a date string, not the millisecond timestamp the OpenRouter
docs sometimes imply. A naive `int(ms)/1000` parse yields `None` and silently drops every
limited-free model. Parse ISO strings too.

## De-dup state
Keep a local JSON of already-seen limited-free `id`s so the monitor only notifies on NEW
entries. On each run, rewrite the seen-set to the current limited-free set (expired models
drop out naturally).

## Building a comparison report
Anchor the user's main model as a fixed spec dict (context, params, $/M token, modality)
since the comparison baseline shouldn't be re-fetched live. Derive the alert body purely
from API fields (context length, modality, description, cutoff, free-until) — never invent
merits. A watchdog-style script: print the alert ONLY when new models exist; empty stdout
= silent (correct for `--no-agent` cron delivery).
