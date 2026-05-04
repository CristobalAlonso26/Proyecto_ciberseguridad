import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SeverityPyramidComponent } from './severity-pyramid.component';

describe('SeverityPyramidComponent', () => {
  let component: SeverityPyramidComponent;
  let fixture: ComponentFixture<SeverityPyramidComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SeverityPyramidComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SeverityPyramidComponent);
    component = fixture.componentInstance;
  });

  it('should build stacked datasets by severity', () => {
    component.repositories = [
      {
        name: 'repo-a',
        sbom: { total_components: 0, by_type: {}, by_language: {} },
        vulnerabilities: { total: 3, by_severity: { Critical: 1, High: 2 }, items: [] },
        codeql: { total_issues: 0, top_files: [], items: [] },
        metrics: { vulnerability_density: 0, risk_score: 0 },
      },
    ];

    component.ngOnChanges();

    expect(component.chartData.labels).toEqual(['repo-a']);
    expect(component.chartData.datasets.length).toBe(4);
    expect(component.chartData.datasets[0].data).toEqual([1]);
  });
});
