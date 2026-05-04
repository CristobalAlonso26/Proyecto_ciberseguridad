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
  @Input() ranking: Array<{ name: string; risk_score: number; risk_score_raw: number }> = [];

  width(score: number): string {
    return `${Math.max(0, Math.min(100, score * 10))}%`;
  }
}
