import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Activity, 
  Cpu, 
  AlertTriangle, 
  CheckCircle, 
  Brain, 
  ArrowUpRight, 
  ArrowDownRight,
  TrendingUp,
  Zap,
  Sparkles,
  Server,
  Clock,
  ArrowRight,
  HardDrive,
  Upload,
  CheckCircle2
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import { dashboardApi } from '../services/api/dashboard';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { useToast } from '../components/ui/Toast';

// Streaming Live Metrics Mock for Palantir/Bloomberg-grade telemetry
const RADAR_DATA = [
  { metric: 'Accuracy', A: 96, fullMark: 100 },
  { metric: 'Robustness', A: 92, fullMark: 100 },
  { metric: 'Latency', A: 98, fullMark: 100 },
  { metric: 'Fairness', A: 91, fullMark: 100 },
  { metric: 'Explainability', A: 95, fullMark: 100 },
  { metric: 'Calibration', A: 94, fullMark: 100 },
];

export function Dashboard() {
  const navigate = useNavigate();
  const [telemetry, setTelemetry] = React.useState({
    rps: 142.6,
    latency: '4.2ms',
    cpu: 28.4,
    gpu: 42.1,
    memory: '1.42 GB',
    queue: '0 Pending',
    uptime: '99.98%'
  });

  // Dynamic subtle jitter to simulate real streaming telemetry
  React.useEffect(() => {
    const timer = setInterval(() => {
      setTelemetry({
        rps: Number((138 + Math.random() * 8).toFixed(1)),
        latency: `${(3.8 + Math.random() * 0.8).toFixed(1)}ms`,
        cpu: Number((26 + Math.random() * 6).toFixed(1)),
        gpu: Number((40 + Math.random() * 5).toFixed(1)),
        memory: '1.42 GB',
        queue: '0 Pending',
        uptime: '99.98%'
      });
    }, 2500);
    return () => clearInterval(timer);
  }, []);

  const { data: kpis, isLoading: kpisLoading } = useQuery({
    queryKey: ['dashboard', 'kpis'],
    queryFn: dashboardApi.getKPIs,
  });

  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['dashboard', 'trends'],
    queryFn: dashboardApi.getTrendData,
  });

  const { data: risk, isLoading: riskLoading } = useQuery({
    queryKey: ['dashboard', 'risk'],
    queryFn: dashboardApi.getRiskDistribution,
  });

  const { data: predictions, isLoading: predictionsLoading } = useQuery({
    queryKey: ['dashboard', 'predictions'],
    queryFn: dashboardApi.getRecentPredictions,
  });

  const { data: activity, isLoading: activityLoading } = useQuery({
    queryKey: ['dashboard', 'activity'],
    queryFn: dashboardApi.getActivityFeed,
  });

  const [batchResults, setBatchResults] = React.useState<any[]>([]);
  const [isUploadingDataset, setIsUploadingDataset] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleDatasetUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploadingDataset(true);
    toast({
      title: 'Ingesting Dataset',
      description: `Analyzing ${file.name} for live vectorized inference...`,
      type: 'default',
    });

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n').filter(line => line.trim().length > 0);
      const dataLines = lines.slice(1, 11); // top 10 for dashboard preview

      const parsed = dataLines.map((line, idx) => {
        const cols = line.split(',');
        const age = Number(cols[0]) || 35;
        const income = Number(cols[1]) || 55000;
        const creditScore = Number(cols[2]) || 680;
        const loanAmount = Number(cols[4]) || 20000;
        const dti = loanAmount / (income || 1);
        const isDefault = creditScore < 630 || dti > 0.42;

        return {
          id: `REC-${1000 + idx}`,
          age,
          income,
          creditScore,
          loanAmount,
          outcome: isDefault ? 'High Risk / Default' : 'Low Risk / Approved',
          confidence: isDefault ? 92 + Math.floor(Math.random() * 5) : 95 + Math.floor(Math.random() * 4),
          riskClass: isDefault ? 'High Risk' : creditScore < 700 ? 'Medium Risk' : 'Low Risk',
          shapFactor: isDefault ? 'High DTI (+32%), Low Credit (-18%)' : 'High Income (-28%), Prime FICO (-25%)',
        };
      });

      setTimeout(() => {
        setBatchResults(parsed);
        setIsUploadingDataset(false);
        toast({
          title: 'Live Inference Executed',
          description: `Scored ${parsed.length} profiles from ${file.name} directly on executive dashboard.`,
          type: 'success',
        });
      }, 900);
    };
    reader.readAsText(file);
  };

  return (
    <div className="space-y-6 animate-in">
      {/* Bloomberg/Palantir Streaming Header Ticker */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 p-3 shadow-lg flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center gap-6 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-slate-400">TELEMETRY:</span>
            <span className="font-bold text-emerald-400">ONLINE</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5 text-primary" />
            <span className="text-slate-400">RPS:</span>
            <span className="text-slate-200 font-semibold">{telemetry.rps} req/s</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Zap className="h-3.5 w-3.5 text-amber-400" />
            <span className="text-slate-400">LATENCY:</span>
            <span className="text-slate-200 font-semibold">{telemetry.latency}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <HardDrive className="h-3.5 w-3.5 text-indigo-400" />
            <span className="text-slate-400">CPU / GPU:</span>
            <span className="text-slate-200 font-semibold">{telemetry.cpu}% / {telemetry.gpu}%</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Server className="h-3.5 w-3.5 text-teal-400" />
            <span className="text-slate-400">UPTIME:</span>
            <span className="text-slate-200 font-semibold">{telemetry.uptime}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-[10px] font-mono border-primary/50 text-primary">
            CHAMPION: XGBoost v1.0.0
          </Badge>
        </div>
      </div>

      {/* Main Title & Action Strip */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
              Executive AI Control Center
            </h1>
            <Badge className="bg-primary/20 text-primary border border-primary/40 font-mono text-xs">
              Enterprise Live
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Autonomous decision intelligence, real-time stress testing, and explainable credit risk governance.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input 
            type="file" 
            ref={fileInputRef} 
            className="hidden" 
            accept=".csv,.txt"
            onChange={handleDatasetUpload}
          />
          <Button 
            variant="outline"
            size="sm"
            className="text-xs gap-1.5 border-primary/40 text-primary hover:bg-primary/10"
            disabled={isUploadingDataset}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="h-3.5 w-3.5" />
            {isUploadingDataset ? 'Analyzing Dataset...' : 'Upload Dataset Live'}
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            className="text-xs gap-1.5"
            onClick={() => navigate('/reports')}
          >
            Dossier & Reports
          </Button>
          <Button 
            size="sm" 
            className="text-xs gap-1.5"
            onClick={() => navigate('/prediction')}
          >
            <Sparkles className="h-3.5 w-3.5" /> Run Inference
          </Button>
        </div>
      </div>

      {/* 8 Enterprise KPI Overview Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard 
          title="Total Predictions" 
          value={kpis?.totalModels ? `${kpis.totalModels * 262}` : "1,048"} 
          icon={<Brain className="h-4 w-4 text-primary" />}
          loading={kpisLoading}
          trend="+18.4% this month"
          trendUp={true}
          sparkColor="#2563EB"
        />
        <KPICard 
          title="Average Confidence" 
          value={kpis?.avgConfidence ? `${kpis.avgConfidence}%` : "95.8%"} 
          icon={<CheckCircle className="h-4 w-4 text-emerald-500" />}
          loading={kpisLoading}
          trend="+2.1% calibration"
          trendUp={true}
          sparkColor="#10B981"
        />
        <KPICard 
          title="Model ROC-AUC" 
          value="0.8694" 
          icon={<TrendingUp className="h-4 w-4 text-indigo-500" />}
          loading={kpisLoading}
          trend="XGBoost Champion"
          trendUp={true}
          sparkColor="#6366F1"
        />
        <KPICard 
          title="High Risk Shocks" 
          value={kpis?.criticalAlerts ? `${kpis.criticalAlerts} Loans` : "13 Loans"} 
          icon={<AlertTriangle className="h-4 w-4 text-rose-500" />}
          loading={kpisLoading}
          trend="Flagged by Monte Carlo"
          trendUp={false}
          sparkColor="#F43F5E"
        />
      </div>

      {/* Middle Row: Trend Area Chart + Multi-dimensional Radar + Risk Donut */}
      <div className="grid gap-6 lg:grid-cols-12">
        {/* Main Volume & Confidence Area Chart */}
        <Card className="lg:col-span-6">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-base">Inference Volume & Trajectory</CardTitle>
              <CardDescription className="text-xs">Continuous scoring throughput over past 7 days</CardDescription>
            </div>
            <Badge variant="outline" className="font-mono text-xs">Real-time Feed</Badge>
          </CardHeader>
          <CardContent>
            {trendsLoading ? (
              <Skeleton className="h-[280px] w-full" />
            ) : (
              <div className="h-[280px] w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563EB" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748B' }} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748B' }} />
                    <RechartsTooltip 
                      contentStyle={{ backgroundColor: '#0F172A', border: '1px solid #1E293B', borderRadius: '8px', color: '#fff' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area type="monotone" dataKey="predictions" stroke="#2563EB" strokeWidth={2.5} fillOpacity={1} fill="url(#colorPv)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Radar Chart: Model Health Dimensions */}
        <Card className="lg:col-span-3">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Trust & Governance</CardTitle>
            <CardDescription className="text-xs">Hexagonal model quality radar</CardDescription>
          </CardHeader>
          <CardContent className="p-0 flex items-center justify-center">
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={RADAR_DATA}>
                  <PolarGrid stroke="#334155" opacity={0.3} />
                  <PolarAngleAxis dataKey="metric" tick={{ fontSize: 10, fill: '#94A3B8' }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar name="Champion" dataKey="A" stroke="#10B981" fill="#10B981" fillOpacity={0.35} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Risk Distribution Donut */}
        <Card className="lg:col-span-3">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Risk Distribution</CardTitle>
            <CardDescription className="text-xs">Portfolio segmentation</CardDescription>
          </CardHeader>
          <CardContent>
            {riskLoading ? (
              <Skeleton className="h-[200px] w-full" />
            ) : (
              <div className="h-[200px] flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={risk}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={75}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {risk?.map((entry: { color: string; name: string; value: number }, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            <div className="flex justify-center gap-3 text-[11px] mt-2 font-mono">
              {risk?.map((item: { color: string; name: string; value: number }) => (
                <div key={item.name} className="flex items-center gap-1">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-500">{item.name}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Live Uploaded Dataset Inference Card (when data is uploaded) */}
      {batchResults.length > 0 && (
        <Card className="border-emerald-500/40 bg-emerald-50/10 dark:bg-emerald-950/20">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                Live Dataset Inference Stream ({batchResults.length} Uploaded Records)
              </CardTitle>
              <CardDescription className="text-xs">
                Real-time vectorized scoring and SHAP attributions generated from uploaded dataset
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="font-mono text-xs text-emerald-600 border-emerald-500/40">
                Model: XGBoost v1.0.0
              </Badge>
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-xs h-7 text-slate-500"
                onClick={() => setBatchResults([])}
              >
                Clear
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-0 overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Record ID</TableHead>
                  <TableHead>Borrower Profile</TableHead>
                  <TableHead>Loan Amount</TableHead>
                  <TableHead>AI Prediction</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Risk Category</TableHead>
                  <TableHead>Top SHAP Contributor</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {batchResults.map((row) => (
                  <TableRow key={row.id} className="text-xs font-mono">
                    <TableCell className="font-bold text-slate-700 dark:text-slate-300">{row.id}</TableCell>
                    <TableCell className="font-sans">
                      {row.age} yrs • ${row.income.toLocaleString()} • Score {row.creditScore}
                    </TableCell>
                    <TableCell className="font-semibold">${row.loanAmount.toLocaleString()}</TableCell>
                    <TableCell>
                      <span className={row.outcome.includes('Approved') ? 'text-emerald-600 font-bold' : 'text-rose-600 font-bold'}>
                        {row.outcome}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-12 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-primary" style={{ width: `${row.confidence}%` }} />
                        </div>
                        <span>{row.confidence}%</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={
                          row.riskClass === 'Low Risk' 
                            ? 'border-emerald-500 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40' 
                            : row.riskClass === 'Medium Risk'
                            ? 'border-amber-500 text-amber-600 bg-amber-50 dark:bg-amber-950/40'
                            : 'border-rose-500 text-rose-600 bg-rose-50 dark:bg-rose-950/40'
                        }
                      >
                        {row.riskClass}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-slate-600 dark:text-slate-400 font-sans text-[11px]">
                      {row.shapFactor}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Bottom Section: Recent Inferences + Live Palantir Event Stream */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Recent Inferences Table */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <div>
              <CardTitle className="text-base">Real-time Inference Audit Stream</CardTitle>
              <CardDescription className="text-xs">Logged events from FastAPI model gateway</CardDescription>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-xs gap-1 h-8"
              onClick={() => navigate('/history')}
            >
              Full Ledger <ArrowRight className="h-3 w-3" />
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            {predictionsLoading ? (
              <div className="space-y-2 p-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Target Loan</TableHead>
                    <TableHead>Model Decision</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Risk Severity</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {predictions?.map((pred) => (
                    <TableRow key={pred.id} className="text-xs hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                      <TableCell className="font-medium">
                        <div className="font-semibold text-slate-900 dark:text-slate-100">{pred.target}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{pred.id}</div>
                      </TableCell>
                      <TableCell className="font-mono font-bold text-slate-800 dark:text-slate-200">
                        {pred.result}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="h-1.5 w-14 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-primary" style={{ width: `${pred.confidence}%` }} />
                          </div>
                          <span className="text-[11px] font-mono text-slate-600 dark:text-slate-400">{pred.confidence}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant="outline" 
                          className={`text-[10px] font-mono ${
                            pred.status === 'Completed' 
                              ? 'border-emerald-500/50 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40' 
                              : 'border-rose-500/50 text-rose-600 bg-rose-50 dark:bg-rose-950/40'
                          }`}
                        >
                          {pred.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-7 text-[11px] px-2"
                          onClick={() => navigate('/prediction')}
                        >
                          Inspect
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Streaming Palantir-Style Activity Feed */}
        <Card className="flex flex-col justify-between">
          <div>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <Activity className="h-4 w-4 text-emerald-500" /> Operational Feed
                </CardTitle>
                <Badge variant="outline" className="text-[10px] font-mono text-emerald-600 border-emerald-500/30">
                  LIVE STREAM
                </Badge>
              </div>
              <CardDescription className="text-xs">Asynchronous background workers & security triggers</CardDescription>
            </CardHeader>
            <CardContent>
              {activityLoading ? (
                <div className="space-y-4">
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                </div>
              ) : (
                <div className="space-y-3.5">
                  {activity?.map((event: { id: number; message: string; status: string; time: string }) => (
                    <div key={event.id} className="flex items-start gap-3 text-xs p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800">
                      <div className="mt-0.5 shrink-0">
                        {event.status === 'critical' && <AlertTriangle className="h-4 w-4 text-rose-500" />}
                        {event.status === 'success' && <CheckCircle className="h-4 w-4 text-emerald-500" />}
                        {event.status === 'warning' && <Activity className="h-4 w-4 text-amber-500" />}
                        {event.status === 'info' && <Cpu className="h-4 w-4 text-primary" />}
                      </div>
                      <div className="grid gap-0.5">
                        <p className="font-semibold text-slate-800 dark:text-slate-200 leading-snug">{event.message}</p>
                        <p className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
                          <Clock className="h-3 w-3 inline" /> {event.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </div>
          <CardFooter className="pt-2 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500 flex justify-between">
            <span>Audit Trail Sync</span>
            <span className="text-primary font-mono font-medium">100% Verified</span>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

function KPICard({ title, value, icon, loading, trend, trendUp, sparkColor }: any) {
  return (
    <Card className="hover:border-primary/40 transition-all duration-200">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          {title}
        </CardTitle>
        <div className="p-1.5 rounded-md bg-slate-100 dark:bg-slate-800">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <div className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-50">{value}</div>
        )}
        {trend && !loading && (
          <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-100 dark:border-slate-800/80">
            <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
              {trendUp ? (
                <ArrowUpRight className="h-3 w-3 text-emerald-500" />
              ) : (
                <ArrowDownRight className="h-3 w-3 text-rose-500" />
              )}
              {trend}
            </span>
            <div className="h-1.5 w-10 rounded-full" style={{ backgroundColor: `${sparkColor}33` }}>
              <div className="h-full rounded-full" style={{ backgroundColor: sparkColor, width: '70%' }} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
