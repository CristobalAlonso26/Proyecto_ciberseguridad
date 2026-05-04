import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-severity-pyramid',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './severity-pyramid.component.html',
  styleUrl: './severity-pyramid.component.css',
})
export class SeverityPyramidComponent implements OnChanges {
  @Input() repositories: RepositoryAnalysis[] = [];

  chartData: ChartConfiguration<'bar'>['data'] = { labels: [], datasets: [] };

  readonly chartOptions: ChartConfiguration<'bar'>['options'] = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    scales: { x: { stacked: true }, y: { stacked: true } },
    plugins: {
      legend: { labels: { color: '#cbd5e1' } },
      tooltip: { mode: 'index', intersect: true },
    },
  };

  ngOnChanges(): void {
    const labels = this.repositories.map((repo) => repo.name);
    this.chartData = {
      labels,
      datasets: [
        this.buildDataset('Critical', '#E45756'),
        this.buildDataset('High', '#F58518'),
        this.buildDataset('Medium', '#EDC948'),
        this.buildDataset('Low', '#54A24B'),
      ],
    };
  }

  private buildDataset(severity: string, color: string): ChartConfiguration<'bar'>['data']['datasets'][number] {
    return {
      label: severity,
      backgroundColor: color,
      borderRadius: 5,
      data: this.repositories.map((repo) => (repo.vulnerabilities.by_severity ?? {})[severity] ?? 0),
    };
  }
}
