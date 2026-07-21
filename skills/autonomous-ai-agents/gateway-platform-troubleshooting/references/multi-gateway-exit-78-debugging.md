# Multi-Profile Gateway Exit Code 78 Debugging

## Real Session Transcript

**Symptom:** s6-supervise for `gateway-llm-wiki` was running (PID 153), but the actual hermes gateway process was absent. s6 was not restarting it.

### Step 1: s6 Status → PID = 0

```
$ od -A n -t u1 /run/service/gateway-llm-wiki/supervise/status
64   0   0   0   106 86 215 229  15  84  91 163  64   0   0   0
106 86 215 229  15 118 132 204   0   0   0   0   0   0   0   0
 78   0   8
```

Byte 0: `64` = ready flag. Bytes 1–4: `0 0 0 0` = PID is 0 (no process). The final `78  0  8` is the exit code information embedded in the status — **exit 78**.

### Step 2: death_tally → Exit Code 78

```
$ od -A n -t u1 /run/service/gateway-llm-wiki/supervise/death_tally
 64   0   0   0  106  86 215 229  15  84  91 163  78   0
```

Byte 5: `78` = EX_CONFIG. Byte 6: `0` = no signal, normal exit.

### Step 3: Finish Script → Permanent Stop

```
$ cat /run/service/gateway-llm-wiki/finish
#!/command/with-contenv sh
if [ "$1" = "78" ]; then
  exit 125    # ← tells s6 NEVER to restart
fi
exit 0
```

Exit 125 from finish = **permanent stop**. The service won't restart until manually intervened.

### Step 4: gateway_state.json → multiplex config error

```json
{
  "gateway_state": "startup_failed",
  "exit_reason": "Profile 'default' enables the port-binding platform 'feishu',
    but gateway.multiplex_profiles is on...",
  "argv": ["/opt/hermes/.venv/bin/hermes", "gateway", "run", "--replace"]
}
```

Note: `argv` shows no `-p llm-wiki` flag, meaning this state file was written by the DEFAULT profile's gateway (and overwrote the llm-wiki state). This is a contamination issue — the state file is stale.

### Step 5: Compare with Working Profile (investment)

**Config diff** (the root cause):

```bash
$ grep -n 'multiplex_profiles' /opt/data/profiles/*/config.yaml
profiles/llm-wiki/config.yaml:572:  multiplex_profiles: true      ← WRONG
profiles/investment/config.yaml:602:  multiplex_profiles: false   ← CORRECT
```

The llm-wiki profile had `gateway.multiplex_profiles: true` while the investment profile (working) had `false`. In a multi-gateway setup (separate s6 processes per profile), secondary profiles MUST NOT have multiplex mode enabled.

### Step 6: Force-Restart

After fixing the config:

```bash
# Clear stale state and restart loop detection
rm -f /opt/data/profiles/llm-wiki/gateway_state.json
rm -f /opt/data/profiles/llm-wiki/gateway/restart_loop.json

# Force s6 to start the service
printf u > /run/service/gateway-llm-wiki/supervise/control
```

Result: gateway process started successfully (PID 1715) and QQ bot came online.

## Key Takeaways

1. **s6 status PID = 0** means the process has exited and s6 is NOT restarting it
2. **Exit code 78** (EX_CONFIG) is a fatal configuration error — the finish script exits 125, permanently stopping the service
3. **`gateway_state.json` contamination** — the default profile can overwrite state files of other profiles. Check the `argv` field: if no `-p <profile>` flag, the state is stale.
4. **`multiplex_profiles: true` on a secondary profile** is the most common cause of exit 78 in multi-gateway setups. Only the default profile should have this enabled.
5. **Force-restart** a permanently stopped s6 service by writing `u` to its control pipe, NOT by `s6-svc -r` (which won't restart a service whose finish script said "don't restart").
