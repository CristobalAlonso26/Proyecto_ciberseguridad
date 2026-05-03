import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-kpi-cards',
  standalone: true,
  templateUrl: './kpi-cards.component.html',
  styleUrl: './kpi-cards.component.css',
})
export class KpiCardsComponent {
  @Input() cards: Array<{ label: string; value: string | number }> = [];
}
