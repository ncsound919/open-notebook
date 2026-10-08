#!/usr/bin/env python3
"""Import a Discourse Tool debate session into an open-notebook podcast briefing.

Reads a session JSON exported from the Discourse Tool
(TranscriptReportModal > Export JSON, i.e. generateTranscriptJSON shape,
or a record from the tool's data/debates.json) and writes two files next
to it:

  <basename>.briefing.md  -> paste as the episode briefing when using the
                             oncology_debate episode profile
  <basename>.context.md   -> paste as the episode content/context

Usage:
    python scripts/import_discourse_session.py <session.json>

Stdlib only, so it runs anywhere.
"""
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1])
    session = json.loads(src.read_text(encoding="utf-8"))

    meta = session.get("metadata", {}) or {}
    topic = meta.get("topic") or session.get("topic", "Oncology Scientific Debate")
    agents = session.get("agents", []) or []
    rounds = session.get("transcriptRounds", []) or session.get("rounds", []) or []
    brief = session.get("researchBrief", {}) or {}
    judge = session.get("judgeResult", {}) or {}
    summary = session.get("executiveSummaryAndTakeaways", {}) or {}

    sides = []
    for a in agents:
        sides.append(
            f"- {a.get('name', '?')} ({a.get('role', '?')}): {a.get('stanceBrief', '')}"
        )
    side_block = "\n".join(sides) if sides else "No debater roster in export."

    evidence_lines = []
    for r in rounds:
        for s in r.get("statements", []) or []:
            claim = (s.get("evaluatedClaim") or {})
            if claim.get("claim"):
                evidence_lines.append(
                    f"- [{s.get('agentName', '?')}] {claim.get('claim')} "
                    f"(Tier {claim.get('evidenceTier', '?')}; "
                    f"falsifier: {claim.get('falsifier', 'n/a')})"
                )
    evidence_block = (
        "\n".join(evidence_lines)
        if evidence_lines
        else "No claim cards in export; use research brief below."
    )
    brief_block = "\n".join(
        f"{k}: {v}" for k, v in brief.items() if v
    ) or "No research brief in export."

    briefing = f"""DISCOURSE DEBATE — {topic}

Source: Oncology Discourse Tool session {meta.get('id', '?')} | """
    briefing += f"""format {meta.get('format', '?')} | consensus {judge.get('consensusScore', '?')}/100

Debaters (affirming vs challenging assigned by stance at briefing time):
{side_block}

Shared evidence both sides must use (claim cards from the arena):
{evidence_block}

Research brief:
{brief_block}

Instructions: stage a legit scientific debate. Each side states its claim,
the other side cross-examines with a counterclaim grounded ONLY in the
shared evidence, then each side concedes exactly one valid point from the
opponent before the closing verdict. No strawmen, no invented data — if a
side lacks evidence for a point, it must say so on the record. End with a
referee-style verdict: what is established, what is contested, and what
experiment would settle it.
"""

    context_parts = [
        f"# {topic}",
        "",
        summary.get("executiveSummary", ""),
        "",
        "## Consensus agreements",
        *[f"- {c}" for c in summary.get("consensusAgreements", [])],
        "",
        "## Remaining cruxes",
        *[f"- {c}" for c in summary.get("remainingCruxes", [])],
        "",
        "## Preregistered next steps",
        *[f"- {c}" for c in summary.get("preregisteredNextSteps", [])],
        "",
    ]
    if judge.get("dissent"):
        context_parts += ["## Dissent", judge["dissent"], ""]

    out_brief = src.with_suffix("").as_posix() + ".briefing.md"
    out_ctx = src.with_suffix("").as_posix() + ".context.md"
    Path(out_brief).write_text(briefing, encoding="utf-8")
    Path(out_ctx).write_text("\n".join(context_parts), encoding="utf-8")
    print(f"briefing -> {out_brief}")
    print(f"context   -> {out_ctx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
