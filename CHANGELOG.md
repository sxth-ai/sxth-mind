# Changelog

All notable changes to sxth-mind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Reference adapters are now packaged** and importable as
  `from sxth_mind.adapters import SalesAdapter, HabitCoachAdapter, LearningAdapter`.
  Previously they lived only under `examples/`, which is not shipped in the
  wheel, so the documented quickstart and the `sxth-mind demo`/`serve` CLI
  failed with `ModuleNotFoundError` after `pip install`. Importing from
  `examples.*` still works in a source checkout via a compatibility shim.
- **Time-based nudges now fire.** `days_since_activity` is derived from
  `last_interaction` (via `ProjectMind.refresh_inactivity()`) instead of only
  ever being reset to 0, so inactivity/comeback/streak nudges actually trigger.
- **Momentum now decays with inactivity** (`apply_momentum_decay()`) rather than
  only ever increasing.
- **`trust_score` now evolves** with each interaction (diminishing growth toward
  1.0) on both `UserMind` and `ProjectMind`.
- **Nudge dismiss/act endpoints are real.** `POST /nudges/{id}/dismiss` and
  `/act` update stored status (404 when the nudge doesn't exist) instead of
  returning a no-op success. Added `BaseStorage.update_nudge_status()` and
  `Mind.check_nudges()/dismiss_nudge()/act_on_nudge()`.
- **HTTP API no longer uses a module-level singleton.** The `Mind` is bound to
  `app.state` and injected via a FastAPI dependency, so multiple apps can run in
  one process and tests stay isolated.
- **`MemoryStorage` stores isolated snapshots** (deep copies) so mutating an
  object after saving no longer changes persisted state, matching
  `SQLiteStorage` semantics.
- Timestamps are timezone-aware UTC (no more deprecated `datetime.utcnow()`).
- `mypy --strict` now passes (the project configured it but had 70+ errors).
- Python 3.10 is now a real, declared-and-tested floor (classifier added,
  tooling targets `py310`).

## [0.1.0] - 2026-01-18

### Added

- **Core Mind abstraction** - Central interface for cognitive state management
  - `chat()` and `chat_stream()` for conversations
  - `get_state()` and `explain_state()` for introspection
  - `get_pending_nudges()` for proactive suggestions

- **Schema definitions**
  - `UserMind` - User-level identity, patterns, and preferences
  - `ProjectMind` - Project-specific context and journey progress
  - `ConversationMemory` - Sliding window message history
  - `Nudge` - Proactive suggestion model
  - `Insight` - Structured observation model

- **Adapter system**
  - `BaseAdapter` abstract class for domain-specific behavior
  - Identity types, journey stages, nudge templates
  - Custom system prompts and state updates

- **Example adapters**
  - `SalesAdapter` - B2B sales pipeline tracking
  - `HabitCoachAdapter` - Habit building with streaks
  - `LearningAdapter` - Skill development tracking

- **LLM providers**
  - `BaseLLMProvider` interface
  - `OpenAIProvider` implementation

- **Storage backends**
  - `BaseStorage` interface
  - `MemoryStorage` - In-memory (default)
  - `SQLiteStorage` - Persistent SQLite

- **Nudge engine**
  - `BaselineNudgeEngine` - Rule-based nudge generation
  - Inactivity, momentum drop, and pattern-based triggers

- **HTTP API** (FastAPI)
  - `/chat` and `/chat/stream` endpoints
  - `/state/{user_id}` and `/explain/{user_id}`
  - `/nudges/{user_id}` endpoints

- **CLI**
  - `sxth-mind demo` - Interactive demo
  - `sxth-mind serve` - HTTP server
  - `sxth-mind info` - Package info

- **Documentation**
  - README with architecture overview
  - Getting started guide
  - Adapter development guide

[Unreleased]: https://github.com/sxth-ai/sxth-mind/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sxth-ai/sxth-mind/releases/tag/v0.1.0
