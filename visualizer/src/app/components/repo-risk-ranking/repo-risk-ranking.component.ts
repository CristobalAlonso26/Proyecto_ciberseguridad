import { Component, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';

export interface RiskBadge {
  label: string;
  color: string;
  bg: string;
}

@Component({
  selector: 'app-repo-risk-ranking',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './repo-risk-ranking.component.html',
  styleUrl: './repo-risk-ranking.component.css',
})
export class RepoRiskRankingComponent {
  @Input() ranking: Array<{ name: string; risk_score: number }> = [];

  readonly defaultLimit = 10;
  showAll = false;

  width(score: number): string {
    return `${Math.max(0, Math.min(100, score * 10))}%`;
  }

  getBadge(score: number): RiskBadge {
    if (score < 2.5) {
      return { label: 'Riesgo Controlado', color: '#22c55e', bg: 'rgba(34, 197, 94, 0.12)' };
    }
    if (score <= 3.75) {
      return { label: 'Atencion Requerida', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)' };
    }
    return { label: 'Intervencion Inmediata', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.12)' };
  }

  get visibleRanking() {
    return this.showAll ? this.ranking : this.ranking.slice(0, this.defaultLimit);
  }

  get hasMore() {
    return this.ranking.length > this.defaultLimit;
  }

  toggle(): void {
    this.showAll = !this.showAll;
  }
}
