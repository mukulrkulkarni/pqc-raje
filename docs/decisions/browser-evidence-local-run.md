# Local Brave Browser Evidence Run

Run this procedure on the machine that contains Brave at:

```text
/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe
```

## Prerequisites

Start the local Flask app. Then install Playwright in a local virtual environment if needed:

```cmd
pip3 install playwright
```

The procedure does not install or download a browser. It uses the existing Brave executable.

## Run

From the repository root:

```cmd
python3 scripts/run_brave_browser_evidence.py --base-url http://127.0.0.1:5000
```

The script uses a temporary browser context and blocks service workers and network access. It records:

- app route loading
- script and stylesheet presence
- keyboard focus samples
- narrow viewport scroll width
- 200% zoom evidence
- screenshots
- offline documentation-route loading

Artifacts are written to `out/browser-evidence-local/`.

## Report back

Please return:

1. The complete terminal output.
2. `out/browser-evidence-local/browser-evidence.json`.
3. The three screenshots.
4. Any Playwright or Brave error text.

Screen-reader behavior remains unverified. We will report semantic HTML and automated accessibility evidence separately from manual assistive-technology evidence.
