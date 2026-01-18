# Contributing to sxth-mind

Thanks for your interest in contributing to sxth-mind!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sxth-mind.git
   cd sxth-mind
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev,openai,api,sqlite]"
   ```
4. Run tests to make sure everything works:
   ```bash
   pytest
   ```

## Development Setup

### Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
ruff check .        # Lint
ruff check . --fix  # Auto-fix issues
```

### Type Checking

We use strict mypy:

```bash
mypy sxth_mind
```

### Running Tests

```bash
pytest                    # All tests
pytest tests/test_mind.py # Specific file
pytest -v                 # Verbose output
```

## What to Contribute

### High-Value Contributions

- **New adapters**: Domain-specific implementations (e.g., customer support, fitness coaching)
- **Storage backends**: Redis, PostgreSQL, MongoDB, etc.
- **LLM providers**: Anthropic, Gemini, local models, etc.
- **Bug fixes**: With tests demonstrating the fix

### Documentation

- Improve existing docs
- Add examples
- Fix typos

### Ideas & Feedback

- Open an issue to discuss new features
- Share how you're using sxth-mind

## Pull Request Process

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/my-new-adapter
   ```

2. **Make your changes** with clear, focused commits

3. **Add tests** for new functionality

4. **Run the full test suite**:
   ```bash
   pytest
   ruff check .
   mypy sxth_mind
   ```

5. **Open a PR** with:
   - Clear description of what changed
   - Link to any related issues
   - Screenshots/examples if applicable

## Adding an Adapter

Adapters live in `examples/`. Here's the structure:

```
examples/
  your_domain/
    __init__.py    # Your adapter class
    README.md      # Usage docs
```

See [docs/adapters.md](docs/adapters.md) for detailed guidance.

Minimum requirements:
- Implement all abstract methods from `BaseAdapter`
- Add tests in `tests/test_your_adapter.py`
- Include a README with usage examples

## Adding a Storage Backend

Storage backends live in `sxth_mind/storage/`. Implement the `BaseStorage` interface:

```python
from sxth_mind.storage.base import BaseStorage

class MyStorage(BaseStorage):
    async def get_user_mind(self, user_id: str) -> UserMind | None:
        ...
    # ... implement all abstract methods
```

Requirements:
- Async implementation
- Tests covering all operations
- Document any required dependencies in `pyproject.toml`

## Adding an LLM Provider

Providers live in `sxth_mind/providers/`. Implement the `BaseLLMProvider` interface:

```python
from sxth_mind.providers.base import BaseLLMProvider

class MyProvider(BaseLLMProvider):
    async def chat(self, messages, **kwargs) -> LLMResponse:
        ...
    async def chat_stream(self, messages, **kwargs):
        ...
```

## Code of Conduct

Be kind. Be respectful. Assume good intent.

We're building something useful together. Constructive feedback is welcome; personal attacks are not.

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas

Thanks for contributing!
