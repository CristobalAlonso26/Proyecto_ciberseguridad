import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-codeql-level-summary',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './codeql-level-summary.component.html',
  styleUrl: './codeql-level-summary.component.css',
})
export class CodeqlLevelSummaryComponent {
  @Input() repositories: RepositoryAnalysis[] = [];

  readonly defaultLimit = 10;
  showAll = false;

  get levels(): string[] {
    const detected = new Set<string>();
    this.repositories.forEach((repo) => {
      Object.keys(repo.codeql.by_level ?? {}).forEach((level) => detected.add(level));
    });
    return Array.from(detected).sort((a, b) => a.localeCompare(b));
  }

  count(repo: RepositoryAnalysis, level: string): number {
    return (repo.codeql.by_level ?? {})[level] ?? 0;
  }

  total(repo: RepositoryAnalysis): number {
    return Object.values(repo.codeql.by_level ?? {}).reduce((acc, value) => acc + value, 0);
  }

  maxValue(): number {
    const values = this.repositories.flatMap((repo) => this.levels.map((lvl) => this.count(repo, lvl)));
    return Math.max(0, ...values);
  }

  alpha(value: number): number {
    const max = this.maxValue();
    if (!max) return 0.1;
    return 0.15 + (value / max) * 0.75;
  }

  get visibleRepos() {
    return this.showAll ? this.repositories : this.repositories.slice(0, this.defaultLimit);
  }

  get hasMore() {
    return this.repositories.length > this.defaultLimit;
  }

  toggle(): void {
    this.showAll = !this.showAll;
  }
}
