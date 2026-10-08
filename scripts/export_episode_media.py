#!/usr/bin/env python3
"""Publish a finished open-notebook episode into the oncology ecosystem.

Copies the episode audio + transcript + briefing into
<ecosystem>/media/notebook/<episode>/ and appends a manifest line so the
ecosystem's output (papers/, lens-readouts/, reports/) can cite the media.

Usage:
    python scripts/export_episode_media.py <episode-dir> [--ecosystem-root PATH]

<episode-dir> is the per-episode folder under notebook_data/podcasts/episodes/
(audio .mp3, transcript.json, outline.json, briefing saved alongside or passed
via --briefing). Stdlib only.

Manifest line (media/notebook/manifest.jsonl):
  {"episode": ..., "exported_at": ..., "audio": ..., "transcript": ..., "briefing": ...}
"""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ECO = Path(
    r"C:\Users\User\Downloads\BUSINESS\SCIENCE\Oncology Ecosystem"
)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    ep = Path(args[0])
    if not ep.is_dir():
        raise SystemExit(f"not a directory: {ep}")
    eco = Path(args[args.index("--ecosystem-root") + 1]) if "--ecosystem-root" in args else DEFAULT_ECO

    dest = eco / "media" / "notebook" / ep.name
    dest.mkdir(parents=True, exist_ok=True)
    copied = {}
    for pattern, key in (("*.mp3", "audio"), ("*.json", "transcript"),
                         ("*.md", "briefing")):
        for f in sorted(ep.glob(pattern)):
            shutil.copy2(f, dest / f.name)
            copied.setdefault(key, []).append(f.name)

    manifest = eco / "media" / "notebook" / "manifest.jsonl"
    with open(manifest, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "episode": ep.name,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            **copied,
        }) + "\n")
    print(f"published {ep.name} -> {dest}")
    print(f"manifest: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
