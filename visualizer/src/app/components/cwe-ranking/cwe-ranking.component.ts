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
  @Input() ranking: Array<{ cwe: string; count: number; repos_count?: number }> = [];

  readonly defaultLimit = 10;
  showAll = false;

  get maxCount(): number {
    return Math.max(0, ...this.ranking.map((item) => item.count));
  }

  width(count: number): string {
    if (!this.maxCount) return '0%';
    return `${(count / this.maxCount) * 100}%`;
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
