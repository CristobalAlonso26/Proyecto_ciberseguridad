import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-codeql-level-summary',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './codeql-level-summary.component.html',
  styleUrl: './codeql-level-summary.component.css',
})
export class CodeqlLevelSummaryComponent {
  @Input() byLevel: Record<string, number> = {};

  get entries(): Array<{ level: string; count: number }> {
    return Object.entries(this.byLevel).map(([level, count]) => ({ level, count }));
  }
}
