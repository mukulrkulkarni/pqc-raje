"""Bounded W1 static and Flask URL/link inventory and resolver."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
WEBSITE = ROOT / "website"
DOCS = ROOT / "docs"
ATTRS = {"href", "src", "action", "poster", "download"}
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"): self.ids.add(values["id"])
        if tag == "a" and values.get("name"): self.ids.add(values["name"])
        for key, value in attrs:
            if key in ATTRS and value is not None:
                self.refs.append((tag, key, value))


def parse(path):
    p = Parser(); p.feed(path.read_text(encoding="utf-8")); return p


def static_target(url_path):
    rel = url_path.lstrip("/")
    candidate = WEBSITE / rel
    if url_path.endswith("/") or candidate.is_dir(): candidate = candidate / "index.html"
    return candidate


def classify_static(source, served, ref, parsers):
    parts = urlsplit(ref)
    if parts.scheme in EXTERNAL_SCHEMES or ref.startswith("//"):
        return "external", "remote URL not fetched"
    if "{{" in ref or "{%" in ref:
        return "planned", "template expression outside static vocabulary"
    resolved = urlsplit(urljoin(served, ref))
    target = static_target(resolved.path)
    if not target.is_file():
        return "broken", f"missing static target {target.relative_to(ROOT).as_posix()}"
    if resolved.fragment:
        parser = parsers.get(target)
        if parser is None and target.suffix.lower() in {".html", ".htm"}:
            parser = parse(target); parsers[target] = parser
        if parser is not None and resolved.fragment not in parser.ids:
            return "broken", f"missing fragment #{resolved.fragment}"
    return "valid", target.relative_to(ROOT).as_posix()


def flask_inventory():
    # Import only after path setup when run from repository root.
    from app import create_app
    app = create_app({"TESTING": True, "SECRET_KEY": "w1-audit"})
    rules = sorted((r.rule, sorted(r.methods - {"HEAD", "OPTIONS"}), r.endpoint) for r in app.url_map.iter_rules())
    return app, rules


def classify_generated(source, served, ref, client):
    parts = urlsplit(ref)
    if parts.scheme in EXTERNAL_SCHEMES or ref.startswith("//"):
        return "external", "remote URL not fetched"
    resolved = urlsplit(urljoin(served, ref))
    response = client.get(resolved.path)
    if response.status_code >= 400:
        return "broken", f"GET {resolved.path} -> {response.status_code}"
    if resolved.fragment and response.mimetype == "text/html":
        p = Parser(); p.feed(response.get_data(as_text=True))
        if resolved.fragment not in p.ids:
            return "broken", f"GET {resolved.path} lacks #{resolved.fragment}"
    return "valid", f"GET {resolved.path} -> {response.status_code}"


def main():
    parsers = {}
    rows = []
    static_files = sorted(p for p in WEBSITE.rglob("*.html") if "_includes" not in p.parts)
    for source in static_files:
        served = "/" + source.relative_to(WEBSITE).as_posix()
        p = parse(source); parsers[source] = p
        for tag, attr, ref in p.refs:
            status, evidence = classify_static(source, served, ref, parsers)
            rows.append({"surface":"static", "source":source.relative_to(ROOT).as_posix(), "served":served,
                         "tag":tag, "attribute":attr, "target":ref, "classification":status, "evidence":evidence})

    app, rules = flask_inventory()
    client = app.test_client()
    generated = [(DOCS/"GETTING_STARTED.html", "/"), (DOCS/"modules"/"index.html", "/docs/modules")]
    names = sorted({p.stem.replace("_tutorial_side_by_side", "") for p in (DOCS/"modules").glob("*_tutorial_side_by_side.html")})
    for name in names:
        generated.append((DOCS/"modules"/f"{name}_tutorial_side_by_side.html", f"/docs/modules/{name}/tutorial"))
    for source, served in generated:
        p = parse(source)
        for tag, attr, ref in p.refs:
            status, evidence = classify_generated(source, served, ref, client)
            rows.append({"surface":"flask-docs", "source":source.relative_to(ROOT).as_posix(), "served":served,
                         "tag":tag, "attribute":attr, "target":ref, "classification":status, "evidence":evidence})

    templates = sorted((ROOT/"app"/"templates").glob("app_*.html"))
    endpoint_re = re.compile(r"url_for\(['\"]([^'\"]+)['\"]")
    endpoints = {endpoint for _, _, endpoint in rules}
    for source in templates:
        text = source.read_text(encoding="utf-8")
        p = parse(source)
        for tag, attr, ref in p.refs:
            match = endpoint_re.search(ref)
            if match:
                endpoint = match.group(1)
                status = "valid" if endpoint in endpoints else "broken"
                evidence = f"endpoint {endpoint} {'registered' if status == 'valid' else 'missing'}"
            elif "{{" in ref or "{%" in ref:
                status, evidence = "planned", "dynamic template URL requires workflow state"
            else:
                status, evidence = classify_generated(source, "/app/", ref, client)
            rows.append({"surface":"flask-app", "source":source.relative_to(ROOT).as_posix(), "served":"dynamic /app workflow",
                         "tag":tag, "attribute":attr, "target":ref, "classification":status, "evidence":evidence})

    # Explicit route vocabulary checks include positive, trailing slash, malformed, and missing targets.
    probes = []
    from app.routes.docs import ALLOWED_MODULE_DOCS, ALLOWED_TUTORIAL_ASSETS
    positive_paths = ["/", "/docs/modules", "/app/"]
    for name in sorted(ALLOWED_MODULE_DOCS):
        positive_paths.extend([f"/docs/modules/{name}", f"/docs/modules/{name}/tutorial"])
        positive_paths.extend(f"/docs/modules/{name}/assets/{asset}" for asset in sorted(ALLOWED_TUTORIAL_ASSETS))
    for path in positive_paths:
        response = client.get(path); probes.append({"kind":"route-vocabulary", "path":path, "status":response.status_code,
                                                    "classification":"valid" if response.status_code < 400 else "broken"})
    for path in ["/docs/modules/", "/docs/modules/config/", "/docs/modules/config/tutorial/", "/app"]:
        response = client.get(path, follow_redirects=False); probes.append({"kind":"trailing-slash", "path":path, "status":response.status_code,
                                                                           "location":response.headers.get("Location")})
    for path in ["/docs/modules/missing", "/docs/modules/CONFIG", "/docs/modules/../config",
                 "/docs/modules/config/assets/missing.js", "/docs/modules/config/assets/../theme.js",
                 "/docs/modules/missing/tutorial", "/app/missing", "/app/download/missing.csv"]:
        response = client.get(path, follow_redirects=False); probes.append({"kind":"negative", "path":path, "status":response.status_code})

    # Exercise the dynamic download link generated only after a completed workflow.
    criteria = '[{"name":"Quality","weight":0.5,"q":0,"p":0.2,"v":0.5,"maximize":true},{"name":"Cost","weight":0.5,"q":0,"p":0.2,"v":0.5,"maximize":false}]'
    matrix = "Asset ID,Quality,Cost\nA,0.9,0.2\nB,0.5,0.8\nC,0.7,0.4\n"
    client.post("/app/confirm-inputs", data={"criteria_mode":"json", "criteria_json":criteria})
    client.post("/app/preview", data={"matrix_csv":matrix, "header_mode":"headered", "missing_replacement":"0"})
    result = client.post("/app/compute", data={"confirm_compute":"yes"})
    match = re.search(rb'href="(/app/download/[^"]+)"', result.data)
    if match:
        path = match.group(1).decode(); response = client.get(path)
        probes.append({"kind":"dynamic-download", "path":path, "status":response.status_code,
                       "classification":"valid" if response.status_code == 200 else "broken"})
    else:
        probes.append({"kind":"dynamic-download", "path":None, "status":result.status_code,
                       "classification":"broken", "evidence":"results page lacked download href"})

    payload = {"revision":"36fce43bbb7c4075f4852b99763f2f5729710a16", "static_files":len(static_files),
               "generated_files":len(generated), "template_files":len(templates), "routes":rules,
               "counts":dict(Counter(r["classification"] for r in rows)), "references":rows, "probes":probes}
    output = ROOT/"out"/"w1-link-inventory.json"
    output.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"output":str(output.relative_to(ROOT)), "static_files":len(static_files),
                      "generated_files":len(generated), "template_files":len(templates),
                      "references":len(rows), "counts":payload["counts"], "probes":len(probes)}, indent=2))
    return 1 if payload["counts"].get("broken", 0) else 0

if __name__ == "__main__": raise SystemExit(main())
