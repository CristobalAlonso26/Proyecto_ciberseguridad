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
    const order = ['Critical', 'High', 'Medium', 'Low'];
    return order.map((key) => ({ key, value: this.distribution[key] ?? 0 }));
  }

  get total() {
    return this.entries.reduce((sum, item) => sum + item.value, 0);
  }

  width(value: number): string {
    if (!this.total) return '0%';
    return `${(value / this.total) * 100}%`;
  }
}
