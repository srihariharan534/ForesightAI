import * as React from 'react';
import { 
  Upload, 
  FileSpreadsheet, 
  ArrowDownToLine, 
  Table as TableIcon,
  Zap,
  ArrowRight,
  CheckCircle2
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { useToast } from '../components/ui/Toast';

interface DatasetItem {
  id: string;
  name: string;
  format: string;
  rows: number;
  columns: number;
  size: string;
  targetCol: string;
  updatedAt: string;
  status: 'Ready' | 'Validated' | 'Processing';
  qualityScore: number;
}

const DATASETS_LIST: DatasetItem[] = [
  {
    id: 'DS-01',
    name: 'sample_data.csv (Active Training Data)',
    format: 'CSV',
    rows: 1000,
    columns: 11,
    size: '63.8 KB',
    targetCol: 'target (Binary Default)',
    updatedAt: '2026-09-03',
    status: 'Validated',
    qualityScore: 98
  },
  {
    id: 'DS-02',
    name: 'sample_prediction.csv (Inference Test Batch)',
    format: 'CSV',
    rows: 22,
    columns: 7,
    size: '1.8 KB',
    targetCol: 'severity',
    updatedAt: '2026-09-02',
    status: 'Ready',
    qualityScore: 95
  },
  {
    id: 'DS-03',
    name: 'sample_simulation.csv (Monte Carlo Shocks)',
    format: 'CSV',
    rows: 15,
    columns: 6,
    size: '1.1 KB',
    targetCol: 'stress_impact',
    updatedAt: '2026-08-31',
    status: 'Ready',
    qualityScore: 92
  },
  {
    id: 'DS-04',
    name: 'sample_risk.csv (Geographic Zone Risk)',
    format: 'CSV',
    rows: 8,
    columns: 4,
    size: '388 B',
    targetCol: 'risk_level',
    updatedAt: '2026-08-30',
    status: 'Ready',
    qualityScore: 100
  }
];

const PREVIEW_ROWS = [
  { age: 23, income: '$80,797', credit_score: 480, years_employed: 30, loan_amount: '$40,870', region: 'North', education: 'Bachelor', target: 0 },
  { age: 62, income: '$56,647', credit_score: 591, years_employed: 4, loan_amount: '$32,943', region: 'West', education: 'High School', target: 0 },
  { age: 55, income: '$65,453', credit_score: 403, years_employed: 16, loan_amount: '$25,193', region: 'East', education: 'Part-Time', target: 0 },
  { age: 43, income: '$53,977', credit_score: 785, years_employed: 0, loan_amount: '$19,467', region: 'Central', education: 'Bachelor', target: 0 },
  { age: 42, income: '$51,932', credit_score: 700, years_employed: 18, loan_amount: '$19,801', region: 'North', education: 'Part-Time', target: 0 },
];

export function Datasets() {
  const [datasets, setDatasets] = React.useState<DatasetItem[]>(DATASETS_LIST);
  const [selectedDataset, setSelectedDataset] = React.useState<DatasetItem>(DATASETS_LIST[0]);
  const [isUploading, setIsUploading] = React.useState<boolean>(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setTimeout(() => {
      const newDataset: DatasetItem = {
        id: `DS-0${datasets.length + 1}`,
        name: file.name,
        format: file.name.endsWith('.csv') ? 'CSV' : 'JSON',
        rows: 500,
        columns: 9,
        size: `${(file.size / 1024).toFixed(1)} KB`,
        targetCol: 'target',
        updatedAt: 'Just now',
        status: 'Validated',
        qualityScore: 97
      };
      setDatasets([newDataset, ...datasets]);
      setSelectedDataset(newDataset);
      setIsUploading(false);
      toast({
        title: 'Dataset Ingested',
        description: `Successfully validated ${file.name} (500 rows, 0 null values).`,
        type: 'success',
      });
    }, 1200);
  };

  return (
    <div className="space-y-6 animate-in">
      {/* Hidden File Input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        className="hidden" 
        accept=".csv,.json"
        onChange={handleFileChange}
      />

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Datasets</h1>
            <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
              Feature Store Ready
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Ingest, validate, preview, and preprocess raw training data and test batches.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline"
            className="gap-1.5 text-xs border-primary/40 text-primary hover:bg-primary/10"
            onClick={() => {
              toast({
                title: 'MLOps Retraining Triggered',
                description: 'Cross-validating XGBoost 100-estimator pipeline on active dataset.',
                type: 'success'
              });
            }}
          >
            <Zap className="h-3.5 w-3.5 text-amber-500" />
            Trigger Retraining Pipeline
          </Button>
          <Button 
            className="gap-2 text-xs"
            onClick={handleUploadClick}
            disabled={isUploading}
          >
            <Upload className="h-3.5 w-3.5" /> 
            {isUploading ? 'Validating Dataset...' : 'Upload New Dataset'}
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-primary">
          <CardContent className="pt-4">
            <p className="text-xs text-slate-500 font-medium uppercase">Datasets Registered</p>
            <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-50">{datasets.length} Files</h3>
            <p className="text-xs text-slate-400 mt-2">Datasets located in /datasets/</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="pt-4">
            <p className="text-xs text-slate-500 font-medium uppercase">Data Quality Health</p>
            <h3 className="text-2xl font-bold mt-1 text-emerald-600">98.4%</h3>
            <p className="text-xs text-emerald-600 font-medium mt-2">Passed schema validation</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="pt-4">
            <p className="text-xs text-slate-500 font-medium uppercase">Total Row Volume</p>
            <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-50">1,045 Records</h3>
            <p className="text-xs text-slate-400 mt-2">Sample and production sets</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="pt-4">
            <p className="text-xs text-slate-500 font-medium uppercase">Preprocessing Engine</p>
            <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-50">StandardScaler</h3>
            <p className="text-xs text-slate-400 mt-2">Median Impute + Label Encoding</p>
          </CardContent>
        </Card>
      </div>

      {/* End-to-End MLOps Pipeline Flow Strip */}
      <Card className="border-primary/30 bg-primary/5 dark:bg-primary/10">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-primary flex items-center gap-1.5 font-mono">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              Automated MLOps Production Pipeline (Status: Healthy)
            </span>
            <Badge variant="outline" className="text-[10px] font-mono text-primary border-primary/40">
              CI/CD MLflow Synchronized
            </Badge>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            {['Ingest Raw CSV', 'Null Imputation', 'Feature Engineering', 'XGBoost Training', '100-Fold CV', 'SHAP Attributions', 'Canary Rollout'].map((step, idx) => (
              <React.Fragment key={idx}>
                <div className="px-3 py-1.5 rounded-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 font-medium flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  {step}
                </div>
                {idx < 6 && <ArrowRight className="h-3.5 w-3.5 text-slate-400 shrink-0" />}
              </React.Fragment>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Datasets Table */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Repository Datasets</CardTitle>
          <CardDescription className="text-xs">Click a dataset to view its schema preview and statistical distribution</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Dataset Name</TableHead>
                <TableHead>Format</TableHead>
                <TableHead>Rows</TableHead>
                <TableHead>Columns</TableHead>
                <TableHead>Target Variable</TableHead>
                <TableHead>Quality Score</TableHead>
                <TableHead>Size</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {datasets.map((ds) => (
                <TableRow 
                  key={ds.id} 
                  onClick={() => setSelectedDataset(ds)}
                  className={`cursor-pointer transition-colors ${
                    selectedDataset.id === ds.id 
                      ? 'bg-primary/5 dark:bg-primary/10' 
                      : 'hover:bg-slate-50/60 dark:hover:bg-slate-800/40'
                  }`}
                >
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <FileSpreadsheet className="h-4 w-4 text-primary shrink-0" />
                      <div>
                        <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">{ds.name}</div>
                        <div className="text-xs text-slate-400 font-mono">{ds.id} • Updated {ds.updatedAt}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-xs font-mono">{ds.format}</TableCell>
                  <TableCell className="text-xs font-mono font-medium">{ds.rows.toLocaleString()}</TableCell>
                  <TableCell className="text-xs font-mono">{ds.columns}</TableCell>
                  <TableCell className="text-xs font-mono text-primary font-medium">{ds.targetCol}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="border-emerald-500/50 text-emerald-600 font-mono text-xs">
                      {ds.qualityScore}%
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs font-mono text-slate-500">{ds.size}</TableCell>
                  <TableCell className="text-right">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-xs h-8"
                      onClick={(e) => {
                        e.stopPropagation();
                        toast({ title: 'Downloading', description: `Exporting ${ds.name}`, type: 'default' });
                      }}
                    >
                      <ArrowDownToLine className="h-3.5 w-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dataset Schema Preview */}
      <Card>
        <CardHeader className="pb-3 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              <TableIcon className="h-4 w-4 text-primary" /> Preview: {selectedDataset.name}
            </CardTitle>
            <CardDescription className="text-xs">
              First 5 sample records loaded from active dataset
            </CardDescription>
          </div>
          <Badge variant="outline" className="font-mono text-xs">
            {selectedDataset.rows} Total Records
          </Badge>
        </CardHeader>
        <CardContent className="p-0 overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Age</TableHead>
                <TableHead>Income</TableHead>
                <TableHead>Credit Score</TableHead>
                <TableHead>Years Employed</TableHead>
                <TableHead>Loan Amount</TableHead>
                <TableHead>Region</TableHead>
                <TableHead>Education</TableHead>
                <TableHead>Target Label</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {PREVIEW_ROWS.map((r, i) => (
                <TableRow key={i} className="text-xs font-mono">
                  <TableCell>{r.age}</TableCell>
                  <TableCell className="font-semibold">{r.income}</TableCell>
                  <TableCell>{r.credit_score}</TableCell>
                  <TableCell>{r.years_employed}</TableCell>
                  <TableCell>{r.loan_amount}</TableCell>
                  <TableCell className="font-sans">{r.region}</TableCell>
                  <TableCell className="font-sans">{r.education}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-400">
                      {r.target} (Good)
                    </Badge>
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
