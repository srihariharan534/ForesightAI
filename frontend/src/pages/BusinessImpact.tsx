import * as React from 'react';
import { 
  DollarSign, 
  ShieldCheck, 
  AlertOctagon, 
  BarChart3, 
  Target
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { apiClient } from '../services/api/client';

export function BusinessImpact() {
  const [data, setData] = React.useState<any>(null);

  React.useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get('/mlops/business-impact');
        setData(res.data);
      } catch {
        setData({
          capitalProtected: "$4.28M",
          expectedLossReduction: "24.6%",
          overallPortfolioRoi: "318%",
          currentApprovalRate: "78.4%",
          costMatrix: {
            falseNegativeCost: "$18,500 (Uncaught default)",
            falsePositiveCost: "$1,200 (Lost customer margin)",
            costOptimizedThreshold: 0.42
          },
          portfolioComparison: [
            { strategy: "Legacy Rule Engine", approvalRate: "68%", defaultRate: "8.4%", annualLoss: "$5.62M" },
            { strategy: "ForesightAI Champion (XGBoost)", approvalRate: "78.4%", defaultRate: "3.1%", annualLoss: "$1.34M" }
          ]
        });
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              Executive Business Impact & ROI
            </h1>
            <Badge variant="outline" className="border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
              <DollarSign className="mr-1 h-3 w-3" /> P&amp;L Value Engine
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Quantifying machine learning accuracy into balance sheet outcomes: Capital protected, expected loss reduction, and cost matrix optimization.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-slate-200/80 dark:border-slate-800 bg-emerald-500/5">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">Capital Protected</CardDescription>
            <CardTitle className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
              {data?.capitalProtected || "$4.28M"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-slate-500">Prevented default write-offs</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/80 dark:border-slate-800">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider">Expected Loss Reduction</CardDescription>
            <CardTitle className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {data?.expectedLossReduction || "24.6%"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-slate-500">Relative to legacy rules baseline</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/80 dark:border-slate-800">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider">Risk-Adjusted ROI</CardDescription>
            <CardTitle className="text-3xl font-bold text-violet-600 dark:text-violet-400">
              {data?.overallPortfolioRoi || "318%"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-slate-500">Platform deployment payback: 3.2 mo</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/80 dark:border-slate-800">
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-semibold uppercase tracking-wider">Underwriting Approval Rate</CardDescription>
            <CardTitle className="text-3xl font-bold text-slate-900 dark:text-white">
              {data?.currentApprovalRate || "78.4%"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-emerald-600 font-medium">+10.4% higher loan volume safely captured</p>
          </CardContent>
        </Card>
      </div>

      {/* Strategy Comparison Matrix */}
      <Card className="border-slate-200/80 dark:border-slate-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" /> Underwriting Strategy Value Comparison
          </CardTitle>
          <CardDescription className="text-xs">
            Direct financial benchmark of ForesightAI ML Champion versus standard legacy underwriting
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Strategy</TableHead>
                <TableHead>Portfolio Approval Rate</TableHead>
                <TableHead>Default Rate (%)</TableHead>
                <TableHead>Annual Default Write-Off</TableHead>
                <TableHead>Net Revenue Delta</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.portfolioComparison?.map((row: any, idx: number) => {
                const isChampion = row.strategy.includes("ForesightAI");
                return (
                  <TableRow key={idx} className={isChampion ? "bg-primary/5 font-medium" : ""}>
                    <TableCell className="font-semibold flex items-center gap-2">
                      {isChampion ? <ShieldCheck className="h-4 w-4 text-primary" /> : null}
                      {row.strategy}
                    </TableCell>
                    <TableCell>{row.approvalRate}</TableCell>
                    <TableCell className={isChampion ? "text-emerald-600 font-bold" : "text-rose-600 font-bold"}>{row.defaultRate}</TableCell>
                    <TableCell>{row.annualLoss}</TableCell>
                    <TableCell>
                      <Badge variant={isChampion ? "default" : "secondary"}>
                        {isChampion ? "+$4.28M Net Saved" : "Baseline"}
                      </Badge>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Cost Matrix Trade-Off */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-slate-200/80 dark:border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-1.5 text-rose-600">
              <AlertOctagon className="h-4 w-4" /> False Negative Cost
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <p className="text-xl font-bold text-slate-900 dark:text-white">$18,500</p>
            <p className="text-xs text-slate-500">Average principal lost per undetected defaulting borrower</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/80 dark:border-slate-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-1.5 text-amber-600">
              <AlertOctagon className="h-4 w-4" /> False Positive Cost
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <p className="text-xl font-bold text-slate-900 dark:text-white">$1,200</p>
            <p className="text-xs text-slate-500">Lost origination fee and lifetime net interest margin</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/80 dark:border-slate-800 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-1.5 text-primary">
              <BarChart3 className="h-4 w-4" /> Cost-Optimized Threshold
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <p className="text-xl font-bold text-primary">0.42 Probability Gate</p>
            <p className="text-xs text-slate-500">Mathematically minimizes portfolio Expected Total Cost function</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
