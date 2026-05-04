# Security Vulnerability Analysis Pipeline

Pipeline E2E para análisis de seguridad de repositorios:

**Miner → Analyzer → Visualizer**

- **Miner**: extrae repos de una organización GitHub, los clona y ejecuta **CodeQL**, **Syft** y **Grype**.
- **Analyzer**: consolida resultados y genera `data/results/analysis.json` (incluye SBOM, vulnerabilidades, CodeQL y CI/CD).
- **Visualizer**: dashboard Angular que consume `analysis.json` desde `visualizer/src/assets/analysis.json`.

## Requisitos

- **Python 3.11+**
- **Git**, **Syft**, **Grype**, **CodeQL CLI** instalados en el PATH (o usar Dev Container)
- **GitHub Personal Access Token** con scopes `public_repo` y `read:org`

## Inicio rápido (flujo E2E)

### 1. Configurar

```bash
cp .env.example .env
# Editar .env y poner tu GITHUB_TOKEN
```

### 2. Instalar dependencias

```bash
uv sync
```

### 3. Ejecutar Miner

```bash
# Probar sin clonar (solo lista repos)
uv run python -m miner --dry-run

# Ejecución completa
uv run python -m miner
```

Los resultados se guardan en `data/results/` y `data/reports/`.

### 4. Ejecutar Analyzer

```bash
uv run python analyzer/generate_analysis.py
```

Notas:
- El Analyzer genera `data/results/analysis.json` en cada ejecución.
- Si el contenido del análisis no cambia (ignorando `metadata.generated_at`), se omite la ejecución de notebooks.
- Si cambia, ejecuta en orden `nbs/01_overview.ipynb`, `nbs/02_vulnerability_patterns.ipynb` y `nbs/03_repository_risk_and_conclusions.ipynb`.
- Si `jupyter` no está disponible en el entorno, se muestra advertencia y **no** se interrumpe la generación de `analysis.json`.

Validación rápida:

```bash
jq '.metadata' data/results/analysis.json
jq '.cross_repo_analysis' data/results/analysis.json
```

### 5. Ejecutar Visualizer

```bash
cd visualizer
npm install
npm run start
```

El dashboard queda disponible en `http://localhost:4200/`.

> **Nota:** En Docker Compose, `analysis.json` se sincroniza automáticamente desde `data/results/analysis.json` hacia `visualizer/src/assets/analysis.json` en cada arranque del servicio `visualizer`. En ejecución local, ejecuta `./scripts/prepare_visualizer_data.sh` manualmente.

---

## Opciones del CLI

| Flag | Descripción | Default |
|---|---|---|
| `--org NAME` | Organización GitHub | `GITHUB_ORG` del .env |
| `--workers N` | Workers para clonado | `3` |
| `--analysis-workers N` | Workers para análisis | `2` |
| `--visibility CHOICE` | `all`, `public`, `private`, `internal` | `public` |
| `--limit N` | Máximo de repos | `50` |
| `--recent-days N` | Días de actividad | `30` |
| `--dry-run` | Solo listar repos | — |
| `--output-json PATH` | Guardar resumen en JSON | — |
| `-v` | Logging DEBUG | — |

## Usar con Dev Container

Si no quieres instalar las herramientas manualmente, abre el proyecto en VS Code y ejecuta `Dev Containers: Reopen in Container`. Esto instala CodeQL, Syft y Grype automáticamente.

```bash
# Dentro del contenedor
uv sync
uv run python -m miner
uv run python analyzer/generate_analysis.py
```

## Usar con Docker Compose

```bash
docker compose run --rm miner
docker compose up analyzer       # Jupyter Lab en http://localhost:8888
docker compose up visualizer     # Dashboard en http://localhost:4200
```

> El servicio `visualizer` sincroniza automáticamente `analysis.json` en cada arranque hacia `src/assets/`. No es necesario ejecutar el script manualmente cuando usas Docker Compose.

## Estructura

```
├── miner/
│   ├── __main__.py          # CLI entrypoint
│   ├── models.py            # Repository dataclass
│   ├── github_client.py     # GitHub API client
│   ├── clone.py             # git clone
│   ├── pipeline.py          # Pipeline con ThreadPoolExecutor
│   └── analyzers/
│       ├── syft.py          # Generación de SBOM
│       ├── grype.py         # Escaneo de vulnerabilidades
│       └── codeql.py        # Análisis estático de código
├── data/
│   ├── repos/               # Repositorios clonados
│   ├── results/             # SBOMs, vulns y analysis.json
│   └── reports/             # Reportes CodeQL SARIF y CI/CD
├── analyzer/
│   ├── generate_analysis.py # Genera data/results/analysis.json
│   └── ...                  # Parsers y agregación
├── visualizer/              # Dashboard Angular
├── scripts/
│   └── prepare_visualizer_data.sh
├── docker-compose.yml
├── .devcontainer/
└── pyproject.toml
```

## Configuración

| Variable | Default | Descripción |
|---|---|---|
| `GITHUB_TOKEN` | **requerido** | PAT con `public_repo`, `read:org` |
| `GITHUB_ORG` | **requerido** | Slug de la organización |
| `REPO_LIMIT` | `50` | Máximo de repos a analizar |
| `REPO_VISIBILITY` | `public` | Visibilidad de repos |
| `CLONE_WORKERS` | `3` | Workers para clonado |
