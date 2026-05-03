import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { VulnerabilityRow } from '../../models/analysis.model';

@Component({
  selector: 'app-vulnerabilities-table',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './vulnerabilities-table.component.html',
  styleUrl: './vulnerabilities-table.component.css',
})
export class VulnerabilitiesTableComponent {
  @Input() rows: VulnerabilityRow[] = [];

  selectedRepository = 'all';
  selectedSeverity = 'all';

  get repositories(): string[] {
    return Array.from(new Set(this.rows.map((x) => x.repository))).sort();
  }

  get severities(): string[] {
    return Array.from(new Set(this.rows.map((x) => x.severity))).sort();
  }

  get filteredRows(): VulnerabilityRow[] {
    return this.rows.filter((row) => {
      const matchesRepo = this.selectedRepository === 'all' || row.repository === this.selectedRepository;
      const matchesSeverity = this.selectedSeverity === 'all' || row.severity === this.selectedSeverity;
      return matchesRepo && matchesSeverity;
    });
  }
}
