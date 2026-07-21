# Agnes AI Model Catalog (Reference)

## API Base URL
`https://apihub.agnes-ai.com/v1`

## Authentication
`Authorization: Bearer YOUR_API_KEY`

## Text Models

### agnes-2.0-flash (RECOMMENDED)
- **Endpoint:** `/v1/chat/completions`
- **Context window:** 256K
- **Max output:** 64K tokens
- **Capabilities:** Chat, streaming, tool calling, coding, reasoning, image understanding, agent workflows
- **Free tier RPM:** 20 (actual executable)
- **Best for:** General use, coding, reasoning, vision input, streaming

### agnes-1.5-flash
- **Endpoint:** `/v1/chat/completions`
- **Context window:** 256K
- **Capabilities:** Fast chat, text generation, image URL input, low-latency inference
- **Free tier RPM:** 20 (actual executable)
- **Best for:** High-throughput chat, content generation, summarization

## Image Models

### agnes-image-2.1-flash (RECOMMENDED)
- **Endpoint:** `/v1/images/generations`
- **Capabilities:** High-density visual generation, image editing, flexible sizes, URL or Base64 output
- **Free tier RPM:** 20 (1K), 10 (2K), 1 (3K/4K)
- **Best for:** Detailed compositions, marketing assets, character visuals

### agnes-image-2.0-flash
- **Endpoint:** `/v1/images/generations`
- **Capabilities:** Text-to-image, image-to-image, URL output, Base64 output
- **Free tier RPM:** 20 (1K)
- **Best for:** Fast image generation, creative images, product visuals

## Video Models

### agnes-video-v2.0
- **Endpoint:** `/v1/videos`
- **Capabilities:** Text-to-video, image-to-video, multi-image video, keyframe animation, async generation
- **Free tier RPM:** 20 (actual executable)
- **Result query:** `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>`
- **Best for:** Storytelling, marketing videos, product demos

## Subscription Quotas (Paid)

| Plan | Price | Text (2.0-flash) | Images | Video |
|------|:---:|:----------------:|:------:|:-----:|
| Starter | $4 | 1,500 req/5h; 15K/week | 4K/day | 500s/day |
| Plus | $10 | 7,500 req/5h; 75K/week | 4K/day | 500s/day |
| Pro | $50 | 30K req/5h; 300K/week | 4K/day | 500s/day |

## Compatibility Notes
- Fully OpenAI-compatible API format
- Supports streaming, tool calling, vision inputs
- `thinking` mode and advanced parameters supported on chat models
- For 400 errors: verify required params, request body shape, image URL accessibility
- For 401 errors: verify API key, bearer token format, account status
- For 429 errors: reduce concurrency, add retry with backoff
- For 500/502/503/520: retry with exponential backoff

## Sources
- GitHub: https://github.com/AgnesAI-Labs/Agnes-AI
- Docs: https://agnes-ai.com/doc/overview
- Pricing: https://platform.agnes-ai.com/
- Platform: https://platform.agnes-ai.com/
