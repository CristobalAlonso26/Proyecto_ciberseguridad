import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Analysis, CicdRow, ValidationMetadata, VulnerabilityRow } from './models/analysis.model';
import { AnalysisDataService } from './services/analysis-data.service';
import { KpiCardsComponent } from './components/kpi-cards/kpi-cards.component';
import { SeverityChartComponent } from './components/severity-chart/severity-chart.component';
import { RepoRiskRankingComponent } from './components/repo-risk-ranking/repo-risk-ranking.component';
import { RepoComparisonChartComponent } from './components/repo-comparison-chart/repo-comparison-chart.component';
import { VulnerabilitiesTableComponent } from './components/vulnerabilities-table/vulnerabilities-table.component';
import { CicdFindingsTableComponent } from './components/cicd-findings-table/cicd-findings-table.component';
import { ValidationStatusComponent } from './components/validation-status/validation-status.component';
import { CodeqlLevelSummaryComponent } from './components/codeql-level-summary/codeql-level-summary.component';
import { CweRankingComponent } from './components/cwe-ranking/cwe-ranking.component';
import { ArtifactTypeHeatmapComponent } from './components/artifact-type-heatmap/artifact-type-heatmap.component';
import { SeverityPyramidComponent } from './components/severity-pyramid/severity-pyramid.component';
import { KeyFindingsComponent, KeyFinding } from './components/key-findings/key-findings.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    KpiCardsComponent,
    SeverityChartComponent,
    RepoRiskRankingComponent,
    RepoComparisonChartComponent,
    VulnerabilitiesTableComponent,
    CicdFindingsTableComponent,
    ValidationStatusComponent,
    CodeqlLevelSummaryComponent,
    CweRankingComponent,
    ArtifactTypeHeatmapComponent,
    SeverityPyramidComponent,
    KeyFindingsComponent,
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  loading = true;
  error = '';
  analysis: Analysis | null = null;
  refreshState: 'idle' | 'updated' | 'error' = 'idle';

  selectedRepository = 'all';
  selectedAnalysisTypes: Array<'dependency' | 'codeql' | 'cicd'> = ['dependency', 'codeql', 'cicd'];
  enabledSeverities: string[] = ['Critical', 'High', 'Medium', 'Low', 'Unknown'];

  constructor(private readonly analysisService: AnalysisDataService) {}

  ngOnInit(): void {
    this.analysisService.refreshState$.subscribe((state) => {
      this.refreshState = state;
    });

    this.analysisService.getAnalysis().subscribe({
      next: (data) => {
        this.analysis = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = `No se pudo cargar assets/analysis.json (${err.status || 'error'}).`;
        this.loading = false;
      },
    });
  }

  get availableRepositories(): string[] {
    return (this.analysis?.repositories ?? []).map((repo) => repo.name).sort((a, b) => a.localeCompare(b));
  }

  get knownSeverities(): string[] {
    return ['Critical', 'High', 'Medium', 'Low', 'Unknown'];
  }

  toggleAnalysisType(type: 'dependency' | 'codeql' | 'cicd'): void {
    if (this.selectedAnalysisTypes.includes(type)) {
      if (this.selectedAnalysisTypes.length > 1) {
        this.selectedAnalysisTypes = this.selectedAnalysisTypes.filter((item) => item !== type);
      }
      return;
    }
    this.selectedAnalysisTypes = [...this.selectedAnalysisTypes, type];
  }

  toggleSeverity(severity: string): void {
    if (this.enabledSeverities.includes(severity)) {
      if (this.enabledSeverities.length > 1) {
        this.enabledSeverities = this.enabledSeverities.filter((value) => value !== severity);
      }
      return;
    }
    this.enabledSeverities = [...this.enabledSeverities, severity];
  }

  refreshData(): void {
    this.analysisService.forceRefresh();
  }

  hasType(type: 'dependency' | 'codeql' | 'cicd'): boolean {
    return this.selectedAnalysisTypes.includes(type);
  }

  get filteredRepositories(): Analysis['repositories'] {
    if (!this.analysis) return [];
    return this.analysis.repositories.filter((repo) => this.selectedRepository === 'all' || repo.name === this.selectedRepository);
  }

  get isEmpty(): boolean {
    return !this.analysis || !this.analysis.repositories?.length;
  }

  get kpis() {
    if (!this.analysis) return [];
    const repos = this.filteredRepositories;
    const avgRisk = repos.length
      ? repos.reduce((acc, repo) => acc + repo.metrics.risk_score, 0) /
        repos.length
      : 0;

    return [
      { label: 'Repos analizados', value: repos.length, subtitle: 'Repositorios visibles por filtros', accent: 'cyan' },
      { label: 'Componentes', value: repos.reduce((a, r) => a + (r.sbom.total_components ?? 0), 0), subtitle: 'Inventario consolidado SBOM', accent: 'teal' },
      { label: 'Vulnerabilidades', value: repos.reduce((a, r) => a + this.repoVulnerabilities(r), 0), subtitle: 'Detectadas por Grype', accent: 'red' },
      { label: 'Issues CodeQL', value: this.hasType('codeql') ? repos.reduce((a, r) => a + (r.codeql.total_issues ?? 0), 0) : 0, subtitle: 'Hallazgos de análisis estático', accent: 'amber' },
      { label: 'Hallazgos CI/CD', value: this.totalCicdFindings, subtitle: 'Workflows y prácticas inseguras', accent: 'amber' },
      { label: 'Fixes disponibles', value: this.totalFixesAvailable, subtitle: 'Vulnerabilidades con remediación', accent: 'green' },
      { label: 'Risk score promedio', value: `${avgRisk.toFixed(2)} / 10`, subtitle: 'Promedio entre repositorios', accent: 'cyan' },
    ];
  }

  private repoVulnerabilities(repo: Analysis['repositories'][number]): number {
    if (!this.hasType('dependency')) return 0;
    const allowed = new Set(this.enabledSeverities.map((item) => item.toLowerCase()));
    return (repo.vulnerabilities.items ?? []).filter((item) => allowed.has((item.severity ?? 'Unknown').toLowerCase())).length;
  }

  get totalFixesAvailable(): number {
    if (!this.analysis) return 0;
    if (!this.hasType('dependency')) return 0;
    return this.filteredRepositories.reduce((acc, repo) => acc + (repo.vulnerabilities.with_fix_available ?? 0), 0);
  }

  get totalCicdFindings(): number {
    if (!this.analysis) return 0;

    if (!this.hasType('cicd')) return 0;
    return this.filteredRepositories.reduce((acc, repo) => acc + (repo.cicd?.total_findings ?? 0), 0);
  }

  get vulnerabilityRows(): VulnerabilityRow[] {
    if (!this.analysis) return [];
    if (!this.hasType('dependency')) return [];
    const allowed = new Set(this.enabledSeverities.map((item) => item.toLowerCase()));
    return this.filteredRepositories.flatMap((repo) =>
      (repo.vulnerabilities.items ?? []).map((item) => ({ ...item, repository: repo.name }))
    ).filter((item) => allowed.has((item.severity ?? 'Unknown').toLowerCase()));
  }

  get cicdRows(): CicdRow[] {
    if (!this.analysis) return [];

    if (!this.hasType('cicd')) return [];
    return this.filteredRepositories.flatMap((repo) =>
      (repo.cicd?.items ?? []).map((item) => ({
        ...item,
        repository: repo.name,
      }))
    );
  }

  get validation(): ValidationMetadata {
    return this.analysis?.metadata.validation ?? { warnings: [], invalid_files: [] };
  }

  get cweRanking(): Array<{ cwe: string; count: number; repos_count: number }> {
    if (!this.analysis) return [];

    const baseRanking = this.analysis.cross_repo_analysis.common_weakness_ranking ?? [];
    const cweRepoMap = new Map<string, Set<string>>();

    this.vulnerabilityRows.forEach((row) => {
      const cwe = row.cwe?.trim();
      if (!cwe) return;
      if (!cweRepoMap.has(cwe)) cweRepoMap.set(cwe, new Set<string>());
      cweRepoMap.get(cwe)?.add(row.repository);
    });

    return baseRanking.map((item) => ({
      ...item,
      repos_count: cweRepoMap.get(item.cwe)?.size ?? 0,
    }));
  }

  get normalizedRiskRanking(): Array<{ name: string; risk_score: number }> {
    if (!this.analysis) return [];
    return [...this.filteredRepositories]
      .sort((a, b) => (b.metrics.risk_score ?? 0) - (a.metrics.risk_score ?? 0))
      .map((repo) => ({
        name: repo.name,
        risk_score: repo.metrics.risk_score ?? 0,
      }));
  }

  get formattedGeneratedAt(): string {
    if (!this.analysis?.metadata.generated_at) return 'N/A';
    return new Date(this.analysis.metadata.generated_at).toLocaleString();
  }

  get filteredSeverityDistribution(): Record<string, number> {
    const result: Record<string, number> = {};
    this.vulnerabilityRows.forEach((row) => {
      const key = row.severity || 'Unknown';
      result[key] = (result[key] ?? 0) + 1;
    });
    return result;
  }

  get keyFindings(): KeyFinding[] {
    if (!this.analysis) return [];

    const topRepo = this.normalizedRiskRanking[0];
    const topCwe = this.cweRanking[0];
    const criticalHighWithFix = this.vulnerabilityRows.filter(
      (v) => (v.severity === 'Critical' || v.severity === 'High') && v.fix_available
    ).length;

    const findings: KeyFinding[] = [];

    if (topRepo) {
      const repoData = this.analysis.repositories.find((r) => r.name === topRepo.name);
      let driver = 'Sin datos';
      if (repoData) {
        const grypeCount = repoData.vulnerabilities.total;
        const codeqlCount = repoData.codeql.total_issues;
        const cicdCount = repoData.cicd?.total_findings ?? 0;
        if (grypeCount >= codeqlCount && grypeCount >= cicdCount) {
          driver = `${grypeCount} vulnerabilidades de dependencias (Grype)`;
        } else if (codeqlCount >= grypeCount && codeqlCount >= cicdCount) {
          driver = `${codeqlCount} issues de analisis estatico (CodeQL)`;
        } else {
          driver = `${cicdCount} hallazgos de CI/CD`;
        }
      }
      findings.push({
        icon: '🎯',
        label: 'Mayor riesgo',
        value: `${topRepo.name} (${topRepo.risk_score.toFixed(2)})`,
        detail: `Driver principal: ${driver}`,
        accent: 'red',
      });
    }

    if (topCwe) {
      findings.push({
        icon: '🔗',
        label: 'Debilidad mas repetida',
        value: topCwe.cwe,
        detail: `${topCwe.count} ocurrencias en ${topCwe.repos_count ?? 0} repos`,
        accent: 'amber',
      });
    }

    findings.push({
      icon: '🔧',
      label: 'Fixes inmediatos disponibles',
      value: `${criticalHighWithFix} vulnerabilidades`,
      detail: 'Critical/High con parche listo para aplicar',
      accent: 'green',
    });

    return findings;
  }
}
