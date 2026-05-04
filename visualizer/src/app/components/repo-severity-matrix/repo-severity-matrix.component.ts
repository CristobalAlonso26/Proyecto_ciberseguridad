import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-repo-severity-matrix',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './repo-severity-matrix.component.html',
  styleUrl: './repo-severity-matrix.component.css',
})
export class RepoSeverityMatrixComponent {
  @Input() repositories: RepositoryAnalysis[] = [];

  readonly severities = ['Critical', 'High', 'Medium', 'Low'];

  getTotal(repo: RepositoryAnalysis): number {
    const bySeverity = repo.vulnerabilities.by_severity ?? {};
    return this.severities.reduce((sum, sev) => sum + (bySeverity[sev] ?? 0), 0);
  }

  count(repo: RepositoryAnalysis, severity: string): number {
    return (repo.vulnerabilities.by_severity ?? {})[severity] ?? 0;
  }

  width(repo: RepositoryAnalysis, severity: string): string {
    const total = this.getTotal(repo);
    if (!total) return '0%';
    return `${((this.count(repo, severity) / total) * 100).toFixed(1)}%`;
  }
}
