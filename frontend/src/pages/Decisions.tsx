import * as React from 'react';
import { 
  Target, 
  CheckCircle2, 
  TrendingUp, 
  ArrowRight, 
  ShieldCheck, 
  Zap, 
  Sparkles,
  Layers,
  Scale
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useToast } from '../components/ui/Toast';

interface Recommendation {
  id: string;
  category: string;
  title: string;
  description: string;
  impactScore: number;
  confidence: number;
  riskLevel: 'Low' | 'Medium' | 'High';
  status: 'Pending' | 'Approved' | 'Executed';
  actionLabel: string;
  metrics: {
    expectedRoi: string;
    riskReduction: string;
    timeline: string;
  };
}

const INITIAL_RECOMMENDATIONS: Recommendation[] = [
  {
    id: 'REC-01',
    category: 'Credit Underwriting',
    title: 'Adjust DTI Threshold for Tier-2 Borrowers',
    description: 'Based on recent macroeconomic shocks and Monte Carlo default simulation, lowering maximum DTI from 45% to 38% for applicants with credit scores under 620 will reduce portfolio Expected Loss by 14.2%.',
    impactScore: 92,
    confidence: 94.6,
    riskLevel: 'Low',
    status: 'Pending',
    actionLabel: 'Apply Policy Update',
    metrics: {
      expectedRoi: '+14.2% Capital Saved',
      riskReduction: '-220 bps Default Rate',
      timeline: 'Immediate'
    }
  },
  {
    id: 'REC-02',
    category: 'Liquidity Reserve',
    title: 'Increase Stress-Buffer Liquidity Allocation',
    description: 'Scenario analysis indicates a 70% income shock under Financial Crisis models causes severe capital strain. Pre-allocating a 5% contingency reserve cushions downstream defaults.',
    impactScore: 88,
    confidence: 91.2,
    riskLevel: 'Medium',
    status: 'Pending',
    actionLabel: 'Allocate Buffer',
    metrics: {
      expectedRoi: '$2.4M Risk Guard',
      riskReduction: 'Coverage ratio to 1.8x',
      timeline: '2 Weeks'
    }
  },
  {
    id: 'REC-03',
    category: 'Automated Origination',
    title: 'Fast-Track Low-Risk Prime Approvals (Score > 740)',
    description: 'XGBoost feature attribution demonstrates employment tenure > 5 yrs combined with prime credit scores holds 99.1% repayment confidence. Enabling instant approval accelerates conversions by 35%.',
    impactScore: 85,
    confidence: 98.4,
    riskLevel: 'Low',
    status: 'Approved',
    actionLabel: 'Deploy Rule',
    metrics: {
      expectedRoi: '+$640K New Originations',
      riskReduction: 'Zero marginal loss',
      timeline: 'Active'
    }
  },
  {
    id: 'REC-04',
    category: 'Proactive Collections',
    title: 'Early Restructuring Intervention on First Missed Payment',
    description: 'Bayesian probability trajectory signals that initiating proactive loan restructuring on day 15 post-missed payment cuts final default rates from 44% down to 18%.',
    impactScore: 79,
    confidence: 89.0,
    riskLevel: 'High',
    status: 'Pending',
    actionLabel: 'Trigger Outreach',
    metrics: {
      expectedRoi: '+26% Recovery Rate',
      riskReduction: 'Mitigates 380 loans',
      timeline: '3 Days'
    }
  }
];

