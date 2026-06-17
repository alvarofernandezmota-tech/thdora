"""Cliente para la GitHub Contents API — lectura y escritura de diarios en yggdrasil-dew."""
from __future__ import annotations

import base64
import logging
from datetime import date
from functools import cached_property

from src.bot.http_client import get_client
from src.config import settings

logger = logging.getLogger(__name__)

_BASE = "https://api.github.com"


class GitHubClient:
    """Gestiona la escritura de entradas de diario en el repositorio yggdrasil-dew."""

    DIARIOS_PATH = "diarios/{date}.md"
    TOKI_SECTION = "## \ud83e\udd16 TOKI (auto)"

    @cached_property
    def _headers(self) -> dict[str, str]:
        """Cabeceras HTTP para la GitHub API, construidas una sola vez."""
        return {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _repo_url(self, path: str) -> str:
        return f"{_BASE}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/contents/{path}"

    async def get_file(self, path: str) -> tuple[str, str | None]:
        """Devuelve (contenido_decodificado, sha) del archivo, o ('', None) si no existe."""
        r = await get_client().get(self._repo_url(path), headers=self._headers)
        if r.status_code == 404:
            return "", None
        r.raise_for_status()
        data = r.json()
        return base64.b64decode(data["content"]).decode(), data["sha"]

    async def upsert_file(
        self, path: str, content: str, sha: str | None, message: str
    ) -> bool:
        """Crea o actualiza un archivo en el repo. Devuelve False en conflicto 409."""
        payload: dict = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
        }
        if sha:
            payload["sha"] = sha
        r = await get_client().put(
            self._repo_url(path), headers=self._headers, json=payload
        )
        if r.status_code == 409:
            return False
        r.raise_for_status()
        return True

    def _build_new_diario(self, today: str) -> str:
        """Genera el contenido inicial de un diario nuevo para la fecha dada."""
        return (
            f"---\ndate: {today}\ntags: [diario]\nsource: toki\n---\n\n"
            f"{self.TOKI_SECTION}\n\n## \u270d\ufe0f Manual\n"
        )

    def _inject_entry(self, body: str, entry: str) -> str:
        """Inserta la entrada en la sección TOKI del diario, creándola si no existe."""
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
        if not toki_found:
            manual_idx = next(
                (i for i, ln in enumerate(lines) if ln.strip() == "## \u270d\ufe0f Manual"),
                len(lines),
            )
            lines.insert(manual_idx, f"{self.TOKI_SECTION}\n\n")
            insert_at = manual_idx + 1
        lines.insert(insert_at, f"\n{entry.strip()}\n")
        return "".join(lines)

    async def append_to_diario(self, entry: str, user_id: int) -> bool:
        """Añade una entrada al diario del día actual. Reintenta en caso de conflicto 409."""
        today = date.today().isoformat()
        path = self.DIARIOS_PATH.format(date=today)

        body, sha = await self.get_file(path)
        if not body:
            body = self._build_new_diario(today)

        updated = self._inject_entry(body, entry)
        message = f"toki: entrada diario {today} (user {user_id})"
        ok = await self.upsert_file(path, updated, sha, message)

        if not ok:  # conflicto 409 — reintento con SHA fresco
            body, sha = await self.get_file(path)
            updated = self._inject_entry(body, entry)
            ok = await self.upsert_file(path, updated, sha, message)

        return ok


_github_client = GitHubClient()


def get_github_client() -> GitHubClient:
    """Devuelve el singleton de GitHubClient."""
    return _github_client
