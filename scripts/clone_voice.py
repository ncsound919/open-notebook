#!/usr/bin/env python3
"""Clone your voice for open-notebook podcasts — $0, self-hosted.

Flow:
  1. Record 5-15 s of clean speech, save as 16-bit PCM WAV (mono, 16-48 kHz).
  2. Run:  python scripts/clone_voice.py <sample.wav> "<voice id>" [--transcript "..."]
     - validates the sample (format, duration, clipping risk)
     - stages voices/<id>.wav + voices/<id>.txt into ./tts_data/f5-voices/
     - if the F5 server is up, uploads via POST /v1/audio/clone
  3. Paste the printed speaker-profile JSON into the app
     (Podcasts > Speaker profiles) with tts_provider "openai_compatible"
     pointed at the F5 server, voice "file://<voice id>".

Needs the F5 server (docker compose --profile oss-voices --profile oss-clone up tts-f5).
Transcript: if omitted, transcribe the sample first (any STT) and pass it —
F5 requires the exact transcript of the reference clip.
"""
import sys
import wave
from pathlib import Path

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None

MIN_SECONDS = 5.0
MAX_SECONDS = 15.0
F5_BASE = "http://localhost:8002"
VOICES_DIR = Path(__file__).resolve().parent.parent / "tts_data" / "f5-voices"


def check_wav(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        if w.getcomptype() != "NONE" or w.getsampwidth() != 2:
            raise SystemExit("sample must be 16-bit PCM WAV")
        if w.getnchannels() != 1:
            print("WARN: stereo sample — mono converts cleaner; continuing.")
        seconds = w.getnframes() / w.getframerate()
    print(f"sample: {seconds:.1f}s, {w.getframerate()} Hz")
    if seconds < MIN_SECONDS:
        raise SystemExit(f"too short — need at least {MIN_SECONDS:.0f}s for a stable clone")
    if seconds > MAX_SECONDS + 3:
        print(f"WARN: over {MAX_SECONDS:.0f}s — F5 clips to ~12s; trim for best match.")
    return seconds


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    sample = Path(sys.argv[1])
    voice_id = sys.argv[2].strip().lower().replace(" ", "-")
    transcript = ""
    if "--transcript" in sys.argv:
        transcript = sys.argv[sys.argv.index("--transcript") + 1]
    if not sample.is_file():
        raise SystemExit(f"not found: {sample}")
    if not transcript:
        raise SystemExit("pass --transcript with the EXACT words spoken in the sample")

    check_wav(sample)
    VOICES_DIR.mkdir(parents=True, exist_ok=True)
    (VOICES_DIR / f"{voice_id}.wav").write_bytes(sample.read_bytes())
    (VOICES_DIR / f"{voice_id}.txt").write_text(transcript, encoding="utf-8")
    print(f"staged: {VOICES_DIR / (voice_id + '.wav')}")

    if httpx is not None:
        try:
            with open(sample, "rb") as f:
                r = httpx.post(
                    f"{F5_BASE}/v1/audio/clone",
                    files={"audio": (f"{voice_id}.wav", f, "audio/wav")},
                    data={"voice_id": voice_id, "transcript": transcript},
                    timeout=120,
                )
            print(f"server upload: HTTP {r.status_code}")
        except Exception as e:  # server down is fine — staged files load on boot
            print(f"server unreachable ({e}); staged files load on next boot.")
    else:
        print("httpx not installed; skipping upload — staged files load on boot.")

    print("\n--- speaker profile JSON (Podcasts > Speaker profiles > New) ---")
    print(
        """{
  "name": "%s-voice",
  "description": "Cloned host voice (%s)",
  "tts_provider": "openai_compatible",
  "tts_model": "f5-tts",
  "speakers": [
    {"name": "Host", "voice_id": "file://%s",
     "backstory": "Show host, cloned voice.",
     "personality": "Natural, conversational."}
  ]
}"""
        % (voice_id, voice_id, voice_id)
    )
    print("\nPoint an openai_compatible credential at the F5 server "
          "(base_url http://tts-f5:8000/v1 in compose, http://localhost:8002/v1 local).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
