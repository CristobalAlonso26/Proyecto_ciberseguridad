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
  search = '';

  selectedVulnerability: VulnerabilityRow | null = null;

  readonly pageSize = 25;
  currentPage = 1;

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
      const q = this.search.trim().toLowerCase();
      const matchesSearch =
        !q ||
        row.id?.toLowerCase().includes(q) ||
        row.artifact?.toLowerCase().includes(q) ||
        row.cwe?.toLowerCase().includes(q) ||
        row.location?.toLowerCase().includes(q);
      return matchesRepo && matchesSeverity && matchesSearch;
    });
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.filteredRows.length / this.pageSize));
  }

  get pagedRows(): VulnerabilityRow[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredRows.slice(start, start + this.pageSize);
  }

  get pageNumbers(): number[] {
    const pages: number[] = [];
    const maxVisible = 5;
    let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
    const end = Math.min(this.totalPages, start + maxVisible - 1);
    start = Math.max(1, end - maxVisible + 1);
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }

  goToPage(page: number): void {
    this.currentPage = page;
  }

  prevPage(): void {
    if (this.currentPage > 1) this.currentPage--;
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) this.currentPage++;
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.selectedVulnerability = null;
  }

  selectVulnerability(vuln: VulnerabilityRow): void {
    if (this.selectedVulnerability === vuln) {
      this.selectedVulnerability = null;
    } else {
      this.selectedVulnerability = vuln;
    }
  }

  severityClass(severity: string): string {
    return severity?.toLowerCase?.() ?? 'unknown';
  }

  truncate(value: string | undefined, size = 28): string {
    if (!value) return '-';
    return value.length > size ? `${value.slice(0, size)}…` : value;
  }

  getRemediation(vuln: VulnerabilityRow): string | null {
    if (vuln.fix_available && vuln.artifact && vuln.fix_version) {
      return `Actualizar ${vuln.artifact} a la versión ${vuln.fix_version}`;
    }
    return null;
  }
}
