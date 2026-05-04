import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ExecutiveInsight {
  label: string;
  value: string | number;
}

@Component({
  selector: 'app-executive-insights',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './executive-insights.component.html',
  styleUrl: './executive-insights.component.css',
})
export class ExecutiveInsightsComponent {
  @Input() insights: ExecutiveInsight[] = [];
}