export function Decisions() {
  const [recommendations, setRecommendations] = React.useState<Recommendation[]>(INITIAL_RECOMMENDATIONS);
  const [activeFilter, setActiveFilter] = React.useState<string>('All');
  const { toast } = useToast();

  const handleExecute = (id: string, title: string) => {
    setRecommendations((prev) =>
      prev.map((rec) =>
        rec.id === id ? { ...rec, status: 'Executed' as const } : rec
      )
    );
    toast({
      title: 'Action Executed',
      description: `Successfully executed policy: "${title}"`,
      type: 'success',
    });
  };

  const filtered = activeFilter === 'All' 
    ? recommendations 
    : recommendations.filter(r => r.category === activeFilter);

  const categories = ['All', 'Credit Underwriting', 'Liquidity Reserve', 'Automated Origination', 'Proactive Collections'];

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Decision Center</h1>
            <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
              <Sparkles className="h-3 w-3 mr-1 inline" /> AI-Prescriptive
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Turn predictions and Monte Carlo scenario simulations into auditable, automated business decisions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2 text-xs" onClick={() => {
            toast({ title: 'Simulation Sync', description: 'Recommendations re-aligned with latest ML models.', type: 'default' });
          }}>
            <Zap className="h-3.5 w-3.5 text-amber-500" /> Re-Compute Policies
          </Button>
        </div>
      </div>

      {/* KPI Overview Strip */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-primary">
          <CardContent className="pt-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Active Prescriptions</p>
                <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-50">4 Policies</h3>
              </div>
              <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
                <Target className="h-5 w-5" />
              </div>
            </div>
            <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-3 font-medium flex items-center gap-1">
              <TrendingUp className="h-3.5 w-3.5" /> 2 pending execution
            </p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="pt-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Avg Decision Confidence</p>
                <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-50">93.3%</h3>
              </div>
              <div className="rounded-lg bg-emerald-500/10 p-2.5 text-emerald-500">
                <ShieldCheck className="h-5 w-5" />
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-3">Calibrated by Bayesian inference</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="pt-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">Expected Capital Impact</p>
                <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-50">$3.04M</h3>
              </div>
              <div className="rounded-lg bg-blue-500/10 p-2.5 text-blue-500">
                <Scale className="h-5 w-5" />
              </div>
            </div>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-3 font-medium">Over next 2 fiscal quarters</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="pt-5">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">System Governance</p>
                <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-50">100% Auditable</h3>
              </div>
              <div className="rounded-lg bg-amber-500/10 p-2.5 text-amber-500">
                <Layers className="h-5 w-5" />
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-3">Full SHAP/LIME traceability</p>
          </CardContent>
        </Card>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2 pt-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveFilter(cat)}
            className={`px-3 py-1.5 text-xs font-medium rounded-full transition-colors ${
              activeFilter === cat
                ? 'bg-primary text-white shadow-sm'
                : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Recommendations Feed */}
      <div className="grid gap-5 lg:grid-cols-2">
        {filtered.map((rec) => (
          <Card key={rec.id} className="relative overflow-hidden flex flex-col justify-between border-slate-200/80 dark:border-slate-800 hover:shadow-md transition-shadow">
            <div>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between gap-2">
                  <Badge variant="outline" className="text-xs font-mono">
                    {rec.category}
                  </Badge>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-slate-500">Confidence:</span>
                    <Badge variant="default" className="bg-emerald-600/90 text-white font-mono text-xs">
                      {rec.confidence}%
                    </Badge>
                    <span
                      className={`inline-block h-2 w-2 rounded-full ${
                        rec.riskLevel === 'Low'
                          ? 'bg-emerald-500'
                          : rec.riskLevel === 'Medium'
                          ? 'bg-amber-500'
                          : 'bg-rose-500'
                      }`}
                      title={`Risk: ${rec.riskLevel}`}
                    />
                  </div>
                </div>
                <CardTitle className="text-lg font-semibold mt-2 text-slate-900 dark:text-slate-100">
                  {rec.title}
                </CardTitle>
                <CardDescription className="text-sm leading-relaxed mt-1 text-slate-600 dark:text-slate-400">
                  {rec.description}
                </CardDescription>
              </CardHeader>

              <CardContent className="pt-0">
                <div className="grid grid-cols-3 gap-2 bg-slate-50 dark:bg-slate-900/80 p-3 rounded-lg border border-slate-100 dark:border-slate-800/80 text-xs">
                  <div>
                    <span className="text-slate-400 block mb-0.5">Expected Impact</span>
                    <span className="font-semibold text-slate-900 dark:text-slate-100">{rec.metrics.expectedRoi}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-0.5">Risk Delta</span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">{rec.metrics.riskReduction}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block mb-0.5">Implementation</span>
                    <span className="font-semibold text-slate-700 dark:text-slate-300">{rec.metrics.timeline}</span>
                  </div>
                </div>
              </CardContent>
            </div>

            <CardFooter className="pt-3 pb-4 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400 font-mono">{rec.id}</span>
                <span className="text-slate-300 dark:text-slate-600">•</span>
                <span className={`font-medium ${rec.status === 'Executed' ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {rec.status === 'Executed' ? 'Policy Executed' : 'Awaiting Confirmation'}
                </span>
              </div>
              <Button
                size="sm"
                disabled={rec.status === 'Executed'}
                variant={rec.status === 'Executed' ? 'outline' : 'default'}
                className="gap-1.5 text-xs font-medium"
                onClick={() => handleExecute(rec.id, rec.title)}
              >
                {rec.status === 'Executed' ? (
                  <>
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> Active in Engine
                  </>
                ) : (
                  <>
                    {rec.actionLabel} <ArrowRight className="h-3.5 w-3.5" />
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
