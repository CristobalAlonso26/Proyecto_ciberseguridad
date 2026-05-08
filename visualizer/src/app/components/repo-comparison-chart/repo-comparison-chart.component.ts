import { Component, Input, OnChanges } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-repo-comparison-chart',
  standalone: true,
  imports: [BaseChartDirective],
  templateUrl: './repo-comparison-chart.component.html',
  styleUrl: './repo-comparison-chart.component.css',
})
export class RepoComparisonChartComponent implements OnChanges {
  @Input() repositories: RepositoryAnalysis[] = [];

  readonly defaultLimit = 15;
  showAll = false;

  chartData: ChartConfiguration<'bar'>['data'] = { labels: [], datasets: [] };

  readonly chartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { ticks: { color: '#cbd5e1' } },
      y: { beginAtZero: true, ticks: { color: '#cbd5e1' } },
    },
    plugins: {
      legend: { labels: { color: '#cbd5e1' } },
      tooltip: { mode: 'index', intersect: false },
    },
  };

  get visibleRows() {
    return this.showAll ? this.repositories : this.repositories.slice(0, this.defaultLimit);
  }

  get hasMore() {
    return this.repositories.length > this.defaultLimit;
  }

  toggle(): void {
    this.showAll = !this.showAll;
  }

  ngOnChanges(): void {
    this.chartData = {
      labels: this.repositories.map((repo) => repo.name),
      datasets: [
        {
          label: 'Dependency (Grype)',
          data: this.repositories.map((repo) => repo.vulnerabilities.total ?? 0),
          backgroundColor: '#F58518',
          borderRadius: 4,
        },
        {
          label: 'CodeQL',
          data: this.repositories.map((repo) => repo.codeql.total_issues ?? 0),
          backgroundColor: '#22D3EE',
          borderRadius: 4,
        },
      ],
    };
  }
}
