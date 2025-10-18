# 📦 Nursing Training AI - JavaScript/TypeScript SDK

Official JavaScript/TypeScript client library for the Nursing Training AI API.

## Installation

```bash
npm install @nursing-ai/sdk
# or
yarn add @nursing-ai/sdk
```

## Quick Start

### TypeScript

```typescript
import { NursingAIClient } from '@nursing-ai/sdk';

// Initialize client
const client = new NursingAIClient({
  apiKey: 'your_enterprise_api_key',
  baseUrl: 'https://api.nursingtrainingai.com' // optional
});

// Get user
const user = await client.users.get('user_123');
console.log(`User: ${user.name}, Band: ${user.currentBand}`);

// Get analytics
const analytics = await client.analytics.getUserAnalytics('user_123');
console.log(`Accuracy: ${analytics.accuracyPercentage}%`);
```

### JavaScript

```javascript
const { NursingAIClient } = require('@nursing-ai/sdk');

const client = new NursingAIClient({ apiKey: 'your_key' });

client.users.get('user_123')
  .then(user => console.log(user))
  .catch(error => console.error(error));
```

## Features

- ✅ Full TypeScript support
- ✅ Promise-based API
- ✅ Automatic retries
- ✅ Error handling
- ✅ Rate limit management

## Documentation

https://docs.nursingtrainingai.com/sdk/javascript

