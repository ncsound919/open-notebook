"""The oncology briefing templates are the contract the pipeline pastes as the
episode briefing; explain_briefing.jinja must render with its documented data
keys and carry the plain-language rules the lane exists for."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

PROMPTS = Path(__file__).resolve().parent.parent / "prompts" / "oncology"


def _render(template: str, **data: object) -> str:
    env = Environment(
        loader=FileSystemLoader(PROMPTS),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template(template).render(**data)


EXPLAIN_DATA = {
    "title": "Organ tropism validation",
    "audience": "smart non-specialist",
    "why_it_matters": "Where a tumour spreads decides which drug can reach it.",
    "question": "Can we predict the destination site from the primary tumour's profile?",
    "what_we_did": "Trained a multiclass model on 5,000 samples across 12 sites.",
    "findings": "- macro-AUC 0.71 across 12 destination sites\n- liver control recovered = true",
    "meaning": "A positive control recovered, so the signal is not an artifact.",
    "unknown": "Out-of-cohort sites remain untested.",
    "next_step": "External validation on a second cohort.",
    "source_note": "",
}


def test_explain_briefing_renders_all_fields():
    text = _render("explain_briefing.jinja", **EXPLAIN_DATA)
    assert "Organ tropism validation" in text
    assert "macro-AUC 0.71" in text
    assert "Out-of-cohort sites remain untested" in text
    # No unresolved jinja left behind.
    assert "{{" not in text


def test_explain_briefing_is_informational_not_debate():
    text = _render("explain_briefing.jinja", **EXPLAIN_DATA)
    lowered = text.lower()
    assert "informational episode, not a debate" in lowered
    assert "plain words first" in lowered
    assert "translated into meaning" in lowered


def test_explain_briefing_carries_optional_source_note():
    text = _render(
        "explain_briefing.jinja",
        **{**EXPLAIN_DATA, "source_note": "Envelope sha256 abc"},
    )
    assert "Envelope sha256 abc" in text


def test_migration_28_is_registered():
    """AGENTS.md: a new migration needs the files AND the hard-coded
    AsyncMigrationManager edit. Importing the manager pulls in the SurrealDB
    client, so verify both sides statically — this catches the file-without-
    -registration case with no DB stack required."""
    root = Path(__file__).resolve().parent.parent
    manager = (root / "open_notebook" / "database" / "async_migrate.py").read_text(
        encoding="utf-8"
    )
    for f in ("28.surrealql", "28_down.surrealql"):
        assert (root / "open_notebook" / "database" / "migrations" / f).exists()
        assert f"migrations/{f}" in manager, (
            f"migration {f} exists but is not registered"
        )

    up = manager.split("self.up_migrations = [")[1].split("]")[0]
    down = manager.split("self.down_migrations = [")[1].split("]")[0]
    assert "28.surrealql" in up and "28_down.surrealql" in down
    # Up and down lists stay the same length.
    assert up.count(".surrealql") == down.count(".surrealql")
