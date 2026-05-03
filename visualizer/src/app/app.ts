import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Analysis, CicdRow, VulnerabilityRow } from './models/analysis.model';
import { AnalysisDataService } from './services/analysis-data.service';
import { KpiCardsComponent } from './components/kpi-cards/kpi-cards.component';
import { SeverityChartComponent } from './components/severity-chart/severity-chart.component';
import { RepoRiskRankingComponent } from './components/repo-risk-ranking/repo-risk-ranking.component';
import { RepoComparisonChartComponent } from './components/repo-comparison-chart/repo-comparison-chart.component';
import { VulnerabilitiesTableComponent } from './components/vulnerabilities-table/vulnerabilities-table.component';
import { CicdFindingsTableComponent } from './components/cicd-findings-table/cicd-findings-table.component';

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
      { label: 'Repos analizados', value: this.analysis.metadata.repos_analyzed },
      { label: 'Total componentes', value: this.analysis.cross_repo_analysis.total_components },
      { label: 'Total vulnerabilidades', value: this.analysis.cross_repo_analysis.total_vulnerabilities },
      { label: 'Issues CodeQL', value: this.analysis.cross_repo_analysis.total_codeql_issues },
      { label: 'Hallazgos CI/CD', value: this.totalCicdFindings },
      { label: 'Risk score promedio', value: avgRisk.toFixed(2) },
    ];
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
      repo.vulnerabilities.items.map((item) => ({ ...item, repository: repo.name }))
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
}
