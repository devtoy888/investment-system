# Agnes Video V2.0 API Test Notes (2026-06-23)

## Video Generation API Details

### Endpoint
- **Create**: `POST https://apihub.agnes-ai.com/v1/videos`
- **Poll**: `GET https://apihub.agnes-ai.com/v1/videos/{task_id}`

### Parameters (Create)
| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| model | string | Yes | Must be `agnes-video-v2.0` |
| prompt | string | Yes | Detailed scene description |
| ratio | string | No | `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| resolution | string | No | `720p`, `1080p`, `480p` |

### Response (Create)
```json
{
  "id": "task_xxx",
  "task_id": "task_xxx",
  "video_id": "video_xxx",
  "status": "queued",
  "progress": 0,
  "seconds": "5.0",
  "size": "704x1280"
}
```

### Response (Poll - Completed)
Returns task object at **root level** (NOT nested under `data`):
```json
{
  "status": "completed",
  "progress": 100,
  "remixed_from_video_id": "https://platform-outputs.agnes-ai.space/videos/...",
  "video_id": "video_xxx",
  "size": "704x1280"
}
```

### Polling
- **Recommended**: `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>` (uses `video_id` from create response)
- **Legacy**: `GET https://apihub.agnes-ai.com/v1/videos/<TASK_ID>` (uses `task_id`)
- Add optional `?model_name=agnes-video-v2.0` to recommended endpoint when using upstream raw video ID or non-default model.

### Duration Control (NEW 2026-06-23)
Duration is controlled by `num_frames` and `frame_rate`: `seconds = num_frames / frame_rate`
- **Constraints**: `num_frames` ≤ 441, must follow `8n+1` rule (81, 121, 161, 241, 441)
- **frame_rate**: 1–60, recommended 24
- **Common settings**: 3s (81/24), 5s (121/24), 10s (241/24), 18s (441/24)
- **Note**: The API accepts `duration` param but ENFORCES ~5s regardless. Use multiple clips + ffmpeg concat for longer videos.

### Resolution Standardization (NEW)
The model supports 3 tiers: 480p, 720p, 1080p. Input dimensions are mapped to closest standard output size.
Recommended aspect ratios: 16:9 (landscape), 9:16 (portrait/phone), 1:1 (square), 4:3 (traditional), 3:4 (vertical portrait).

### Prompt Best Practices (NEW)
Structure: `[Subject] + [Action] + [Scene] + [Camera Movement] + [Lighting] + [Style]`
- Keep prompts focused on visual description; avoid narrative/abstract concepts
- Max ~2000 chars before truncation
- For multi-clip consistency: define character description ONCE and reuse identically in every prompt

### Content Policy Triggers (UPDATED)
Commonly rejected words: `bikini`, `wet skin`, `sweaty`, `tight`, `form-fitting`, `slip dress`, `nightgown`, `robe`, `pajama`
Safe alternatives: flowing summer dress, elegant/stylish/classic, golden hour lighting on skin

### Mode Types
- **Text-to-Video**: Just `model` + `prompt` (plus optional dims/frames)
- **Image-to-Video**: Add `image` (single URL) + prompt describing motion
- **Multi-Image**: Use `extra_body.image` (array) + prompt describing transitions
- **Keyframe Animation**: Use `extra_body.image` + `extra_body.mode: "keyframes"` + transition prompt

### Auth (CRITICAL)
Hermes `custom` provider reads key from `OPENAI_API_KEY` env var ONLY.
`CUSTOM_AGNES_API_KEY` is NOT picked up. Always use `OPENAI_API_KEY` in `.env`.

### Test Run
- Prompt: "a beautiful young Chinese woman with long black hair, wearing a stylish summer dress, standing on a tropical beach at sunset, gentle ocean breeze, cinematic lighting, photorealistic, 4k quality"
- Ratio: `9:16` (phone portrait)
- Resolution: `720p`
- Size: `704x1280`
- Duration: 5.04s
- File size: 1.67 MB
- Total generation time: ~2.5 min (queued → processing → completed)
