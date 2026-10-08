#!/usr/bin/env python3
"""Preview the two debate voices side by side (Kokoro OSS lane).

Renders the same line with both oss_kokoro_cast voices so you can hear
that the debaters are distinguishable before generating a full episode.

Usage:
    python scripts/preview_voices.py [--base-url http://localhost:8001/v1]
        [--voice-a af_heart] [--voice-b am_adam]

Needs: httpx (pip install httpx) + a running Kokoro server
  (docker compose --profile oss-voices up tts-kokoro).
Writes preview-voice-a.mp3 / preview-voice-b.mp3 next to the script.
"""
import sys

try:
    import httpx
except ImportError:
    raise SystemExit("pip install httpx")

LINE = (
    "The tumor board is now in session. I disagree with the proposed "
    "surrogate endpoint, and here is exactly why the numbers do not hold up."
)

args = sys.argv[1:]
base = "http://localhost:8001/v1"
voice_a, voice_b = "af_heart", "am_adam"
if "--base-url" in args:
    base = args[args.index("--base-url") + 1]
if "--voice-a" in args:
    voice_a = args[args.index("--voice-a") + 1]
if "--voice-b" in args:
    voice_b = args[args.index("--voice-b") + 1]

for tag, voice in (("a", voice_a), ("b", voice_b)):
    r = httpx.post(
        f"{base}/audio/speech",
        json={"model": "kokoro", "input": LINE, "voice": voice,
              "response_format": "mp3"},
        timeout=120,
    )
    r.raise_for_status()
    out = f"preview-voice-{tag}-{voice}.mp3"
    with open(out, "wb") as f:
        f.write(r.content)
    print(f"{voice} -> {out} ({len(r.content)} bytes)")
print("Play both files: the debaters should be unmistakably different.")
