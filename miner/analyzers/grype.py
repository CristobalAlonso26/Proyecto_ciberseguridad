import json
import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def run_grype(sbom_path: str, output_path: str) -> dict | None:
    if not shutil.which("grype"):
        logger.error("grype no encontrado en PATH")
        return None

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = ["grype", f"sbom:{sbom_path}", "-o", f"json={output_path}"]
    logger.info(f"Ejecutando: grype sbom:...")

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        logger.error(f"Grype falló: {r.stderr.strip()[:500]}")
        return None

    data = json.loads(Path(output_path).read_text())
    matches = data.get("matches", [])
    logger.info(f"Grype: {len(matches)} vulnerabilidades encontradas")
    return data
