import json
import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run_syft(repo_path: str, output_path: str) -> dict | None:
    if not shutil.which("syft"):
        logger.error("syft no encontrado en PATH")
        return None

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = ["syft", f"dir:{repo_path}", "-o", f"json={output_path}"]
    logger.info(f"Ejecutando: {' '.join(cmd[:3])}...")

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        logger.error(f"Syft falló: {r.stderr.strip()[:500]}")
        return None

    data = json.loads(Path(output_path).read_text())
    components = data.get("artifacts", [])
    logger.info(f"SBOM generado: {len(components)} componentes")
    return data
