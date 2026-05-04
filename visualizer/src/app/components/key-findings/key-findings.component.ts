import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface KeyFinding {
  icon: string;
  label: string;
  value: string;
  detail: string;
  accent: string;
}

@Component({
  selector: 'app-key-findings',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './key-findings.component.html',
  styleUrl: './key-findings.component.css',
})
export class KeyFindingsComponent {
  @Input() findings: KeyFinding[] = [];
}
