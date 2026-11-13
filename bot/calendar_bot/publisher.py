"""Publishing of data/events.json through git (ADR 0009)."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Awaitable, Callable, Optional, Set, Tuple

logger = logging.getLogger(__name__)

RETRY_INTERVAL_SECONDS = 60
GIT_TIMEOUT_SECONDS = 120
MAX_RACE_RETRIES = 3
CONFLICT_MESSAGE = (
    "No he podido publicar tus cambios en el calendario porque hay un conflicto en el repositorio. "
    "Hace falta resolverlo a mano en la Raspberry Pi."
)


class Publisher:
    def __init__(
        self,
        repo_dir: Path,
        events_file: str = "data/events.json",
        notify: Optional[Callable[[str], Awaitable[None]]] = None,
    ):
        self.repo_dir = repo_dir
        self.events_file = events_file
        self._notify = notify
        self._lock = asyncio.Lock()
        self._conflict_notified = False
        self._tasks: Set["asyncio.Task[None]"] = set()

    async def publish(self, message: str) -> None:
        """Commit the events file locally and push it in the background."""
        await self._git("add", self.events_file)
        code, _ = await self._git("diff", "--cached", "--quiet")
        if code != 0:
            code, output = await self._git("commit", "-m", message)
            if code != 0:
                logger.error("git commit failed: %s", output)
                raise RuntimeError("git commit failed")
        task = asyncio.create_task(self.sync())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def retry_forever(self, interval: float = RETRY_INTERVAL_SECONDS) -> None:
        while True:
            await asyncio.sleep(interval)
            try:
                if await self._has_pending():
                    await self.sync()
            except Exception:
                logger.exception("Publication retry failed")

    async def sync(self) -> bool:
        """Pull with rebase and push. Returns True when everything is published."""
        async with self._lock:
            for _ in range(MAX_RACE_RETRIES):
                code, output = await self._git("pull", "--rebase")
                if code != 0:
                    abort_code, _ = await self._git("rebase", "--abort")
                    if abort_code == 0:
                        await self._report_conflict()
                    else:
                        logger.warning("git pull failed: %s", output)
                    return False
                code, output = await self._git("push")
                if code == 0:
                    self._conflict_notified = False
                    return True
                if not _is_rejected(output):
                    logger.warning("git push failed: %s", output)
                    return False
            return False

    async def _report_conflict(self) -> None:
        logger.error("Rebase conflict while publishing")
        if not self._conflict_notified and self._notify:
            self._conflict_notified = True
            await self._notify(CONFLICT_MESSAGE)

    async def _has_pending(self) -> bool:
        code, output = await self._git("rev-list", "--count", "@{u}..HEAD")
        return code == 0 and output.strip() not in ("", "0")

    async def _git(self, *args: str) -> Tuple[int, str]:
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        process = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=str(self.repo_dir),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), GIT_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return 1, "timeout"
        return process.returncode or 0, stdout.decode(errors="replace")


def _is_rejected(output: str) -> bool:
    return "rejected" in output or "fetch first" in output or "non-fast-forward" in output
