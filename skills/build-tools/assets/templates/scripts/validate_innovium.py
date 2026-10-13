"""Validate innovium.json against the Innovium manifest spec."""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["id", "name", "description", "category"]

STANDARD_CATEGORIES = [
    "development",
    "version-control",
    "communication",
    "data",
    "knowledge",
    "productivity",
    "project",
    "ai",
    "cloud",
    "simulation",
    "other",
]

VALID_TRANSPORTS = ["stdio", "streamable-http", "sse"]

VALID_PLATFORMS = [
    "macos-arm64",
    "macos-x64",
    "linux-x64",
    "linux-arm64",
    "windows-x64",
    "windows-arm64",
]

VALID_DEP_TYPES = ["binary", "npm", "pip", "system"]

VALID_ENV_TYPES = ["string", "number", "boolean", "url", "path"]

ICON_NAMES = ["icon.png", "icon.jpg", "icon.svg"]


def error(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr)


def validate(manifest: dict, repo_root: Path) -> list[str]:
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    if "id" in manifest:
        id_val = manifest["id"]
        if not isinstance(id_val, str) or id_val != id_val.lower() or " " in id_val:
            errors.append(f"id must be lowercase kebab-case, got: {id_val!r}")

    if "category" in manifest:
        cat = manifest["category"]
        if cat not in STANDARD_CATEGORIES:
            warn(f"Non-standard category: {cat!r} (will be grouped under 'Other')")

    transport = manifest.get("transport", "stdio")
    if transport not in VALID_TRANSPORTS:
        errors.append(f"Invalid transport: {transport!r}")

    if transport == "stdio" and "command" not in manifest:
        errors.append("stdio transport requires 'command' field")

    if transport in ("streamable-http", "sse") and "url" not in manifest:
        errors.append(f"{transport} transport requires 'url' field")

    if "platforms" in manifest:
        for p in manifest["platforms"]:
            if p not in VALID_PLATFORMS:
                errors.append(f"Invalid platform: {p!r}")

    if "env" in manifest:
        for i, env_var in enumerate(manifest["env"]):
            prefix = f"env[{i}]"
            for field in ["name", "displayName", "type"]:
                if field not in env_var:
                    errors.append(f"{prefix}: missing required field '{field}'")
            if "type" in env_var and env_var["type"] not in VALID_ENV_TYPES:
                errors.append(f"{prefix}: invalid type {env_var['type']!r}")

    if "dependencies" in manifest:
        runtime = manifest["dependencies"].get("runtime", [])
        for i, dep in enumerate(runtime):
            prefix = f"dependencies.runtime[{i}]"
            for field in ["type", "name", "displayName"]:
                if field not in dep:
                    errors.append(f"{prefix}: missing required field '{field}'")
            if "type" in dep and dep["type"] not in VALID_DEP_TYPES:
                errors.append(f"{prefix}: invalid type {dep['type']!r}")

    if not any((repo_root / name).exists() for name in ICON_NAMES):
        warn("No icon file found (icon.png/jpg/svg). A default icon will be used.")

    if not (repo_root / "LICENSE").exists() and not (repo_root / "LICENSE.md").exists():
        warn("No LICENSE file found.")

    return errors


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = repo_root / "innovium.json"

    if not manifest_path.exists():
        error("innovium.json not found in repo root")
        sys.exit(1)

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in innovium.json: {e}")
        sys.exit(1)

    errors = validate(manifest, repo_root)

    if errors:
        for e in errors:
            error(e)
        sys.exit(1)

    print(f"innovium.json is valid: {manifest.get('name', '?')} ({manifest.get('id', '?')})")


if __name__ == "__main__":
    main()
