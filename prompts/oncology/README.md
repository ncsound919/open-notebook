# Oncology briefing templates

Render with experiment data and paste the result as the episode **briefing**
when using the `oncology_experiment_log`, `oncology_paper`, `oncology_debate`,
or `oncology_explain` episode profiles (seeded by migration 26 and 28).

- `experiment_log.jinja` — data: `experiment_id, date, hypothesis, methods,
  results, artifacts` — produces a structured lab-log briefing.
- `paper_draft.jinja` — data: `title, authors, abstract_notes, methods,
  results, discussion_points` — produces a paper-generation briefing
  (Abstract / Intro / Methods / Results / Discussion).
- `debate_briefing.jinja` — data: `motion, side_a, side_b, evidence` —
  produces a discourse-debate briefing (claim / counterclaim / evidence /
  verdict), voiced by the `oncology_lab` speaker pair.
- `explain_briefing.jinja` — data: `title, audience, why_it_matters,
  question, what_we_did, findings, meaning, unknown, next_step,
  source_note` — produces a plain-language informational briefing for the
  `oncology_explain` profile (migration 28, `onc_explain_pair` cast). Use this
  lane when there is no debate material (e.g. the Discourse Tool's model
  backend is unavailable): the episode explains the research to a smart
  non-specialist instead of staging a debate with nothing to debate.

Logging loop: experiment output (Oncology Ecosystem `platform/reports/`,
`lens-readouts/`) -> notebook source -> episode with the matching profile ->
paper draft or debate episode. Every generated document keeps the source
manifest so the paper trail stays legit.

Lane choice: real debate session from the Discourse Tool -> `oncology_debate`;
everything else -> `oncology_explain`. Never voice an empty debate — the
informational lane always has the actual findings to explain.
