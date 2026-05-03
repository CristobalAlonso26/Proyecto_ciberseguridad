import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def scan_workflow(file_path: str) -> list[str]:
    issues = []
    try:
        with open(file_path, "r") as f:
            workflow = yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"No se pudo parsear {file_path}: {e}")
        return issues

    if not isinstance(workflow, dict):
        return issues

    jobs = workflow.get("jobs", {})
    if not isinstance(jobs, dict):
        return issues

    for job_name, job_def in jobs.items():
        if not isinstance(job_def, dict):
            continue

        steps = job_def.get("steps", [])
        if not isinstance(steps, list):
            continue

        for step in steps:
            if not isinstance(step, dict):
                continue
            run_cmd = step.get("run", "")
            if not isinstance(run_cmd, str):
                continue

            if "npm install" in run_cmd and "npm ci" not in run_cmd:
                issue = f"Job '{job_name}': usa 'npm install' en vez de 'npm ci' (dependencias no deterministas)"
                if issue not in issues:
                    issues.append(issue)

    permissions = workflow.get("permissions")
    if permissions == "write-all":
        issues.append("Permisos excesivos: 'permissions: write-all'")
    elif isinstance(permissions, dict):
        if permissions.get("contents") == "write":
            issues.append("Permiso 'contents: write' innecesario")

    return issues


def run_cicd_scan(repo_path: str, repo_name: str) -> dict:
    workflows_dir = Path(repo_path) / ".github" / "workflows"
    result = {
        "repo": repo_name,
        "workflows_scanned": 0,
        "findings": [],
    }

    if not workflows_dir.exists():
        logger.info(f"[{repo_name}] No se encontraron workflows de CI/CD")
        return result

    yml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not yml_files:
        logger.info(f"[{repo_name}] No hay archivos .yml/.yaml en workflows")
        return result

    logger.info(f"[{repo_name}] Escaneando {len(yml_files)} workflows de CI/CD...")
    result["workflows_scanned"] = len(yml_files)

    for wf_path in yml_files:
        issues = scan_workflow(str(wf_path))
        if issues:
            result["findings"].append({
                "workflow": wf_path.name,
                "issues": issues,
            })

    total_issues = sum(len(f["issues"]) for f in result["findings"])
    logger.info(f"[{repo_name}] CI/CD: {total_issues} hallazgos en {len(result['findings'])} workflows")
    return result
