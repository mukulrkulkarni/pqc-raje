# Browser Evidence Notes

**Chunk status:** partial. The evidence collector correction is complete, but no browser evidence was collected in this correction chunk.

## Current and target status

The target remains the server-rendered, no-JavaScript `/app` workflow on local `127.0.0.1`. The prior local CDP collector reported `app_has_script=true`, while a manual Brave console check reported `document.scripts=[]`. This correction replaces locator-based script detection with a native DOM evaluation. It changes no application page, JavaScript, or application behavior.

The authorized Windows Brave executable preflight previously returned `BRAVE_MISSING` for:

```cmd
if exist "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" (echo BRAVE_PRESENT) else (echo BRAVE_MISSING)
```

No Brave browser or CDP session was launched for this correction.

## Corrected collector method

After `/app/` loads, `scripts/run_brave_browser_evidence.py` calls `page.evaluate` with this native browser expression:

```javascript
() => ({
  script_count: document.scripts.length,
  scripts: Array.from(document.scripts, (script) => script.outerHTML)
})
```

The collector writes the native values to `app_script_count` and `app_scripts_outer_html`; it derives the compatibility field `app_has_script` from `script_count > 0`. WSL gateway discovery, CDP endpoint selection, Playwright `connect_over_cdp`, and all other existing collector scope remain unchanged.

## Expected JSON

A future user-run collector invocation must write `browser-evidence.json` with these relevant fields. For an app document with no script elements, the expected values are:

```json
{
  "base_url": "http://127.0.0.1:5000",
  "cdp_url": "http://WINDOWS_GATEWAY:9222",
  "app_url": "http://127.0.0.1:5000/app/",
  "app_script_count": 0,
  "app_scripts_outer_html": [],
  "app_has_script": false,
  "app_has_stylesheet": false
}
```

If scripts exist, `app_script_count` equals the length of `app_scripts_outer_html`, and each list item is the script element's `outerHTML` as returned by the browser.

## Commands and results

```cmd
python -m py_compile scripts/run_brave_browser_evidence.py
```

Result: passed.

```cmd
python scripts/run_brave_browser_evidence.py --help
```

Result: passed; CLI exposes `--diagnose-cdp` and `--connect-check`.

```cmd
python scripts/run_brave_browser_evidence.py --connect-check
```

Result: rejected with exit code 2 because `--connect-check` requires `--diagnose-cdp`.

The native DOM helper was not run without a browser. These checks validate script syntax and CLI control flow only; they do not constitute browser evidence.

## Positive, negative, and edge evidence

| Category | Check | Result |
|---|---|---|
| Positive | Native evaluation returns one script count and that script's `outerHTML` | Pending execution |
| Negative | `--connect-check` without `--diagnose-cdp` is rejected | Pending execution |
| Edge | Native evaluation returns zero count and an empty list for no script elements | Pending execution |
| Browser required | Brave/CDP navigation and rendered DOM output | Not run; no user-run evidence supplied |

## Limitations and recovery

Screen-reader and assistive-technology behavior remains unverified. No browser visual, focus-order, zoom/reflow, script-disabled, network-disabled, CSP, or automated accessibility evidence exists from this correction. Do not treat static checks or a collector implementation change as browser evidence.

To collect browser evidence, the user must run the corrected collector against an authorized local Brave/CDP session and supply its output. Capture the resulting JSON without changing application files. The `app_script_count` and `app_scripts_outer_html` fields then provide the authoritative native DOM result for script elements.
