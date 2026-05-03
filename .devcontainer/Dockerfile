# ============================================================
# Security Vulnerability Analysis Pipeline — Dev Container Image
# ============================================================
# Combina lo mejor de ambos proyectos de referencia:
# - ciberseguridad_2026: herramientas preinstaladas y verificadas
# - Gape-mol/Proyecto-CiberSeg: estructura multi-servicio con volumes
# ============================================================

FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

LABEL maintainer="Security Pipeline Team"
LABEL description="Dev Container para analisis de vulnerabilidades (CodeQL, Syft, Grype)"

ARG DEBIAN_FRONTEND=noninteractive

# ----------------------------------------------------------
# 1. Instalar uv (gestor de dependencias Python rapido)
# ----------------------------------------------------------
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ----------------------------------------------------------
# 2. Instalar Syft (generador de SBOMs)
# ----------------------------------------------------------
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
    | sh -s -- -b /usr/local/bin

# ----------------------------------------------------------
# 3. Instalar Grype (escaner de vulnerabilidades en dependencias)
# ----------------------------------------------------------
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh \
    | sh -s -- -b /usr/local/bin

# ----------------------------------------------------------
# 4. Instalar Node.js 20 (requerido para analisis JS/TS con CodeQL)
# ----------------------------------------------------------
RUN rm -f /etc/apt/sources.list.d/yarn.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------
# 5. Instalar CodeQL CLI
# ----------------------------------------------------------
ARG CODEQL_VERSION=2.25.3
RUN curl -sSfL "https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/codeql-linux64.zip" \
    -o /tmp/codeql.zip \
    && unzip -q /tmp/codeql.zip -d /usr/local \
    && chmod +x /usr/local/codeql/codeql \
    && ln -s /usr/local/codeql/codeql /usr/local/bin/codeql \
    && rm /tmp/codeql.zip

# ----------------------------------------------------------
# 6. Pre-descargar query packs de CodeQL
# ----------------------------------------------------------
RUN codeql pack download codeql/python-queries \
    && codeql pack download codeql/javascript-queries \
    && codeql pack download codeql/java-queries \
    || echo "Nota: Algunos query packs pueden no estar disponibles offline."

# ----------------------------------------------------------
# 7. Configurar Git para directorios de repos
# ----------------------------------------------------------
RUN git config --system --add safe.directory '*'

# ----------------------------------------------------------
# 8. Verificar todas las herramientas instaladas
# ----------------------------------------------------------
RUN echo "=== Verificacion de herramientas ===" \
    && echo "Python: $(python3 --version)" \
    && echo "uv: $(uv --version)" \
    && echo "Node.js: $(node --version)" \
    && echo "npm: $(npm --version)" \
    && echo "CodeQL: $(codeql version)" \
    && echo "Syft: $(syft --version)" \
    && echo "Grype: $(grype version)" \
    && echo "Git: $(git --version)" \
    && echo "=== Verificacion completa ==="

# ----------------------------------------------------------
# 9. Variables de entorno
# ----------------------------------------------------------
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace
