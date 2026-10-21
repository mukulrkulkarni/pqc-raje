# Browser CDP Troubleshooting Notes

**Status:** procedure prepared; no browser, CDP, network, or accessibility
evidence was collected in this subchunk.

## Diagnosis

The prior procedure launched the Windows-mounted executable from WSL and then
probed WSL `127.0.0.1:9222`. That route is not reliable: WSL localhost does not
always reach a Windows-host listener, and a loopback-only Windows listener
cannot serve WSL through the gateway. The revised procedure separates Windows
launch and verification from WSL reachability.

## User-run diagnostic sequence

The authoritative copyable commands and expected outputs are in
[Local Brave CDP Evidence Procedure](browser-evidence-local-run.md). The steps
are deliberately ordered:

1. Validate the Windows Brave path and launch Brave in PowerShell.
2. Confirm the Windows listener address and Windows `127.0.0.1` CDP response.
3. Obtain the WSL Windows-gateway address from `/etc/resolv.conf`.
4. Probe `http://$WIN_HOST:9222/json/version` from WSL.
5. Inspect firewall policy only when Windows localhost works but WSL fails.
6. Test Playwright `connect_over_cdp` only after the HTTP endpoint succeeds.

The launch uses a temporary profile and `--remote-debugging-address=0.0.0.0`.
This accommodates the WSL gateway but increases exposure. The procedure limits
that exposure to a trusted private network and requires explicit cleanup.

## Positive, negative, and edge diagnostics

| Category | Command or condition | Expected output or interpretation |
|---|---|---|
| Positive | `Test-Path -LiteralPath $Brave -PathType Leaf` | `True`; launcher path is valid. |
| Positive | Windows `/json/version` request | `Browser` and `webSocketDebuggerUrl` values. |
| Positive | WSL `--diagnose-cdp` probe | `CDP_HTTP_OK:`. |
| Positive | WSL `--diagnose-cdp --connect-check` | `PLAYWRIGHT_CDP_OK:`. |
| Negative | Missing Brave executable | `BRAVE_MISSING`; stop before CDP work. |
| Negative | No port listener or Windows refusal | Brave did not expose CDP; inspect process and arguments. |
| Negative | Windows works; WSL returns `CDP_HTTP_FAILED` | Diagnose listener address then firewall policy. |
| Negative | HTTP succeeds; connect check fails | Preserve `PLAYWRIGHT_CDP_FAILED`; investigate CDP WebSocket transport. |
| Edge | Listener is `127.0.0.1` only | Relaunch with `--remote-debugging-address=0.0.0.0`. |
| Edge | Listener is IPv6 `::` only | Relaunch with an IPv4-compatible listener for this procedure. |
| Edge | `$WIN_HOST` is empty or malformed | WSL networking configuration is unavailable; do not substitute an arbitrary host. |
| Edge | Corporate policy blocks port 9222 | Use approved administrator process; do not disable firewall globally. |

## Static test evidence

Executed from the repository root:

```cmd
python -m py_compile scripts\run_brave_browser_evidence.py
python scripts\run_brave_browser_evidence.py --help
python scripts\run_brave_browser_evidence.py --connect-check
```

The first command must succeed. The help command must list `--diagnose-cdp` and
`--connect-check`. The third command is a negative argument-validation check:
it must fail with `--connect-check requires --diagnose-cdp`, without a network
connection. These tests verify syntax and CLI control flow only; the task
prohibits browser evidence collection in this troubleshooting subchunk.

## Limitations

- No Windows PowerShell command, Brave launch, listener, firewall query, WSL
  connection, Playwright connection, screenshot, DOM capture, or browser test
  ran here.
- The actual Windows gateway and firewall policy depend on the user's computer.
- The script uses a three-second HTTP timeout; a slow or policy-restricted host
  can require manual investigation rather than retries.
- Screen-reader and other assistive-technology (AT) behavior remains
  unverified. Semantic HTML and automated accessibility checks cannot establish
  AT usability.
- Do not treat this procedure or static checks as collected browser evidence.
