import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .pipeline import Pipeline


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_args() -> argparse.Namespace:
    default_limit = int(os.environ.get("REPO_LIMIT", "50"))
    p = argparse.ArgumentParser(description="Security Vulnerability Analysis Pipeline — Miner")
    p.add_argument("--org", help="Organización GitHub")
    p.add_argument("--workers", type=int, default=3, help="Workers para clonado (default: 3)")
    p.add_argument("--analysis-workers", type=int, default=2, help="Workers para análisis (default: 2)")
    p.add_argument("--visibility", choices=["all", "public", "private", "internal"], default="public")
    p.add_argument("--limit", type=int, default=default_limit, help=f"Máximo de repos (default: {default_limit})")
    p.add_argument("--recent-days", type=int, default=30, help="Días de actividad (default: 30)")
    p.add_argument("--dry-run", action="store_true", help="Solo listar repos")
    p.add_argument("--keep-repos", action="store_true", help="No eliminar repos clonados después del análisis")
    p.add_argument("--output-json", type=Path, help="Guardar resumen en JSON")
    p.add_argument("-v", "--verbose", action="store_true", help="Logging DEBUG")
    return p.parse_args()


def run() -> None:
    load_dotenv()
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger("miner")

    project_root = Path(__file__).resolve().parent.parent

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        logger.error("Se requiere GITHUB_TOKEN o GH_TOKEN")
        sys.exit(1)

    org = args.org or os.environ.get("GITHUB_ORG")
    if not org:
        logger.error("Se requiere GITHUB_ORG")
        sys.exit(1)

    if args.dry_run:
        from .github_client import GitHubClient
        client = GitHubClient(token)
        repos = client.fetch_active_repos(org, args.visibility, args.limit, args.recent_days)
        for r in repos:
            print(f"  {r.full_name} ({r.language or '?'})")
        print(f"\nTotal: {len(repos)} repos")
        return

    pipeline = Pipeline(
        token=token,
        org=org,
        clone_root=os.environ.get("REPOS_ROOT", str(project_root / "data" / "repos")),
        results_root=os.environ.get("RESULTS_ROOT", str(project_root / "data" / "results")),
        reports_root=os.environ.get("REPORTS_ROOT", str(project_root / "data" / "reports")),
        visibility=args.visibility,
        limit=args.limit,
        recent_days=args.recent_days,
        clone_workers=args.workers,
        analysis_workers=args.analysis_workers,
        keep_repos=args.keep_repos,
    )

    summary = pipeline.run()

    print("\n" + "=" * 55)
    print("RESUMEN DEL PIPELINE")
    print("=" * 55)
    print(f"  {'repos_encontrados':<22} {summary['repos']}")
    print(f"  {'repos_clonados':<22} {summary['cloned']}")
    for r in summary.get("results", []):
        print(f"  {r['repo']:<22} deps={r['sbom_components']} vulns={r.get('vuln_count', 0)} codeql={r['codeql_findings']} cicd={r.get('cicd_findings', 0)}")
    print("=" * 55)

    if args.output_json:
        args.output_json.write_text(json.dumps(summary, indent=2, default=str))
        logger.info(f"Resumen guardado en: {args.output_json}")


if __name__ == "__main__":
    run()
