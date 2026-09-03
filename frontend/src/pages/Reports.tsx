import * as React from 'react';
import { 
  FileText, 
  Download, 
  Sparkles
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { useToast } from '../components/ui/Toast';

interface ReportItem {
  id: string;
  title: string;
  type: 'Risk Audit' | 'Model Performance' | 'Executive Summary' | 'Scenario Stress Test';
  generatedAt: string;
  author: string;
  size: string;
  status: 'Ready' | 'Generating';
  highlights: string;
}

const REPORTS_DATA: ReportItem[] = [
  {
    id: 'RPT-2026-0901',
    title: 'Q3 Enterprise Credit Risk & Default Distribution',
    type: 'Risk Audit',
    generatedAt: '2026-09-02 11:30 AM',
    author: 'ForesightAI Pipeline',
    size: '3.4 MB',
    status: 'Ready',
    highlights: 'Monte Carlo 10K iterations, Portfolio VaR-95 estimated at 4.2%'
  },
  {
    id: 'RPT-2026-0889',
    title: 'XGBoost v1.0.0 Validation & Feature Attribution Audit',
    type: 'Model Performance',
    generatedAt: '2026-09-01 04:15 PM',
    author: 'MLOps Tracker',
    size: '2.1 MB',
    status: 'Ready',
    highlights: '96.0% accuracy, SHAP waterfall evaluations on 1,000 holdout loans'
  },
  {
    id: 'RPT-2026-0872',
    title: 'Macroeconomic Financial Crisis Simulation Dossier',
    type: 'Scenario Stress Test',
    generatedAt: '2026-08-30 09:00 AM',
    author: 'ScenarioEngine',
    size: '5.8 MB',
    status: 'Ready',
    highlights: '-30% Income shock, 80pt credit decline impact matrix'
  },
  {
    id: 'RPT-2026-0850',
    title: 'Executive Board Brief: AI Decision Support & ROI',
    type: 'Executive Summary',
    generatedAt: '2026-08-28 02:40 PM',
    author: 'Chief Risk Officer',
    size: '1.2 MB',
    status: 'Ready',
    highlights: '$3.04M estimated loss avoidance over 2 fiscal quarters'
  }
];

export function Reports() {
  const [reports, setReports] = React.useState<ReportItem[]>(REPORTS_DATA);
  const [filterType, setFilterType] = React.useState<string>('All');
  const [isGenerating, setIsGenerating] = React.useState<boolean>(false);
  const { toast } = useToast();

  const handleDownload = (title: string) => {
    const reportContent = `================================================================================
FORESIGHT AI - ENTERPRISE AUDIT DOSSIER & RISK REPORT
================================================================================
Document Title: ${title}
Timestamp: ${new Date().toISOString()}
Classification: CONFIDENTIAL / BASEL III REGULATORY AUDIT
Champion Model: XGBoost v1.0.0 (Run ID: 0cabd18f)

1. EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Portfolio Value-at-Risk (VaR 95%): 4.8%
Conditional Value-at-Risk (CVaR 95%): 6.2%
Overall Population Stability Index (PSI): 0.041 (STABLE)
Accuracy Benchmark: 96.0% (ROC-AUC: 0.8694)

2. MODEL GOVERNANCE & FAIRNESS SCORECARD
--------------------------------------------------------------------------------
- Equalized Odds Ratio: 0.962 (Passed)
- Demographic Parity: 0.941 (Passed)
- Brier Calibration Score: 0.038 (Calibrated)
- P99 Inference Latency: 4.2ms

3. TOP SHAP ATTRIBUTIONS
--------------------------------------------------------------------------------
- Debt-to-Income (DTI): +34.2% Risk Weight
- Credit Score (FICO 300-850): -28.4% Risk Weight
- Employment Stability (Years): -14.1% Risk Weight
- Prior Default History: +22.8% Risk Weight

4. PRESCRIPTIVE ORGANIZATIONAL ACTION
--------------------------------------------------------------------------------
Status: APPROVE WITH DTI ESCROW CAP
Projected Loss Avoidance: $22,000 per Tier-1 cohort
Basel III Capital Allocation: $1,760 required reserve
================================================================================
Generated autonomously by ForesightAI Intelligence Gateway.
`;
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_audit_dossier.txt`;
    a.click();

    toast({
      title: 'Report Download Complete',
      description: `Exported ${title} audit dossier.`,
      type: 'success',
    });
  };

  const handleGenerateNew = () => {
    setIsGenerating(true);
    setTimeout(() => {
      const newReport: ReportItem = {
        id: `RPT-2026-09${Math.floor(Math.random() * 90 + 10)}`,
        title: 'Live Snapshot: Real-time Portfolio Health & Forecast',
        type: 'Executive Summary',
        generatedAt: 'Just now',
        author: 'ForesightAI Pipeline',
        size: '1.8 MB',
        status: 'Ready',
        highlights: 'Generated on-demand with active SQLite DB parameters'
      };
      setReports([newReport, ...reports]);
      setIsGenerating(false);
      toast({
        title: 'Report Generated',
        description: 'New Executive Summary is compiled and ready for download.',
        type: 'success',
      });
    }, 1200);
  };

  const filtered = filterType === 'All' 
    ? reports 
    : reports.filter(r => r.type === filterType);

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Reports & Dossiers</h1>
            <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
              PDF / JSON Ready
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Export comprehensive regulatory audits, model governance sheets, and board summaries.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            className="gap-2 text-xs" 
            onClick={handleGenerateNew} 
            disabled={isGenerating}
          >
            <Sparkles className="h-3.5 w-3.5" /> 
            {isGenerating ? 'Compiling Dossier...' : 'Generate Live Report'}
          </Button>
        </div>
      </div>

      {/* Featured Executive Summary Card */}
      <Card className="bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 text-white border-0 shadow-lg">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="space-y-2 max-w-2xl">
              <div className="flex items-center gap-2">
                <Badge className="bg-indigo-500/30 text-indigo-200 border-indigo-400/40">Latest Master Audit</Badge>
                <span className="text-xs text-slate-400">Generated 2026-09-02</span>
              </div>
              <h2 className="text-xl font-bold text-white">ForesightAI Comprehensive Risk & Model Validation Dossier</h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                Includes full XGBoost ROC-AUC breakdown (0.8694), SHAP feature importance waterfalls, Monte Carlo stress-testing outcomes across 10,000 draws, and executive decision-center action items.
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button 
                variant="secondary" 
                size="sm" 
                className="gap-1.5 text-xs font-semibold bg-white text-slate-900 hover:bg-slate-100"
                onClick={() => handleDownload('Master Dossier')}
              >
                <Download className="h-3.5 w-3.5" /> Download Full PDF
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filter Tabs */}
      <div className="flex gap-2 flex-wrap">
        {['All', 'Risk Audit', 'Model Performance', 'Executive Summary', 'Scenario Stress Test'].map((t) => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              filterType === t
                ? 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 shadow-sm'
                : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Reports Table */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Generated Reports Archive</CardTitle>
          <CardDescription className="text-xs">Immutable snapshots of risk models, metrics, and simulations</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Report Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Key Highlights</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>File Size</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((item) => (
                <TableRow key={item.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                  <TableCell className="font-medium text-slate-900 dark:text-slate-100">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-primary shrink-0" />
                      <div>
                        <div>{item.title}</div>
                        <div className="text-xs text-slate-400 font-mono">{item.id} • {item.author}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">
                      {item.type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-slate-600 dark:text-slate-400 max-w-xs truncate">
                    {item.highlights}
                  </TableCell>
                  <TableCell className="text-xs text-slate-500 whitespace-nowrap">
                    {item.generatedAt}
                  </TableCell>
                  <TableCell className="text-xs font-mono text-slate-500">
                    {item.size}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="gap-1 text-xs" 
                      onClick={() => handleDownload(item.title)}
                    >
                      <Download className="h-3.5 w-3.5" /> PDF
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
