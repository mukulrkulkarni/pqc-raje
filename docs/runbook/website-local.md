# Run the companion website locally

## Why you need a local server

The static companion website uses root-absolute links like `/modules/index.html`.

- With `file://.../website/index.html`, a link `/modules/index.html` becomes:
  - `file:///modules/index.html` (or `file:///C:/modules/index.html` on Windows)
  - which does not exist.

Using a local HTTP server makes `/modules/...` resolve under the website root.

## Recommended (single entrypoint)

From the repository root:

```bash
python scripts/dev_local.py
```

Then open:

- Website: http://localhost:8000/
- App: http://localhost:5000/

(You can still run `scripts/serve_website.py` if you only need docs.)

To change port:

```bash
set PORT=8001
python scripts/serve_website.py
```

## Alternative (one-liner)

```bash
python -m http.server 8000 --directory website
```

## Notes

- This is a static server only. It does not run the Flask app.
- The Flask app is separate (typically served on a different port/domain).
