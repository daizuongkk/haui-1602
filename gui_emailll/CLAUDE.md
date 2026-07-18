# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An AI weather-hazard forecasting and multilingual alert system for **Điện Biên province, Vietnam**. It fetches weather forecasts, applies terrain-corrected rules to detect natural-disaster hazards, translates the alerts into Vietnamese, Thái (Điện Biên dialect) and H'Mông, renders them to audio, and serves everything to a React frontend (resident view + official dashboard) through a FastAPI backend. Most code comments, console output, and docs are in Vietnamese.

The pieces communicate **through JSON files on disk** — `active_alerts.json` (pipeline output) → `translation_agent/output/alert.json` (bulletins) + audio, which the API merges by the key `(location name, date)`.

## Architecture — Clean Architecture layers

The Python code is layered; dependencies point inward
(`presentation → application → domain`, with `infrastructure` implementing the ports the application depends on):

| Layer | Package | Responsibility |
|---|---|---|
| Config | `backend/config/` | Centralized settings: `THRESHOLDS`, file paths, model ids, constants. **Tune hazard sensitivity here, never in rule logic.** |
| Shared | `backend/shared/` | Cross-cutting vocabulary — `alert_levels` (priority, labels, emoji). |
| Domain | `backend/domain/` | Pure business logic, no I/O: `downscaling`, `hazard_rules`, `aggregation`, `models`. |
| Infrastructure | `backend/infrastructure/` | I/O adapters + `ports` (Protocols): `openmeteo`, `gemini_client`, `gtts_speech`, `json_store`, `audio_catalog`, `logging_config`. |
| Application | `backend/application/` | Use cases wiring domain + infra via ports: `forecast_pipeline`, `translation_service`, `tts_pipeline`, `alert_merging`, `broadcasting`, `validation`, `prompts`, `benchmark_data`. |
| Presentation | `backend/presentation/` | Entry points: `cli`, `benchmark`, `translation_cli`, `tts_cli`, and `api/` (FastAPI `app`/`routes`/`schemas`). |
| Tests | `backend/tests/` | Domain + use-case tests, runnable without network (fake providers). |

All intra-project imports are absolute under the `backend` package (e.g. `from backend.domain.hazard_rules import evaluate_hazards`). **Compatibility shims** keep the old entry points working: root `main.py`, `benchmark.py`, and `backend/main.py` are one-liners delegating into `backend/presentation/`.

## Commands

Run everything **from the repo root** so the `backend` package resolves.

```bash
# Pipeline: fetch → terrain-correct → evaluate → write data/active_alerts.json
python -m backend.presentation.cli            # (or: python main.py)

# Rule-engine skill benchmark (POD / FAR / CSI over 10 labelled scenarios, no network)
python -m backend.presentation.benchmark      # (or: python benchmark.py)

# Translation agent + TTS (needs GEMINI_API_KEY in ./.env)
python -m backend.presentation.translation_cli
python -m backend.presentation.tts_cli

# Backend API
pip install -r backend/requirements.txt
uvicorn backend.presentation.api.app:app --reload   # http://localhost:8000

# Tests
python -m pytest backend/tests

# Frontend
cd frontend && npm install && npm run dev       # http://localhost:5173 (proxies /api, /audio → :8000)
```

**Environment:** the translation step requires `GEMINI_API_KEY` in a `.env` at the repo root (gitignored). `gtts` is needed for TTS; `fastapi`/`uvicorn` for the API; `pytest` for tests — all in `backend/requirements.txt`.

## Non-obvious domain logic (in `domain/`)

- **Terrain downscaling** (`downscaling.py`) is the key physics step: Open-Meteo returns temperatures at its coarse grid elevation; `downscale_temperature` corrects them to each location's true elevation via the lapse rate (`config.LAPSE_RATE`, 0.0065 °C/m). Every temperature-based hazard decision uses the corrected value.
- **Hazard rules** (`hazard_rules.py`) rank 7 categories on Red > Orange > Yellow (Green = none). Notable:
  - Landslide risk is a **composite score** `(rain_24h·0.5 + deep_soil_moisture·150 + water_balance·0.3) · risk_factor`, gated by minimum rainfall; weights live in `config.LANDSLIDE_SCORE_WEIGHTS`, `water_balance = rain − evapotranspiration`.
  - Cold/frost and "rét đậm rét hại" are evaluated **independently** (separate `if`s) so one night can trigger both.
  - Hail requires simultaneous high CAPE + low freezing level + rain intensity.
  - `evaluate_hazards` returns `HazardAlert` NamedTuples — positional access (`alert[0]`) and attribute access (`alert.hazard`) both work.
- **Daily aggregation** (`aggregation.py`) condenses 24 hourly readings per day; neutral defaults (`config.DAILY_SUMMARY_DEFAULTS`) fill a metric only when its entire source series is missing.

## Data contracts (keep stable — the frontend and cross-stage joins depend on them)

All runtime data lives under `data/` (paths centralized in `backend/config/settings.py`):
- `data/locations.json` — 3 districts (Mường Nhé, Mường Chà, Tuần Giáo): `lat`/`lon`, `real_elevation` (feeds downscaling), `landslide_risk_factor`.
- `data/active_alerts.json` — only days with ≥1 alert; each has `weather_summary` + `alerts[]`.
- `data/output/alert.json` — `{location, date, highest_alert_level, messages{vi,thai,hmong}}`.
- Audio: `data/output/audio/<Location_with_underscores>/<DDMMYYYY>/<lang>.mp3` (convention centralized in `backend/infrastructure/audio_catalog.py`; served at `/audio/...`).
- The merge (`backend/application/alert_merging.py`) joins on `(location name, date)` and degrades gracefully when a day lacks a translation (`has_translation=False`, empty `messages`).

## Conventions

- Alert-level strings `"Red"/"Orange"/"Yellow"/"Green"` and their ordering come from `backend/shared/alert_levels.py` — the single source of truth. Don't redefine them.
- All JSON writes use `encoding="utf-8"` + `ensure_ascii=False` (centralized in `backend/infrastructure/json_store.py`) so Vietnamese survives.
- The translation `SYSTEM_PROMPT` (`backend/application/prompts.py`) enforces anti-hallucination rules: the model may not alter numbers, change levels, or add phenomena. Preserve these when editing (spec: `docs/luatdich.md`).
- The frontend `src/` mirrors the layering: `domain/` (levels, icons), `services/` (api), `components/`, `views/`.
