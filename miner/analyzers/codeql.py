import json
import logging
import os
import shutil
import subprocess
import tempfile
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


def _diagnosticar_entorno() -> bool:
    if not shutil.which("codeql"):
        logger.error("codeql no encontrado en PATH")
        return False
    if not shutil.which("node"):
        logger.error("node no encontrado en PATH (requerido por CodeQL)")
        return False
    if not shutil.which("npm"):
        logger.error("npm no encontrado en PATH (requerido por CodeQL)")
        return False

    result = subprocess.run(
        ["codeql", "--version"],
        capture_output=True, text=True
    )
    logger.info(f"CodeQL version: {result.stdout.strip().splitlines()[0] if result.stdout else 'desconocida'}")

    codeql_packages = Path.home() / ".codeql" / "packages" / "codeql"
    if not codeql_packages.exists():
        logger.warning(f"Directorio de query packs no encontrado: {codeql_packages}")
    else:
        packs = list(codeql_packages.glob("*/"))
        logger.debug(f"Query packs disponibles: {[p.name for p in packs]}")

    return True


def _resolver_query_suite(lang: str) -> str:
    # Buscar suite personalizado del proyecto
    suite_file = Path(__file__).parent / f"security-extended-{lang}.qls"
    if suite_file.exists():
        return str(suite_file)

    # Fallback: buscar security-extended en ~/.codeql/packages/
    codeql_packages = Path.home() / ".codeql" / "packages" / "codeql"
    suite_pattern = f"{lang}-queries/*/codeql-suites/{lang}-security-extended.qls"
    suite_files = list(codeql_packages.glob(suite_pattern))
    if suite_files:
        return str(suite_files[0])
    return f"codeql/{lang}-queries"


def _parse_sarif(sarif_data: dict) -> dict:
    resultados = {
        "total_issues": 0,
        "issues_by_severity": {"error": 0, "warning": 0, "note": 0},
        "issues": [],
        "sarif_metadata": {
            "tool_name": "CodeQL",
            "tool_version": "",
            "language": "",
        },
    }

    for run in sarif_data.get("runs", []):
        tool = run.get("tool", {})
        driver = tool.get("driver", {})
        resultados["sarif_metadata"]["tool_version"] = driver.get("version", "")

        for resultado in run.get("results", []):
            severidad = resultado.get("level", "warning")
            if severidad not in resultados["issues_by_severity"]:
                resultados["issues_by_severity"][severidad] = 0
            resultados["issues_by_severity"][severidad] += 1
            resultados["total_issues"] += 1

            rule = resultado.get("ruleId", "")
            rule_name = ""
            if "message" in resultado and "text" in resultado["message"]:
                rule_name = resultado["message"]["text"][:100]

            primary_loc = resultado.get("locations", [{}])[0] if resultado.get("locations") else {}
            phys = primary_loc.get("physicalLocation", {})
            art = phys.get("artifactLocation", {})
            region = phys.get("region", {})

            resultados["issues"].append({
                "rule_id": rule,
                "rule_name": rule_name,
                "level": severidad,
                "message": resultado.get("message", {}).get("text", "")[:200],
                "file": art.get("uri", ""),
                "line": region.get("startLine", 0),
                "column": region.get("startColumn", 0),
            })

    return resultados


def _crear_base_datos(repo_path: str, db_path: str, codeql_lang: str) -> bool:
    create_cmd = [
        "codeql", "database", "create", db_path,
        "--language", codeql_lang,
        "--source-root", repo_path,
        "--overwrite", "--quiet",
    ]
    if codeql_lang in _CODEQL_NO_BUILD:
        create_cmd += ["--build-mode", "none"]

    logger.info(f"CodeQL: creando base de datos ({codeql_lang})...")
    r = subprocess.run(create_cmd, capture_output=True, text=True)
    if r.returncode == 0:
        return True

    if codeql_lang == "javascript":
        logger.warning(f"CodeQL create falló, reintentando con --skip-autobuild...")
        retry_cmd = create_cmd + ["--skip-autobuild"]
        r = subprocess.run(retry_cmd, capture_output=True, text=True)
        if r.returncode == 0:
            return True

    logger.error(f"CodeQL create falló ({codeql_lang}): {r.stderr.strip()[:300]}")
    return False


def run_codeql(repo_path: str, output_path: str, language: str | None = None) -> dict | None:
    if not _diagnosticar_entorno():
        return None

    codeql_lang = _resolve_language(language, repo_path)
    if not codeql_lang:
        return None

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    db_path = os.path.join(tempfile.gettempdir(), f"codeql-db-{Path(repo_path).name}")

    try:
        if not _crear_base_datos(repo_path, db_path, codeql_lang):
            return None

        query_suite = _resolver_query_suite(codeql_lang)
        threads = os.cpu_count() or 2

        analyze_cmd = [
            "codeql", "database", "analyze", db_path,
            query_suite,
            "--format", "sarif-latest",
            "--output", str(output_path),
            "--threads", str(threads),
            "--quiet",
        ]

        logger.info(f"CodeQL: analizando con {threads} threads...")
        r = subprocess.run(analyze_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            logger.error(f"CodeQL analyze falló ({codeql_lang}): {r.stderr.strip()[:300]}")
            return None

        sarif = json.loads(Path(output_path).read_text())
        resultados = _parse_sarif(sarif)
        resultados["sarif_metadata"]["language"] = codeql_lang

        normalized_path = out.with_name(f"{out.stem}_normalized.json")
        normalized_path.write_text(json.dumps(resultados, indent=2, default=str))
        logger.info(f"CodeQL: JSON normalizado guardado en {normalized_path}")

        logger.info(f"CodeQL: {resultados['total_issues']} findings")
        return resultados

    finally:
        if os.path.exists(db_path):
            shutil.rmtree(db_path, ignore_errors=True)
            logger.debug(f"CodeQL: DB eliminada ({db_path})")


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
