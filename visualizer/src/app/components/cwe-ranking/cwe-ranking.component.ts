import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-cwe-ranking',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cwe-ranking.component.html',
  styleUrl: './cwe-ranking.component.css',
})
export class CweRankingComponent {
  @Input() ranking: Array<{ cwe: string; count: number }> = [];
}
