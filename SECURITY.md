# Security

## Security Model

sxth-mind is a **library** designed to be integrated into your application. It provides cognitive state management, not a complete application stack.

### What sxth-mind handles

- **SQL injection prevention**: All database queries use parameterized statements
- **Data serialization**: Pydantic models validate and sanitize data structures
- **Pluggable storage**: You control where data is stored

### What you handle

- **Authentication**: Verify users before calling `mind.chat(user_id, ...)`
- **Authorization**: Ensure users can only access their own data
- **Rate limiting**: Protect against abuse (especially important since LLM calls cost money)
- **Network security**: TLS, firewalls, VPCs, etc.
- **API key management**: Secure your LLM provider credentials

## Production Deployment

The CLI command `sxth-mind serve` is for **development and demos only**.

For production, integrate the FastAPI app into your own application:

```python
from fastapi import FastAPI, Depends, HTTPException
from sxth_mind.api import create_app
from your_app.auth import get_current_user  # Your auth

app = FastAPI()

# Mount sxth-mind under your auth
sxth_app = create_app(adapter=YourAdapter())
app.mount("/mind", sxth_app)

# Or wrap individual calls
@app.post("/chat")
async def chat(message: str, user = Depends(get_current_user)):
    mind = get_mind()
    return await mind.chat(user.id, message)
```

## Data Privacy

sxth-mind stores:

- **UserMind**: User-level patterns, preferences, identity data
- **ProjectMind**: Project-specific context and progress
- **ConversationMemory**: Recent message history (sliding window)
- **Nudges**: Proactive suggestions

All data is stored in whatever storage backend you configure. You are responsible for:

- Data retention policies
- GDPR/CCPA compliance
- Encryption at rest (if required)
- Backup and recovery

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it via:

1. **GitHub Security Advisories**: [Report a vulnerability](https://github.com/sxth-ai/sxth-mind/security/advisories/new)
2. **Email**: hello@sxth.ai

Please do not open public issues for security vulnerabilities.

We will respond within 48 hours and work with you to understand and address the issue.
