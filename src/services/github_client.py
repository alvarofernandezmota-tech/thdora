import base64
import logging
from datetime import date

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

_BASE = "https://api.github.com"


class GitHubClient:
    DIARIOS_PATH = "diarios/{date}.md"
    TOKI_SECTION = "## 🤖 TOKI (auto)"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _repo_url(self, path: str) -> str:
        return f"{_BASE}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/contents/{path}"

    async def get_file(self, path: str) -> tuple[str, str | None]:
        async with httpx.AsyncClient() as client:
            r = await client.get(self._repo_url(path), headers=self._headers())
        if r.status_code == 404:
            return "", None
        r.raise_for_status()
        data = r.json()
        content = base64.b64decode(data["content"]).decode()
        return content, data["sha"]

    async def upsert_file(
        self, path: str, content: str, sha: str | None, message: str
    ) -> bool:
        payload: dict = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
        }
        if sha:
            payload["sha"] = sha
        async with httpx.AsyncClient() as client:
            r = await client.put(
                self._repo_url(path), headers=self._headers(), json=payload
            )
        if r.status_code == 409:
            return False
        r.raise_for_status()
        return True

    def _build_new_diario(self, today: str) -> str:
        return (
            f"---\ndate: {today}\ntags: [diario]\nsource: toki\n---\n\n"
            f"{self.TOKI_SECTION}\n\n## ✍️ Manual\n"
        )

    def _inject_entry(self, body: str, entry: str) -> str:
        lines = body.splitlines(keepends=True)
        insert_at = len(lines)
        toki_found = False
        for i, line in enumerate(lines):
            if line.strip() == self.TOKI_SECTION:
                toki_found = True
                continue
            if toki_found and line.startswith("## ") and line.strip() != self.TOKI_SECTION:
                insert_at = i
                break
        formatted = f"\n{entry.strip()}\n"
        lines.insert(insert_at, formatted)
        return "".join(lines)

    async def append_to_diario(self, entry: str, user_id: int) -> bool:
        today = date.today().isoformat()
        path = self.DIARIOS_PATH.format(date=today)

        body, sha = await self.get_file(path)
        if not body:
            body = self._build_new_diario(today)

        updated = self._inject_entry(body, entry)
        message = f"toki: entrada diario {today} (user {user_id})"
        ok = await self.upsert_file(path, updated, sha, message)

        if not ok:
            body, sha = await self.get_file(path)
            updated = self._inject_entry(body, entry)
            ok = await self.upsert_file(path, updated, sha, message)

        return ok
