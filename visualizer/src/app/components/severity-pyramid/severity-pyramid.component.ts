import { Component, Input, OnChanges, SimpleChanges, ViewChild, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartDataset } from 'chart.js';
import { RepositoryAnalysis } from '../../models/analysis.model';

@Component({
  selector: 'app-severity-pyramid',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './severity-pyramid.component.html',
  styleUrl: './severity-pyramid.component.css',
})
export class SeverityPyramidComponent implements OnChanges, AfterViewInit {
  @Input() repositories: RepositoryAnalysis[] = [];
  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  readonly DEFAULT_LIMIT = 15;
  displayLimit = this.DEFAULT_LIMIT;
  showAll = false;

  allRelevant: RepositoryAnalysis[] = [];

  chartData: ChartConfiguration<'bar'>['data'] = { labels: [], datasets: [] };
  chartReady = false;

  constructor(private cdr: ChangeDetectorRef) {}

  ngAfterViewInit(): void {
    this.chartReady = true;
  }

  get chartHeight(): string {
    const count = this.chartData.labels?.length ?? 0;
    if (count === 0) return '320px';
    const barHeight = Math.max(count * 36, 320);
    return `${barHeight}px`;
  }

  get hasMore(): boolean {
    return !this.showAll && this.displayLimit < this.allRelevant.length;
  }

  get remainingCount(): number {
    if (this.showAll) return 0;
    return this.allRelevant.length - this.displayLimit;
  }

  get displayCount(): number {
    return this.chartData.labels?.length ?? 0;
  }

  get totalCount(): number {
    return this.allRelevant.length;
  }

  readonly chartOptions: ChartConfiguration<'bar'>['options'] = {
    animation: false,
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    hover: { mode: 'index', intersect: true },
    scales: {
      x: {
        stacked: true,
        title: { display: true, text: 'Cantidad de vulnerabilidades', color: '#94a3b8' },
      },
      y: {
        stacked: true,
        ticks: {
          autoSkip: false,
          maxRotation: 0,
          font: { size: 12 },
          padding: 8,
        },
      },
    },
    plugins: {
      legend: { labels: { color: '#cbd5e1', font: { size: 12 } } },
      tooltip: {
        mode: 'index',
        intersect: true,
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        titleFont: { size: 13, weight: 'bold' },
        bodyFont: { size: 12 },
        padding: 12,
        cornerRadius: 8,
      },
    },
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['repositories']) {
      const current = changes['repositories'].currentValue || [];
      const previous = changes['repositories'].previousValue || [];

      // Anti-loop: Si el padre nos envía la misma cantidad de repositorios,
      // verificamos si son los mismos. Si lo son, evitamos resetear el componente.
      if (previous.length > 0 && current.length === previous.length) {
        const sameRepos = current.every((repo: any, i: number) => repo.name === previous[i]?.name);
        if (sameRepos) {
          return; // Son los mismos datos, ignoramos el ciclo de Angular para no sobreescribir el botón
        }
      }

      console.log('🧹 Filtros globales cambiaron. Reseteando pirámide a 15...');
      this.displayLimit = this.DEFAULT_LIMIT;
      this.showAll = false;
      this.allRelevant = this.repositories
        .filter((repo) => (repo.vulnerabilities.total ?? 0) > 0)
        .sort((a, b) => (b.metrics?.risk_score ?? 0) - (a.metrics?.risk_score ?? 0));

      this.buildChartData();
    }
  }

  loadMore(): void {
    console.log('🔄 Botón presionado: iniciando carga de más repositorios...');
    this.showAll = true;
    this.buildChartData();
  }

  private buildChartData(): void {
    const source = this.showAll
      ? this.allRelevant
      : this.allRelevant.slice(0, this.displayLimit);

    const colors: Array<{ label: string; color: string }> = [
      { label: 'Critical', color: '#E45756' },
      { label: 'High', color: '#F58518' },
      { label: 'Medium', color: '#EDC948' },
      { label: 'Low', color: '#54A24B' },
    ];

    const newLabels = source.map((repo) => repo.name);
    const newDatasets = colors.map(({ label, color }) => ({
      label,
      backgroundColor: color,
      borderRadius: 5,
      barThickness: 28,
      data: source.map((repo) => (repo.vulnerabilities.by_severity ?? {})[label] ?? 0),
    })) as ChartDataset<'bar'>[];

    // Reasignamos el objeto completo para disparar la reactividad nativa
    this.chartData = {
      labels: newLabels,
      datasets: newDatasets
    };

    console.log(`📊 Datos actualizados: renderizando ${newLabels.length} repositorios.`);

    // Angular detectará el cambio y actualizará la altura del div y el canvas automáticamente
    if (this.cdr) {
      this.cdr.detectChanges();
    }
  }
}