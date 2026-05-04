import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RepoComparisonChartComponent } from './repo-comparison-chart.component';

describe('RepoComparisonChartComponent', () => {
  let component: RepoComparisonChartComponent;
  let fixture: ComponentFixture<RepoComparisonChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RepoComparisonChartComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(RepoComparisonChartComponent);
    component = fixture.componentInstance;
  });

  it('should map repositories into grouped bar datasets', () => {
    component.repositories = [
      {
        name: 'repo-x',
        sbom: { total_components: 0, by_type: {}, by_language: {} },
        vulnerabilities: { total: 5, items: [] },
        codeql: { total_issues: 2, top_files: [], items: [] },
        metrics: { vulnerability_density: 0, risk_score: 0 },
      },
    ];

    component.ngOnChanges();

    expect(component.chartData.labels).toEqual(['repo-x']);
    expect(component.chartData.datasets[0].data).toEqual([5]);
    expect(component.chartData.datasets[1].data).toEqual([2]);
  });
});
