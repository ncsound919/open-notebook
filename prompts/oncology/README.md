# Oncology briefing templates

Render with experiment data and paste the result as the episode **briefing**
when using the `oncology_experiment_log`, `oncology_paper`, or
`oncology_debate` episode profiles (seeded by migration 14).

- `experiment_log.jinja` — data: `experiment_id, date, hypothesis, methods,
  results, artifacts` — produces a structured lab-log briefing.
- `paper_draft.jinja` — data: `title, authors, abstract_notes, methods,
  results, discussion_points` — produces a paper-generation briefing
  (Abstract / Intro / Methods / Results / Discussion).
- `debate_briefing.jinja` — data: `motion, side_a, side_b, evidence` —
  produces a discourse-debate briefing (claim / counterclaim / evidence /
  verdict), voiced by the `oncology_lab` speaker pair.

Logging loop: experiment output (Oncology Ecosystem `platform/reports/`,
`lens-readouts/`) -> notebook source -> episode with the matching profile ->
paper draft or debate episode. Every generated document keeps the source
manifest so the paper trail stays legit.
