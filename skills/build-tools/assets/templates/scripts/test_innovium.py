"""Test the MCP server as Innovium would — reading everything from innovium.json."""

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PLATFORM_MAP = {
    "linux": "linux",
    "darwin": "macos",
    "win32": "windows",
}

AUTO_INJECTED = {"uv", "uvx", "npx", "node", "bun", "bunx", "docker", "python", "python3", "pip", "pipx"}


def get_platform_key() -> tuple[str, str]:
    os_key = PLATFORM_MAP.get(sys.platform, sys.platform)
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    return os_key, f"{os_key}-{arch}"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def info(msg: str) -> None:
    print(f"  {msg}")


def section(msg: str) -> None:
    print(f"\n{'='*60}\n{msg}\n{'='*60}")


def load_manifest() -> dict:
    manifest_path = Path(__file__).resolve().parent.parent / "innovium.json"
    if not manifest_path.exists():
        fail("innovium.json not found")
    return json.loads(manifest_path.read_text())


def check_command(manifest: dict) -> list[str]:
    """Check that the declared command exists. Returns the full command+args list."""
    section("1. Command resolution")

    command = manifest.get("command")
    if not command:
        transport = manifest.get("transport", "stdio")
        if transport == "stdio":
            fail("stdio transport requires 'command' but none declared")
        info(f"No command (transport={transport}) — skipping server start")
        return []

    args = manifest.get("args", [])
    full_cmd = [command] + args
    info(f"Declared command: {' '.join(full_cmd)}")

    if shutil.which(command):
        info(f"Found '{command}' in PATH")
    elif command in AUTO_INJECTED:
        info(f"'{command}' is auto-injected by Innovium — checking availability")
        if not shutil.which(command):
            fail(f"Auto-injected command '{command}' not found in PATH")
    else:
        fail(f"Command '{command}' not found in PATH and not auto-injected")

    return full_cmd


def check_dependencies(manifest: dict) -> None:
    """Check and install declared dependencies."""
    section("2. Dependency check")

    deps = manifest.get("dependencies", {}).get("runtime", [])
    if not deps:
        info("No runtime dependencies declared")
        return

    os_key, full_key = get_platform_key()
    info(f"Platform: {full_key}")

    for dep in deps:
        name = dep.get("displayName", dep.get("name", "?"))
        binary = dep.get("name", "")
        required = dep.get("required", False)
        dep_type = dep.get("type", "binary")

        found = shutil.which(binary) is not None if dep_type == "binary" else False

        if found:
            info(f"  {name}: found")
            continue

        install = dep.get("install", {})
        commands = install.get(full_key) or install.get(os_key)

        if not commands:
            hint = dep.get("hint")
            if required:
                fail(f"  {name}: MISSING (required), no install command for {full_key}")
            elif hint:
                info(f"  {name}: not found — hint: {hint}")
            else:
                info(f"  {name}: not found, no install command for {full_key} (optional, skipping)")
            continue

        for entry in commands:
            cmd = entry["command"]
            info(f"  {name}: installing — {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                if required:
                    fail(f"  {name}: install failed — {result.stderr[:500]}")
                else:
                    info(f"  {name}: install failed (optional, continuing) — {result.stderr[:200]}")
            else:
                info(f"  {name}: installed")

        if dep_type == "binary" and not shutil.which(binary):
            if required:
                fail(f"  {name}: still not found after install")
            else:
                info(f"  {name}: still not found after install (optional)")


def smoke_test_server(full_cmd: list[str]) -> dict:
    """Send initialize request using the declared command+args."""
    section("3. MCP server smoke test")

    info(f"Starting server: {' '.join(full_cmd)}")

    init_request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "innovium-ci", "version": "1.0.0"},
        },
    })

    proc = subprocess.run(
        full_cmd,
        input=init_request + "\n",
        capture_output=True,
        text=True,
        timeout=30,
    )

    if proc.returncode != 0 and proc.stderr:
        info(f"Server stderr: {proc.stderr[:500]}")

    if not proc.stdout.strip():
        fail("Server returned no output to initialize request")

    response = json.loads(proc.stdout.strip().split("\n")[0])
    if "result" not in response:
        fail(f"Unexpected response: {response}")

    result = response["result"]
    server_info = result.get("serverInfo", {})
    server_name = server_info.get("name", "unknown")
    server_version = server_info.get("version", "?")
    info(f"Server: {server_name} v{server_version}")

    capabilities = result.get("capabilities", {})
    info(f"Capabilities: {', '.join(capabilities.keys()) or 'none'}")

    return result


def list_tools(full_cmd: list[str]) -> None:
    """Send tools/list request to discover exposed tools."""
    section("4. Tool discovery")

    messages = [
        json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "innovium-ci", "version": "1.0.0"},
            },
        }),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]

    proc = subprocess.run(
        full_cmd,
        input="\n".join(messages) + "\n",
        capture_output=True,
        text=True,
        timeout=30,
    )

    if not proc.stdout.strip():
        info("Could not retrieve tool list (server may not support tools/list)")
        return

    for line in proc.stdout.strip().split("\n"):
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        if msg.get("id") == 2 and "result" in msg:
            tools = msg["result"].get("tools", [])
            info(f"Found {len(tools)} tool(s):")
            for tool in tools:
                desc = tool.get("description", "no description")
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                info(f"  - {tool['name']}: {desc}")
            return

    info("tools/list response not found in output")


def main() -> None:
    manifest = load_manifest()
    print(f"Testing: {manifest.get('name', '?')} ({manifest.get('id', '?')})")
    print(f"Platform: {sys.platform} / {platform.machine()}")

    full_cmd = check_command(manifest)
    check_dependencies(manifest)

    transport = manifest.get("transport", "stdio")
    if full_cmd and transport == "stdio":
        smoke_test_server(full_cmd)
        list_tools(full_cmd)
    elif full_cmd:
        section("3. MCP server smoke test")
        info(f"Transport is '{transport}' — skipping stdin smoke test (server uses HTTP)")

    section("Result")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
