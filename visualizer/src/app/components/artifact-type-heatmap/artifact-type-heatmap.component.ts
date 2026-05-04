import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-artifact-type-heatmap',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './artifact-type-heatmap.component.html',
  styleUrl: './artifact-type-heatmap.component.css',
})
export class ArtifactTypeHeatmapComponent {
  @Input() repositories: RepositoryAnalysis[] = [];

  get columns(): string[] {
    return Array.from(
      new Set(
        this.repositories.flatMap((repo) => Object.keys(repo.vulnerabilities.by_type ?? repo.vulnerabilities.by_artifact_type ?? {}))
      )
    ).sort();
  }

  count(repo: RepositoryAnalysis, type: string): number {
    const source = repo.vulnerabilities.by_type ?? repo.vulnerabilities.by_artifact_type ?? {};
    return source[type] ?? 0;
  }
}
