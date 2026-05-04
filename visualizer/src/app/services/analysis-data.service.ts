import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  BehaviorSubject,
  Observable,
  catchError,
  distinctUntilChanged,
  map,
  merge,
  shareReplay,
  switchMap,
  throwError,
  timer,
  Subject,
} from 'rxjs';
import { Analysis } from '../models/analysis.model';

@Injectable({ providedIn: 'root' })
export class AnalysisDataService {
  private readonly analysisUrl = 'assets/analysis.json';
  private readonly pollMs = 45000;
  private readonly manualRefresh$ = new Subject<void>();
  private readonly refreshStateSubject = new BehaviorSubject<'idle' | 'updated' | 'error'>('idle');
  private lastFingerprint = '';

  readonly refreshState$ = this.refreshStateSubject.asObservable();

  constructor(private readonly http: HttpClient) {}

  getAnalysis(): Observable<Analysis> {
    return merge(timer(0, this.pollMs), this.manualRefresh$).pipe(
      switchMap(() => this.http.get<Analysis>(this.withCacheBust())),
      map((analysis) => {
        const next = this.fingerprint(analysis);
        const changed = this.lastFingerprint !== next;
        this.lastFingerprint = next;
        this.refreshStateSubject.next(changed ? 'updated' : 'idle');
        return analysis;
      }),
      catchError((error) => {
        this.refreshStateSubject.next('error');
        return throwError(() => error);
      }),
      distinctUntilChanged((a, b) => this.fingerprint(a) === this.fingerprint(b)),
      shareReplay({ bufferSize: 1, refCount: true })
    );
  }

  forceRefresh(): void {
    this.manualRefresh$.next();
  }

  private withCacheBust(): string {
    return `${this.analysisUrl}?_=${Date.now()}`;
  }

  private fingerprint(data: Analysis): string {
    return [
      data.metadata?.generated_at ?? '',
      data.repositories?.length ?? 0,
      data.cross_repo_analysis?.total_components ?? 0,
      data.cross_repo_analysis?.total_vulnerabilities ?? 0,
      data.cross_repo_analysis?.total_codeql_issues ?? 0,
    ].join('|');
  }
}
