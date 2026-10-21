# Local Brave CDP Evidence Procedure

Run the Windows commands in **Windows PowerShell** and the Linux commands in
**WSL**. This procedure diagnoses CDP only. It does not install a browser,
change application pages, or claim browser evidence.

## 1. Windows Brave preflight and launch

In PowerShell, use the approved executable path and a new temporary profile.
Do not reuse a normal Brave profile. Close any prior evidence instance first.

```powershell
$Brave = 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
if (-not (Test-Path -LiteralPath $Brave -PathType Leaf)) { throw "BRAVE_MISSING: $Brave" }
$Profile = Join-Path $env:TEMP 'brave-cdp-evidence-profile'
Remove-Item -LiteralPath $Profile -Recurse -Force -ErrorAction SilentlyContinue
Start-Process -FilePath $Brave -ArgumentList @(
  '--headless=new', '--disable-gpu', "--user-data-dir=$Profile",
  '--remote-debugging-address=0.0.0.0', '--remote-debugging-port=9222', 'about:blank'
)
```

Expected positive output: no `BRAVE_MISSING` exception. A temporary profile
limits use of personal browser state. `0.0.0.0` is required for the WSL-gateway
path; it exposes CDP to reachable networks until cleanup. Keep the host on a
trusted private network and stop Brave when finished.

## 2. Windows listener and localhost verification

Wait briefly, then run both commands in PowerShell:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 9222 |
  Format-Table -AutoSize LocalAddress,LocalPort,OwningProcess
Invoke-RestMethod http://127.0.0.1:9222/json/version |
  Select-Object Browser,webSocketDebuggerUrl
```

Positive: listener address is `0.0.0.0` (or the Windows-side WSL-reachable
address), and `Browser` plus `webSocketDebuggerUrl` appear. Negative:
`Connection refused` or no listener means Brave did not launch, its arguments
were not accepted, or another process owns the port. Check:

```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 9222 -State Listen).OwningProcess
```

If the listener is only `127.0.0.1`, WSL may not reach it. Relaunch using the
address argument above. A `::` listener is an IPv6 edge case; use an IPv4
listener for these WSL commands.

## 3. WSL host-address and CDP verification

In WSL, derive the Windows gateway rather than assuming WSL `localhost` maps
to Windows:

```bash
WIN_HOST=$(awk '/^nameserver / { print $2; exit }' /etc/resolv.conf)
printf 'WIN_HOST=%s\n' "$WIN_HOST"
python3 scripts/run_brave_browser_evidence.py \
  --diagnose-cdp --cdp-url "http://$WIN_HOST:9222"
```

Positive: `CDP_HTTP_OK:` then a message that HTTP is reachable. Negative:
`CDP_HTTP_FAILED` means WSL cannot reach CDP. First repeat Section 2. If it
passes in Windows but fails here, diagnose the listener address and firewall;
do not change the application.

## 4. Firewall diagnosis

In elevated PowerShell, inspect active inbound rules before changing them:

```powershell
Get-NetFirewallProfile | Select-Object Name,Enabled
Get-NetFirewallRule -Enabled True -Direction Inbound |
  Get-NetFirewallPortFilter |
  Where-Object { $_.LocalPort -eq '9222' } |
  Format-Table -AutoSize
```

If Windows localhost succeeds, the listener is `0.0.0.0`, and WSL still fails,
a firewall policy can block the WSL virtual adapter. Use organization-approved
firewall procedures only. Do not disable the firewall globally. Remove any
temporary port rule after diagnosis. Endpoint protection or corporate policy
can also block CDP; preserve the exact outputs for the administrator.

## 5. Playwright connection check

Only after the WSL HTTP probe succeeds, run:

```bash
python3 scripts/run_brave_browser_evidence.py \
  --diagnose-cdp --connect-check --cdp-url "http://$WIN_HOST:9222"
```

Positive: `PLAYWRIGHT_CDP_OK: contexts=...`. This verifies
`connect_over_cdp`; it does **not** collect browser evidence. `PLAYWRIGHT_UNAVAILABLE`
means the approved Python package is absent. Install only that project-approved
dependency if authorized; do not run Playwright browser installation commands.
`PLAYWRIGHT_CDP_FAILED` after HTTP success identifies a WebSocket/CDP transport
problem; retain the output.

## 6. Collect evidence only after CDP passes

Start the local application separately, then run:

```bash
python3 scripts/run_brave_browser_evidence.py \
  --base-url http://127.0.0.1:5000 --cdp-url "http://$WIN_HOST:9222"
```

This later command is outside the troubleshooting result. It writes evidence
under `out/browser-evidence-local/` only when the connection succeeds.

## Cleanup and limitations

Close Brave and remove the temporary profile in PowerShell:

```powershell
Get-Process brave -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item -LiteralPath $Profile -Recurse -Force -ErrorAction SilentlyContinue
```

Do not use `--remote-debugging-address=0.0.0.0` longer than needed. CDP grants
full browser control to clients that can reach it. Screen-reader and other
assistive-technology (AT) behavior remains unverified. Semantic HTML and any
automated accessibility result do not replace manual AT testing.
