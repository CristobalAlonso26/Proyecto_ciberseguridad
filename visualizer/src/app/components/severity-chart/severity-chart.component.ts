import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-severity-chart',
  standalone: true,
  templateUrl: './severity-chart.component.html',
  styleUrl: './severity-chart.component.css',
})
export class SeverityChartComponent {
  @Input() distribution: Record<string, number> = {};

  get entries() {
    const preferredOrder = ['Critical', 'High', 'Medium', 'Low'];
    const keys = Object.keys(this.distribution ?? {});
    const ordered = [
      ...preferredOrder.filter((k) => keys.includes(k)),
      ...keys.filter((k) => !preferredOrder.includes(k)).sort(),
    ];
    return ordered.map((key) => ({ key, value: this.distribution[key] ?? 0 }));
  }

  get total() {
    return this.entries.reduce((sum, item) => sum + item.value, 0);
  }

  width(value: number): string {
    if (!this.total) return '0%';
    return `${(value / this.total) * 100}%`;
  }

  percent(value: number): string {
    if (!this.total) return '0%';
    return `${((value / this.total) * 100).toFixed(1)}%`;
  }
}
