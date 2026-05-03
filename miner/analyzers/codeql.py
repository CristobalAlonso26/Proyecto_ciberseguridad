import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

CODEQL_LANGUAGE_MAP = {
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "javascript",
    "Java": "java",
    "Kotlin": "java",
    "C#": "csharp",
    "Go": "go",
    "Ruby": "ruby",
    "C": "cpp",
    "C++": "cpp",
}

_CODEQL_SUPPORTED = {"python", "javascript", "java", "csharp", "go", "ruby", "cpp"}

_CODEQL_NO_BUILD = {"javascript", "python", "ruby"}


def run_codeql(repo_path: str, output_path: str, language: str | None = None) -> dict | None:
    if not shutil.which("codeql"):
        logger.error("codeql no encontrado en PATH")
        return None

    codeql_lang = _resolve_language(language, repo_path)
    if not codeql_lang:
        return None

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    db_path = out.parent / f"{out.stem}-db"

    create_cmd = [
        "codeql", "database", "create", str(db_path),
        "--language", codeql_lang,
        "--source-root", repo_path,
        "--overwrite", "--quiet",
    ]
    if codeql_lang in _CODEQL_NO_BUILD:
        create_cmd += ["--build-mode", "none"]

    logger.info(f"CodeQL: creando base de datos ({codeql_lang})...")
    r = subprocess.run(create_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        logger.error(f"CodeQL create falló ({codeql_lang}): {r.stderr.strip()[:300]}")
        return None

    analyze_cmd = [
        "codeql", "database", "analyze", str(db_path),
        f"codeql/{codeql_lang}-queries",
        "--format", "sarif-latest",
        "--output", str(output_path),
        "--quiet",
    ]

    logger.info(f"CodeQL: analizando...")
    r = subprocess.run(analyze_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        logger.error(f"CodeQL analyze falló ({codeql_lang}): {r.stderr.strip()[:300]}")
        return None

    sarif = json.loads(Path(output_path).read_text())
    results = []
    for run in sarif.get("runs", []):
        results.extend(run.get("results", []))
    logger.info(f"CodeQL: {len(results)} findings")
    return sarif


def _resolve_language(language: str | None, repo_path: str) -> str | None:
    if language:
        mapped = CODEQL_LANGUAGE_MAP.get(language)
        if mapped and mapped in _CODEQL_SUPPORTED:
            return mapped
        logger.info(f"CodeQL: lenguaje '{language}' no soportado, saltando")
        return None

    detected = _detect_language(repo_path)
    if detected:
        return detected

    logger.info("CodeQL: no se pudo detectar lenguaje soportado, saltando")
    return None


_LANG_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".java": "java",
    ".rb": "ruby",
    ".go": "go",
    ".cs": "csharp",
}


def _detect_language(repo_path: str) -> str | None:
    for dirpath, dirnames, filenames in os.walk(repo_path):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", ".venv", "__pycache__"}]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            lang = _LANG_EXTENSIONS.get(ext)
            if lang:
                return lang
    return None
