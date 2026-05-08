import { Component, Input } from '@angular/core';
import { CicdRow } from '../../models/analysis.model';

@Component({
  selector: 'app-cicd-findings-table',
  standalone: true,
  templateUrl: './cicd-findings-table.component.html',
  styleUrl: './cicd-findings-table.component.css',
})
export class CicdFindingsTableComponent {
  @Input() rows: CicdRow[] = [];

  readonly defaultLimit = 10;
  showAll = false;

  get visibleRows() {
    return this.showAll ? this.rows : this.rows.slice(0, this.defaultLimit);
  }

  get hasMore() {
    return this.rows.length > this.defaultLimit;
  }

  toggle(): void {
    this.showAll = !this.showAll;
  }
}
