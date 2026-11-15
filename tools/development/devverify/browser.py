"""Optional real-browser smoke for a development branch environment.

Runs the Playwright spec named by the smoke profile against the rendered
route URL. Fails closed: a missing Playwright install, a missing browser, a
profile without a browser check, or any non-zero exit is a failure, never a pass.
"""

from __future__ import annotations

from pathlib import Path

from .config import REPO_ROOT, AppConfig, Runner, SmokeProfile, VerificationError
from .kube import run_command
from .profiles import render_profile_value

BROWSER_DIR = Path("tests") / "browser"
INSTALL_HINT = (
    "install the pinned Playwright package and browser first: "
    "`npm --prefix tests/browser install --no-save --package-lock=false --ignore-scripts` "
    "then `npx --prefix tests/browser playwright install chromium` "
    "(Chromium also needs its OS libraries; see docs/runbooks/harness-golden-path.md)"
)


def browser_url(config: AppConfig, profile: SmokeProfile) -> str:
    if profile.browser is None:
        raise VerificationError(f"app {config.app!r} has no browser smoke in its profile; refusing --browser")
    if not profile.route_urls:
        raise VerificationError(f"app {config.app!r} profile has a browser check but no routeUrls")
    return render_profile_value(profile.route_urls[0], config=config, field="routeUrls")


def preflight_browser(config: AppConfig, profile: SmokeProfile, *, repo_root: Path = REPO_ROOT) -> None:
    """Run before anything is deployed so a missing prerequisite cannot leave an environment behind."""
    browser_url(config, profile)
    playwright_bin = repo_root / BROWSER_DIR / "node_modules" / ".bin" / "playwright"
    if not playwright_bin.exists():
        raise VerificationError(f"browser smoke unverified: Playwright is not installed; {INSTALL_HINT}")
    spec = repo_root / BROWSER_DIR / "tests" / profile.browser.spec
    if not spec.is_file():
        raise VerificationError(f"browser smoke unverified: spec not found: {spec}")


def run_browser_smoke(
    config: AppConfig, profile: SmokeProfile, *, runner: Runner, repo_root: Path = REPO_ROOT
) -> None:
    url = browser_url(config, profile)
    browser = profile.browser
    assert browser is not None  # browser_url() raised otherwise
    run_command(
        # `env` carries the URL; `--no-install` stops npx from fetching a different Playwright.
        ["env", f"{browser.url_env}={url}", "npx", "--no-install", "playwright", "test", f"tests/{browser.spec}"],
        runner=runner,
        cwd=repo_root / BROWSER_DIR,
        timeout=config.timeout,
    )
