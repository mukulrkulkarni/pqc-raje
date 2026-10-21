# Browser Evidence Notes

**Chunk status:** checkpointed. The evidence collector correction and screenshot field additions are complete and passed static validation. No browser evidence was collected in this correction chunk.

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

The collector writes the native values to `app_script_count` and `app_scripts_outer_html`; it derives the compatibility field `app_has_script` from `script_count > 0`. It calls Playwright `page.screenshot` after page load, saves `app-page.png` in the requested output directory, and records `app_screenshot_path` and `app_screenshot_status`. WSL gateway discovery, CDP endpoint selection, Playwright `connect_over_cdp`, and all other existing collector scope remain unchanged.

## Expected JSON

A future user-run collector invocation must write `browser-evidence.json` with these relevant fields. For an app document with no script elements, the expected values are:

```json
{
  "base_url": "http://127.0.0.1:5000",
  "cdp_url": "http://127.0.0.1:9222",
  "app_url": "http://127.0.0.1:5000/app/",
  "app_script_count": 0,
  "app_scripts_outer_html": [],
  "app_has_script": false,
  "app_has_stylesheet": false,
  "app_screenshot_path": "out/browser-evidence-local/app-page.png",
  "app_screenshot_status": "captured"
}
```

If scripts exist, `app_script_count` equals the length of `app_scripts_outer_html`, and each list item is the script element's `outerHTML` as returned by the browser. `app_screenshot_status` is `captured` only after Playwright successfully writes the screenshot.

## Commands and actual static results

```cmd
python -m py_compile scripts/run_brave_browser_evidence.py
```

Result: exit code 0; compilation passed.

```cmd
python scripts/run_brave_browser_evidence.py --help
```

Result: exit code 0; usage and all five supported options rendered without a browser connection.

The negative invocation ran through a Python subprocess wrapper so its expected argparse exit code did not fail the tool host:

```cmd
python scripts/run_brave_browser_evidence.py --connect-check
```

Result: collector exit code 2; argparse printed `--connect-check requires --diagnose-cdp`. The wrapper exited 0 after recording that expected result.

No browser, CDP, DOM helper, screenshot, browser accessibility, or assistive-technology command ran in this correction. Static checks validate syntax and CLI control flow only; they do not constitute browser evidence.

## Positive, negative, and edge evidence

| Category | Check | Actual result |
|---|---|---|
| Positive | Python compilation of collector | Passed: exit code 0 |
| Negative | `--connect-check` without `--diagnose-cdp` is rejected | Passed: collector exit code 2 and required-argument error |
| Edge | `--help` renders without a browser connection | Passed: exit code 0 and usage rendered |
| Browser required | Brave/CDP navigation, native DOM output, screenshot generation, and rendered DOM output | Not run; no browser evidence collected |

## Limitations and recovery

Screen-reader and assistive-technology behavior remains unverified. No browser visual, focus-order, zoom/reflow, script-disabled, network-disabled, CSP, automated accessibility, screenshot, or browser evidence exists from this correction. Do not treat static checks or a collector implementation change as browser evidence.

To collect browser evidence, the user must run the corrected collector against an authorized local Brave/CDP session and supply its output. Capture the resulting JSON and screenshot without changing application files. The `app_script_count`, `app_scripts_outer_html`, `app_screenshot_path`, and `app_screenshot_status` fields then provide the authoritative collected result.
