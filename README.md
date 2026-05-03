# Security Vulnerability Analysis Pipeline

Extrae repos de una organización GitHub, los clona y ejecuta **CodeQL**, **Syft** y **Grype** en paralelo.

## Requisitos

- **Python 3.11+**
- **Git**, **Syft**, **Grype**, **CodeQL CLI** instalados en el PATH (o usar Dev Container)
- **GitHub Personal Access Token** con scopes `public_repo` y `read:org`

## Inicio rápido

### 1. Configurar

```bash
cp .env.example .env
# Editar .env y poner tu GITHUB_TOKEN
```

### 2. Instalar dependencias

```bash
uv sync
```

### 3. Ejecutar

```bash
# Probar sin clonar (solo lista repos)
python -m miner --dry-run

# Ejecución completa
python -m miner
```

Los resultados se guardan en `data/results/` y `data/reports/`.

---

## Opciones del CLI

| Flag | Descripción | Default |
|---|---|---|
| `--org NAME` | Organización GitHub | `GITHUB_ORG` del .env |
| `--workers N` | Workers para clonado | `3` |
| `--analysis-workers N` | Workers para análisis | `2` |
| `--depth N` | Profundidad del clone (0=completo) | `none` |
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
python -m miner
```

## Usar con Docker Compose

```bash
docker compose run --rm miner
docker compose up analyzer        # Jupyter Lab en :8888
docker compose up visualizer      # Dashboard en :4173
```

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
│   ├── results/             # Resultados Syft/Grype
│   └── reports/             # Reportes CodeQL SARIF
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
