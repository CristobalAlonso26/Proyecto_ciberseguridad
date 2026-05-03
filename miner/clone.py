import logging
import os
import subprocess
from pathlib import Path

from .models import Repository

logger = logging.getLogger(__name__)


def clone_repo(repo: Repository, clone_root: Path, token: str, depth: int | None = None) -> str:
    dest = clone_root / repo.org_name / repo.name
    clone_url = _auth_url(repo.clone_url, token)

    if (dest / ".git").exists():
        logger.info(f"[{repo.full_name}] Actualizando...")
        _run(["git", "-C", str(dest), "fetch", "--all", "--prune", "--quiet"])
    else:
        logger.info(f"[{repo.full_name}] Clonando...")
        dest.mkdir(parents=True, exist_ok=True)
        cmd = ["git", "clone", "--quiet"]
        if depth is not None:
            cmd += ["--depth", str(depth)]
        cmd += [clone_url, str(dest)]
        _run(cmd)

    sha = _run(["git", "-C", str(dest), "rev-parse", "HEAD"]).strip()
    return str(dest)


def _auth_url(clone_url: str, token: str) -> str:
    return clone_url.replace("https://", f"https://x-access-token:{token}@")


def _run(cmd: list[str]) -> str:
    safe = [c if "x-access-token" not in c else "***" for c in cmd]
    logger.debug(f"$ {' '.join(safe)}")
    r = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    if r.returncode != 0:
        raise RuntimeError(f"git falló: {r.stderr.strip()[:500]}")
    return r.stdout
