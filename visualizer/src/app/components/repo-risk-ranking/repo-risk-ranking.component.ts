import { Component, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-repo-risk-ranking',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './repo-risk-ranking.component.html',
  styleUrl: './repo-risk-ranking.component.css',
})
export class RepoRiskRankingComponent {
  @Input() ranking: Array<{ name: string; risk_score: number }> = [];
}
