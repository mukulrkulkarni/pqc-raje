"""Validate Flask CSP response headers."""
from app import create_app
from scripts.preflight.result import CheckResult

REQUIRED = "default-src 'none'"
ROUTES = ("/", "/app/", "/docs/modules/config", "/preview/nonexistent")


def check_csp_headers(verbose: bool = False) -> CheckResult:
    """Check CSP as Flask sends it, not as templates spell it."""
    result = CheckResult("CSP response headers")
    client = create_app({"TESTING": True, "SECRET_KEY": "preflight"}).test_client()
    for route in ROUTES:
        response = client.get(route)
        header = response.headers.get("Content-Security-Policy", "")
        if REQUIRED not in header:
            result.fail(f"{route}: missing hardened CSP response header")
        elif verbose:
            result.info(f"{route}: CSP response header OK")
    return result
