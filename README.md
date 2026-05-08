# Security Vulnerability Analysis Pipeline

Leonardo Castellón - Cristobal Ramos

Pipeline E2E para análisis de seguridad de repositorios:

**Miner → Analyzer → Visualizer**

- **Miner**: extrae repos de una organización GitHub, los clona y ejecuta **CodeQL**, **Syft** y **Grype**.
- **Analyzer**: consolida resultados y genera `data/results/analysis.json` (incluye SBOM, vulnerabilidades, CodeQL y CI/CD).
- **Visualizer**: dashboard Angular que consume `analysis.json` desde `visualizer/src/assets/analysis.json`.

## Inicio rápido

> El flujo E2E se ejecuta **por etapas secuenciales**: **Miner → Analyzer → Visualizer**.

### Opción 1: Docker Compose (recomendado)

**1) Configurar entorno**

```bash
cp .env.example .env
# Editar .env y poner tu GITHUB_TOKEN
```

**2) Ejecutar Miner (genera datos crudos)**

```bash
docker compose run --rm miner
```

**3) Ejecutar Analyzer (genera `analysis.json`)**

```bash
docker compose up analyzer
```

**4) Ejecutar Visualizer (consume `analysis.json`)**

```bash
docker compose up visualizer
```

**5) Validación mínima**

```bash
jq '.metadata' data/results/analysis.json
jq '.repositories | length' data/results/analysis.json
```

Notas:
- Al iniciar, el servicio `analyzer` genera `analysis.json` y ejecuta los 3 notebooks (`nbconvert --execute`) para dejarlos con outputs listos.
- El servicio `visualizer` sincroniza automáticamente `analysis.json` hacia `visualizer/src/assets/` en cada arranque.

### Opción 2: Dev Container

Abre el proyecto en VS Code y ejecuta `Dev Containers: Reopen in Container`.

**Dentro del contenedor, ejecutar secuencialmente:**

```bash
cp .env.example .env
# Editar .env y poner tu GITHUB_TOKEN

uv sync
uv run python -m miner
uv run python analyzer/generate_analysis.py
./scripts/prepare_visualizer_data.sh
cd visualizer && npm install && npm run start
```

### Opción 3: Ejecución local

#### Requisitos

- **Python 3.11+**
- **Git**, **Syft**, **Grype**, **CodeQL CLI** instalados en el PATH
- **GitHub Personal Access Token** con scopes `public_repo` y `read:org`

#### Pasos

**1. Configurar**

```bash
cp .env.example .env
# Editar .env y poner tu GITHUB_TOKEN
```

**2. Instalar dependencias**

```bash
uv sync
```

**3. Ejecutar Miner (datos crudos)**

```bash
# Probar sin clonar (solo lista repos)
uv run python -m miner --dry-run

# Ejecución completa
uv run python -m miner
```

Los resultados se guardan en `data/results/` y `data/reports/`.

**4. Ejecutar Analyzer (consolidación)**

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

**5. Preparar y ejecutar Visualizer**

```bash
./scripts/prepare_visualizer_data.sh
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
