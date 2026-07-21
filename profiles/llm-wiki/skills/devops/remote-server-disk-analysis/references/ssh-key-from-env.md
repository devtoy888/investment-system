# SSH Key Extraction from .env

## The Problem

SSH keys are multi-line values. When stored in a `.env` file, they're typically written as:

```
REMOTE_HOST_SSH_KEY="-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjE...\n-----END OPENSSH PRIVATE KEY-----"
```

Where `\n` is literal text (backslash + n), not real newlines. The entire value is one long line inside quotes.

## Extraction Recipe

### Preferred: Manual quote parsing with \n handling

When the .env has a MIX of real newlines and literal `\n` sequences (common when the user pastes the key and the editor partially expands escapes), the simple `replace` approach can corrupt the base64. Use quote-aware parsing instead:

```python
with open('/opt/data/.env') as f:
    content = f.read()

import re, os, stat

start = content.find('REMOTE_HOST_SSH_KEY=')
rest = content[start:]
eq = rest.find('=')
val = rest[eq+1:].strip()

key_raw = ''
if val.startswith('"'):
    i = 1
    while i < len(val):
        c = val[i]
        if c == '"':
            break
        if c == '\\':
            if i+1 < len(val):
                next_c = val[i+1]
                if next_c == 'n':
                    key_raw += '\n'   # convert literal \n to real newline
                    i += 2
                    continue
                else:
                    key_raw += next_c  # other escapes as-is
                    i += 2
                    continue
        key_raw += c
        i += 1
else:
    key_raw = val.rstrip('\n')

# Write with trailing newline
key_path = os.path.expanduser('~/.ssh/id_rsa')
os.makedirs(os.path.expanduser('~/.ssh'), mode=0o700, exist_ok=True)
with open(key_path, 'w') as f:
    f.write(key_raw)
    if not key_raw.endswith('\n'):
        f.write('\n')
os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
```

### Simpler alternative (when no mixed newlines):

If the .env key is purely one long line with `\n` escapes (no real newlines inside the quotes), this simpler approach works:

### Verification:

```bash
ssh-keygen -lf ~/.ssh/id_rsa
# Expected: 256 SHA256:... (ED25519)
```

**Fallback validator (when `ssh-keygen` fails but the key is actually valid):**
```python
from cryptography.hazmat.primitives import serialization
with open('/opt/data/home/.ssh/id_rsa', 'rb') as f:
    key = serialization.load_ssh_private_key(f.read(), password=None)
    print(f"✅ Valid: {type(key).__name__}")
```

### Troubleshooting:

| Symptom | Cause | Fix |
|---------|-------|-----|
| `error in libcrypto` | Missing trailing newline OR corrupted base64 | Add trailing newline; verify with `cryptography` first |
| `not a key file` | Missing trailing newline or corrupted content | Add trailing newline (`ssh-keygen` requires it even if `cryptography` doesn't) |
| `Permission denied (publickey)` | Key doesn't match authorized_keys | Check the remote host's `~/.ssh/authorized_keys` |
| Connects once then fails | known_hosts conflict or missing `-o IdentitiesOnly=yes` | Use `-v` to see which key is being offered; add `IdentitiesOnly=yes` |
| **SSH works in verbose mode but not in normal mode** | Agent forwarding or key chain conflict | Always include `-o IdentitiesOnly=yes` to force the explicit key |

### Quick test:

```bash
ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    -o BatchMode=yes -o IdentitiesOnly=yes user@host "echo SSH_OK"
```

For debugging, add `-v` (verbose) to see which key is being offered and how the server responds.
