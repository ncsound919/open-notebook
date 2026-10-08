# OSS voice lane — human podcasts for $0

Two self-hosted lanes, both OpenAI-compatible so they plug into the
existing `openai_compatible` TTS provider (no core code changes):

| Lane | Server | Needs | Voices | Clone |
|---|---|---|---|---|
| Presets | `tts-kokoro` (Kokoro-82M, CPU) | nothing | 50+ presets (`af_heart`, `am_adam`…) | no |
| Clone | `tts-f5` (F5-TTS, NVIDIA GPU ~3GB) | your 5–15s sample + transcript | `file://<your-id>` | zero-shot |

## Start the servers

```bash
docker compose --profile oss-voices up tts-kokoro            # presets, CPU
docker compose --profile oss-voices --profile oss-clone up   # + cloning, GPU
```

Health: `curl localhost:8001/health` (kokoro), `curl localhost:8002/healthz` (f5).

## Clone your voice

```bash
python scripts/clone_voice.py my-sample.wav "show-host" --transcript "exact words spoken"
```

Stages `tts_data/f5-voices/<id>.wav + .txt`, uploads to the server if up,
prints speaker-profile JSON. Then Podcasts > Speaker profiles > New, paste
it. Credential: `openai_compatible`, base_url `http://tts-f5:8000/v1`
(in compose) or `http://localhost:8002/v1` (local).

## Speaker mapping

- `tts_provider: "openai_compatible"`, `tts_model`: `kokoro` or `f5-tts`
- `voice_id`: kokoro preset name (`af_heart`) or `file://<voice-id>` for F5
- Seeded profiles (migration 27): `oss_kokoro_cast`, `oss_clone_host`,
  episode `oncology_oss_debate` (same debate format as `oncology_debate`,
  voiced by OSS).

## Notes

- F5 is clone-only: bare voice names return 422 — always `file://`.
- Reference clip quality sets output quality: quiet room, no music,
  transcript must match the audio exactly.
- Human-speech writing still comes from `prompts/podcast/transcript.jinja`
  (HUMAN VOICE DIRECTION) — voices render what the transcript gives them.
