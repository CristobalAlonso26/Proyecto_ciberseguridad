import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Analysis } from '../models/analysis.model';

@Injectable({ providedIn: 'root' })
export class AnalysisDataService {
  constructor(private readonly http: HttpClient) {}

  getAnalysis(): Observable<Analysis> {
    return this.http.get<Analysis>('assets/analysis.json');
  }
}
