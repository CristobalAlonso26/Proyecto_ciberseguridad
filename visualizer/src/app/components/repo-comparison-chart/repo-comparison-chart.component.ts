import { Component, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-repo-comparison-chart',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './repo-comparison-chart.component.html',
  styleUrl: './repo-comparison-chart.component.css',
})
export class RepoComparisonChartComponent {
  @Input() repositories: RepositoryAnalysis[] = [];

  maxFor(type: 'grype' | 'codeql' | 'cicd' | 'risk'): number {
    const values = this.repositories.map((repo) => {
      if (type === 'grype') return repo.vulnerabilities.total ?? 0;
      if (type === 'codeql') return repo.codeql.total_issues ?? 0;
      if (type === 'cicd') return repo.cicd?.total_findings ?? 0;
      return repo.metrics.risk_score ?? 0;
    });
    return Math.max(0, ...values);
  }

  width(value: number, type: 'grype' | 'codeql' | 'cicd' | 'risk'): string {
    const max = this.maxFor(type);
    if (!max) return '0%';
    return `${Math.max(4, (value / max) * 100)}%`;
  }
}
