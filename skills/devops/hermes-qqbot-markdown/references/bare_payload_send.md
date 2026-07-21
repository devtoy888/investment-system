# Bare payload markdown sender (QQ bot, bypasses Hermes delivery)

Use when you want to send markdown to a QQ bot and Hermes's `deliver=qqbot`
downgrades it to plain text. POST a raw `msg_type: 2` payload directly using
the bot's own `.env` credentials.

## Constraints
- NEVER hard-code app_id/secret. Read them from `.env` (Hermes loads `.env`
  but does not export it to the shell env, so `os.environ` won't have them).
- NEVER write `.env` — agent is forbidden; tell the user to edit it.
- The user's C2C openid for that bot == their Hermes `chat_id` for that bot.

## Reusable function

```python
import requests, os

def send_qq_markdown(app_id, secret, openid, markdown_text):
    """Send one markdown message to a QQ C2C user via bare payload.
    Returns count of chunks sent. Splits on '***' if > 4000 chars."""
    tok = requests.post('https://bots.qq.com/app/getAppAccessToken',
                        json={'appId': app_id, 'clientSecret': secret},
                        timeout=10).json().get('access_token')
    if not tok:
        return 0
    chunks = markdown_text.split('\n***\n') if '\n***\n' in markdown_text else [markdown_text]
    sent = 0
    for i, ch in enumerate(chunks):
        body = ch.strip()
        if not body:
            continue
        if i < len(chunks) - 1:
            body += '\n***'
        if len(body) > 4000:
            body = body[:4000]
        r = requests.post(f'https://api.sgroup.qq.com/v2/users/{openid}/messages',
                          headers={'Authorization': f'QQBot {tok}',
                                   'Content-Type': 'application/json'},
                          json={'msg_type': 2, 'markdown': {'content': body}},
                          timeout=15)
        if r.status_code == 200:
            sent += 1
    return sent

# Read credentials from .env without exporting
def load_env(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if line.startswith('QQ_APP_ID=') or line.startswith('QQ_CLIENT_SECRET='):
            k, v = line.split('=', 1)
            env[k] = v.strip().strip('"')
    return env

# Example for the default QQ bot (1904452472):
env = load_env('/opt/data/.env')
OPENID = '82BC393B5BF9B2DC01006D6DFA66CB9B'   # user's Hermes chat_id for that bot
send_qq_markdown(env['QQ_APP_ID'], env['QQ_CLIENT_SECRET'], OPENID, '# 标题\n正文 **加粗**')
```

## Notes
- `msg_type: 2` + `{"markdown": {"content": ...}}` is the correct structure;
  `msg_seq` is optional and does NOT affect rendering (verified: both with and
  without `msg_seq` rendered).
- Single messages up to ~6600 chars rendered fine in testing — QQ has no 4000
  hard limit; 4000 is purely Hermes's `MAX_MESSAGE_LENGTH` split threshold.
- This is the pattern the OpenRouter free-model monitor uses (script does
  `check` mode, then calls this on new models).
