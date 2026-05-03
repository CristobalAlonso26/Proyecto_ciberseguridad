import { Component, Input } from '@angular/core';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-repo-comparison-chart',
  standalone: true,
  templateUrl: './repo-comparison-chart.component.html',
  styleUrl: './repo-comparison-chart.component.css',
})
export class RepoComparisonChartComponent {
  @Input() repositories: RepositoryAnalysis[] = [];
}
