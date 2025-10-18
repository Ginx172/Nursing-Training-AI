# 🐍 Nursing Training AI - Python SDK

Official Python client library for the Nursing Training AI API.

## Installation

```bash
pip install nursing-ai-sdk
```

## Quick Start

```python
from nursing_ai_sdk import NursingAIClient

# Initialize client with API key
client = NursingAIClient(api_key="your_enterprise_api_key")

# Get user information
user = client.users.get("user_123")
print(f"User: {user.name}, Band: {user.current_band}")

# Search questions
questions = client.questions.search(
    specialty="amu",
    band="band_5",
    limit=10
)

# Get user analytics
analytics = client.analytics.get_user_analytics(
    user_id="user_123",
    date_from=datetime(2025, 1, 1),
    date_to=datetime.now()
)
print(f"Accuracy: {analytics.accuracy_percentage}%")

# Get team analytics (Enterprise only)
team_analytics = client.organizations.get_team_analytics(
    organization_id="org_123"
)
```

## Features

- ✅ Full API coverage
- ✅ Type hints and autocomplete
- ✅ Automatic retries
- ✅ Rate limit handling
- ✅ Comprehensive error handling
- ✅ Async support (coming soon)

## Documentation

Full documentation: https://docs.nursingtrainingai.com/sdk/python

## Support

Email: developers@nursingtrainingai.com

