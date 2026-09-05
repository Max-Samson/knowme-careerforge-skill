export interface EngineOptions {
  expectedPages?: number;
  autoHeal?: boolean;
  outputPdf?: string;
}
export interface EngineResult {
  status: 'PASS' | 'FAIL' | 'UNVERIFIED';
  file: string;
  expectedPages: number;
  errors: string[];
  warnings: string[];
  checks: Record<string, { status: 'PASS' | 'FAIL' | 'UNVERIFIED'; [key: string]: unknown }>;
}
export function run(html: string, options?: EngineOptions): Promise<EngineResult>;
export function cli(args?: string[], defaults?: EngineOptions): Promise<EngineResult>;
