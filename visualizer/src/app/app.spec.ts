import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { App } from './app';
import { AnalysisDataService } from './services/analysis-data.service';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        {
          provide: AnalysisDataService,
          useValue: {
            getAnalysis: () => of({ metadata: { generated_at: '', repos_analyzed: 0, data_sources: [] }, repositories: [], cross_repo_analysis: { total_components: 0, total_vulnerabilities: 0, total_codeql_issues: 0, severity_distribution: {}, repo_ranking_by_risk: [] } }),
            refreshState$: of('idle'),
            forceRefresh: () => undefined,
          },
        },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render dashboard title', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Cybersecurity Analysis Dashboard');
  });
});
