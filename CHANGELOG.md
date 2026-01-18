# Changelog

All notable changes to sxth-mind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
