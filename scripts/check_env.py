import sys

import httpx

from src.config import settings

PLACEHOLDER_PREFIXES = ("ghp_...", "your_", "changeme", "xxx", "")

Results: list[tuple[bool, str]] = []


def ok(msg: str) -> None:
    Results.append((True, f"✅ {msg}"))


def fail(msg: str) -> None:
    Results.append((False, f"❌ {msg}"))


def is_placeholder(value: str) -> bool:
    return not value or any(value.startswith(p) for p in PLACEHOLDER_PREFIXES)


def check_tokens() -> None:
    for name, value in [
        ("TELEGRAM_BOT_TOKEN", settings.TELEGRAM_BOT_TOKEN),
        ("GROQ_API_KEY", settings.GROQ_API_KEY),
        ("GITHUB_TOKEN", settings.GITHUB_TOKEN),
    ]:
        if is_placeholder(value):
            fail(f"{name:<22} — Placeholder detectado")
        else:
            ok(f"{name:<22} — OK")


def check_groq() -> None:
    try:
        r = httpx.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            timeout=5.0,
        )
        if r.status_code == 200:
            count = len(r.json().get("data", []))
            ok(f"{'GROQ_API_KEY':<22} — OK (models: {count})")
        else:
            fail(f"{'GROQ_API_KEY':<22} — HTTP {r.status_code}")
    except Exception as e:
        fail(f"{'GROQ_API_KEY':<22} — Error: {e}")


def check_github() -> None:
    try:
        r = httpx.get(
            f"https://api.github.com/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}",
            headers={
                "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            },
            timeout=5.0,
        )
        if r.status_code == 200:
            repo = r.json().get("name", settings.GITHUB_REPO)
            ok(f"{'GITHUB_TOKEN':<22} — OK (repo: {repo})")
        else:
            fail(f"{'GITHUB_TOKEN':<22} — HTTP {r.status_code}")
    except Exception as e:
        fail(f"{'GITHUB_TOKEN':<22} — Error: {e}")


def check_api_health() -> None:
    import os
    base = os.environ.get("THDORA_API_URL", "http://localhost:8001")
    try:
        r = httpx.get(f"{base}/health", timeout=3.0)
        if r.status_code == 200:
            ok(f"{'API health':<22} — OK")
        else:
            fail(f"{'API health':<22} — HTTP {r.status_code}")
    except Exception as e:
        fail(f"{'API health':<22} — Error: {e}")


if __name__ == "__main__":
    check_tokens()
    check_groq()
    check_github()
    check_api_health()

    print("\n── Entorno THDORA ──────────────────────────")
    for _, msg in Results:
        print(msg)
    print("────────────────────────────────────────────\n")

    if any(not passed for passed, _ in Results):
        sys.exit(1)
