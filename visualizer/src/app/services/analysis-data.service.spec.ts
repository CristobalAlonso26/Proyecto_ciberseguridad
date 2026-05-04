import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { AnalysisDataService } from './analysis-data.service';

describe('AnalysisDataService', () => {
  let service: AnalysisDataService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(AnalysisDataService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should request analysis with cache busting', fakeAsync(() => {
    let responseSeen = false;
    service.getAnalysis().subscribe(() => {
      responseSeen = true;
    });

    const req = httpMock.expectOne((r) => r.url === 'assets/analysis.json' && r.params.has('_'));
    req.flush({ metadata: { generated_at: '2026-01-01', repos_analyzed: 0, data_sources: [] }, repositories: [], cross_repo_analysis: { total_components: 0, total_vulnerabilities: 0, total_codeql_issues: 0, severity_distribution: {}, repo_ranking_by_risk: [] } });
    tick();

    expect(responseSeen).toBeTrue();
  }));
});
