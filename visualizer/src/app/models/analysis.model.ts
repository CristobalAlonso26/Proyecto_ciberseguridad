export interface Analysis {
  metadata: AnalysisMetadata;
  repositories: RepositoryAnalysis[];
  cross_repo_analysis: CrossRepoAnalysis;
}

export interface AnalysisMetadata {
  generated_at: string;
  repos_analyzed: number;
  data_sources: string[];
  validation?: ValidationMetadata;
}

export interface ValidationMetadata {
  warnings: string[];
  invalid_files: string[];
}

export interface RepositoryAnalysis {
  name: string;
  sbom: SbomSummary;
  vulnerabilities: VulnerabilitySummary;
  codeql: CodeqlSummary;
  cicd?: CicdSummary;
  metrics: Metrics;
}

export interface CicdSummary {
  workflows_scanned: number;
  total_findings: number;
  items: CicdItem[];
}

export interface CicdItem {
  workflow: string;
  issue: string;
}

export interface SbomSummary {
  total_components: number;
  by_type: Record<string, number>;
  by_language: Record<string, number>;
}

export interface VulnerabilitySummary {
  total: number;
  severity_distribution?: Record<string, number>;
  by_severity?: Record<string, number>;
  by_type?: Record<string, number>;
  by_artifact_type?: Record<string, number>;
  with_fix_available?: number;
  items: VulnerabilityItem[];
}

export interface VulnerabilityItem {
  id: string;
  severity: string;
  description?: string;
  cvss_score?: number;
  epss?: number;
  cwe?: string;
  artifact: string;
  artifact_version: string;
  artifact_type?: string;
  artifact_language?: string;
  location?: string;
  fix_state?: string;
  fix_available?: boolean;
  fix_version?: string;
  risk?: number;
}

export interface CodeqlSummary {
  total_issues: number;
  by_rule?: Record<string, number>;
  by_level?: Record<string, number>;
  top_rules?: Array<{ value: string; count: number }>;
  top_files: Array<{ value: string; count: number }>;
  items: CodeqlItem[];
}

export interface CodeqlItem {
  rule_id: string;
  level: string;
  message: string;
  file: string;
  line: number;
  column: number;
}

export interface Metrics {
  vulnerability_density: number;
  risk_score: number;
  risk_score_raw?: number;
}

export interface CrossRepoAnalysis {
  total_components: number;
  total_vulnerabilities: number;
  total_codeql_issues: number;
  total_cicd_findings?: number;
  cicd_findings_by_repo?: Array<{ name: string; findings: number }>;
  severity_distribution: Record<string, number>;
  common_weakness_ranking?: Array<{ cwe: string; count: number }>;
  repo_ranking_by_risk: Array<{ name: string; risk_score: number }>;
}

export interface VulnerabilityRow extends VulnerabilityItem {
  repository: string;
}

export interface CicdRow extends CicdItem {
  repository: string;
}
