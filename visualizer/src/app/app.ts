import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
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
import { ExecutiveInsightsComponent } from './components/executive-insights/executive-insights.component';
import { RepoSeverityMatrixComponent } from './components/repo-severity-matrix/repo-severity-matrix.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
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
    ExecutiveInsightsComponent,
    RepoSeverityMatrixComponent,
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  loading = true;
  error = '';
  analysis: Analysis | null = null;

  constructor(private readonly analysisService: AnalysisDataService) {}

  ngOnInit(): void {
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

  get isEmpty(): boolean {
    return !this.analysis || !this.analysis.repositories?.length;
  }

  get kpis() {
    if (!this.analysis) return [];
    const avgRisk = this.analysis.repositories.length
      ? this.analysis.repositories.reduce((acc, repo) => acc + repo.metrics.risk_score, 0) /
        this.analysis.repositories.length
      : 0;

    return [
      { label: 'Repos analizados', value: this.analysis.metadata.repos_analyzed, subtitle: 'Repositorios escaneados por pipeline', accent: 'cyan' },
      { label: 'Componentes', value: this.analysis.cross_repo_analysis.total_components, subtitle: 'Inventario consolidado SBOM', accent: 'teal' },
      { label: 'Vulnerabilidades', value: this.analysis.cross_repo_analysis.total_vulnerabilities, subtitle: 'Detectadas por Grype', accent: 'red' },
      { label: 'Issues CodeQL', value: this.analysis.cross_repo_analysis.total_codeql_issues, subtitle: 'Hallazgos de análisis estático', accent: 'amber' },
      { label: 'Hallazgos CI/CD', value: this.totalCicdFindings, subtitle: 'Workflows y prácticas inseguras', accent: 'amber' },
      { label: 'Fixes disponibles', value: this.totalFixesAvailable, subtitle: 'Vulnerabilidades con remediación', accent: 'green' },
      { label: 'Risk score promedio', value: `${avgRisk.toFixed(2)} / 10`, subtitle: 'Promedio entre repositorios', accent: 'cyan' },
    ];
  }

  get totalFixesAvailable(): number {
    if (!this.analysis) return 0;
    return this.analysis.repositories.reduce((acc, repo) => acc + (repo.vulnerabilities.with_fix_available ?? 0), 0);
  }

  get totalCicdFindings(): number {
    if (!this.analysis) return 0;

    return (
      this.analysis.cross_repo_analysis.total_cicd_findings ??
      this.analysis.repositories.reduce((acc, repo) => acc + (repo.cicd?.total_findings ?? 0), 0)
    );
  }

  get vulnerabilityRows(): VulnerabilityRow[] {
    if (!this.analysis) return [];
    return this.analysis.repositories.flatMap((repo) =>
      (repo.vulnerabilities.items ?? []).map((item) => ({ ...item, repository: repo.name }))
    );
  }

  get cicdRows(): CicdRow[] {
    if (!this.analysis) return [];

    return this.analysis.repositories.flatMap((repo) =>
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

  get normalizedRiskRanking(): Array<{ name: string; risk_score: number; risk_score_raw: number }> {
    if (!this.analysis) return [];
    return [...this.analysis.repositories]
      .sort((a, b) => (b.metrics.risk_score ?? 0) - (a.metrics.risk_score ?? 0))
      .map((repo) => ({
        name: repo.name,
        risk_score: repo.metrics.risk_score ?? 0,
        risk_score_raw: repo.metrics.risk_score_raw ?? repo.metrics.risk_score ?? 0,
      }));
  }

  get executiveInsights(): Array<{ label: string; value: string | number; secondary: string; accent: string }> {
    if (!this.analysis) return [];
    const topRepo = this.normalizedRiskRanking[0];
    const severityEntries = Object.entries(this.analysis.cross_repo_analysis.severity_distribution ?? {});
    const dominantSeverity = severityEntries.sort((a, b) => b[1] - a[1])[0]?.[0] ?? 'N/A';
    const highCritical = (this.analysis.cross_repo_analysis.severity_distribution?.['High'] ?? 0) +
      (this.analysis.cross_repo_analysis.severity_distribution?.['Critical'] ?? 0);
    const topCwe = this.cweRanking[0]?.cwe ?? 'N/A';

    return [
      {
        label: 'Repositorio con mayor riesgo',
        value: topRepo ? `${topRepo.name}` : 'N/A',
        secondary: topRepo ? `Score ${topRepo.risk_score.toFixed(2)} / 10` : 'Sin datos de ranking',
        accent: 'critical',
      },
      { label: 'Severidad predominante', value: dominantSeverity, secondary: 'Distribución global de Grype', accent: 'amber' },
      { label: 'Total High/Critical', value: highCritical, secondary: 'Vulnerabilidades prioritarias', accent: 'red' },
      { label: 'Total CI/CD findings', value: this.totalCicdFindings, secondary: 'Hallazgos de workflows', accent: 'teal' },
      { label: 'CWE más frecuente', value: topCwe, secondary: 'Debilidad más repetida', accent: 'cyan' },
      { label: 'Fixes disponibles', value: this.totalFixesAvailable, secondary: 'Remediación potencial inmediata', accent: 'green' },
    ];
  }

  get formattedGeneratedAt(): string {
    if (!this.analysis?.metadata.generated_at) return 'N/A';
    return new Date(this.analysis.metadata.generated_at).toLocaleString();
  }
}
