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
}
