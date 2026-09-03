import * as React from 'react';
import { 
  Sparkles, 
  ArrowRight 
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useNavigate } from 'react-router-dom';

interface PredictionCardData {
  id: string;
  title: string;
  category: string;
  predictedOutcome: string;
  confidence: number;
  riskLevel: 'Low' | 'Medium' | 'High';
  trend: 'improving' | 'deteriorating' | 'stable';
  lastUpdated: string;
  probability: number;
  sparkline: number[];
  factors: string[];
}

const PREDICTIONS: PredictionCardData[] = [
  {
    id: 'PRED-101',
    title: 'Commercial Loan #84920 Underwriting',
    category: 'Credit Risk',
    predictedOutcome: 'Approved (Low Default Risk)',
    confidence: 96.4,
    riskLevel: 'Low',
    trend: 'improving',
    lastUpdated: '2 mins ago',
    probability: 3.6,
    sparkline: [4.8, 4.5, 4.2, 3.9, 3.6],
    factors: ['Credit Score 780', 'DTI 22%', 'Employment 12y'],
  },
  {
    id: 'PRED-102',
    title: 'Q4 Supply Chain Resiliency',
    category: 'Operations',
    predictedOutcome: 'Moderate Vulnerability Shock',
    confidence: 84.1,
    riskLevel: 'Medium',
    trend: 'deteriorating',
    lastUpdated: '14 mins ago',
    probability: 24.8,
    sparkline: [18.2, 19.5, 21.0, 23.4, 24.8],
    factors: ['Lead Time +14d', 'Port Congestion', 'Fuel +12%'],
  },
  {
    id: 'PRED-103',
    title: 'Retail Real Estate Portfolio VaR',
    category: 'Market Risk',
    predictedOutcome: 'Capital Reserve Breached',
    confidence: 91.8,
    riskLevel: 'High',
    trend: 'deteriorating',
    lastUpdated: '32 mins ago',
    probability: 41.2,
    sparkline: [22.0, 26.5, 31.0, 37.8, 41.2],
    factors: ['Interest Rate +150bps', 'Occupancy -8%', 'Cap Rates 6.8%'],
  },
  {
    id: 'PRED-104',
    title: 'SME Working Capital Line #3319',
    category: 'Credit Risk',
    predictedOutcome: 'Conditional Approval (DTI Cap)',
    confidence: 88.5,
    riskLevel: 'Medium',
    trend: 'stable',
    lastUpdated: '1 hour ago',
    probability: 14.5,
    sparkline: [14.8, 14.2, 14.6, 14.4, 14.5],
    factors: ['Revenue Growth +8%', 'Debt Service 1.25x'],
  },
  {
    id: 'PRED-105',
    title: 'Liquidity Stress Under Crisis Shock',
    category: 'Treasury',
    predictedOutcome: 'Buffer Intact (Surplus $4.2M)',
    confidence: 98.1,
    riskLevel: 'Low',
    trend: 'improving',
    lastUpdated: '2 hours ago',
    probability: 1.9,
    sparkline: [3.4, 2.9, 2.5, 2.1, 1.9],
    factors: ['Tier-1 Ratio 14.2%', 'Liquid Assets $45M'],
  },
  {
    id: 'PRED-106',
    title: 'Energy Commodities Exposure',
    category: 'Commodities',
    predictedOutcome: 'Volatile Drawdown Risk',
    confidence: 76.9,
    riskLevel: 'High',
    trend: 'deteriorating',
    lastUpdated: '3 hours ago',
    probability: 38.5,
    sparkline: [25.0, 28.0, 33.2, 36.1, 38.5],
    factors: ['Brent Spread Volatility', 'Refining Margins'],
  }
];

export function ConfidenceGauge({ value, label }: { value: number; label: string }) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference * 0.75;

  const colorClass = 
    value >= 90 ? 'text-emerald-500 stroke-emerald-500' :
    value >= 70 ? 'text-amber-500 stroke-amber-500' :
    value >= 50 ? 'text-orange-500 stroke-orange-500' :
    'text-rose-500 stroke-rose-500';

  return (
    <div className="flex flex-col items-center justify-center p-3">
      <div className="relative w-28 h-28 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-135" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r={radius}
            className="stroke-slate-200 dark:stroke-slate-800"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference * 0.75}
          />
          <circle
            cx="50"
            cy="50"
            r={radius}
            className={`${colorClass} transition-all duration-1000 ease-out`}
            strokeWidth="8"
            strokeDasharray={circumference * 0.75}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-xl font-bold font-mono text-slate-900 dark:text-slate-50">{value}%</span>
          <span className="text-[10px] text-slate-400 font-medium">Confidence</span>
        </div>
      </div>
      <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 mt-1">{label}</span>
    </div>
  );
}

export function PredictionCards() {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = React.useState('All');

  const filtered = activeCategory === 'All' 
    ? PREDICTIONS 
    : PREDICTIONS.filter(p => p.category === activeCategory);

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">AI Prediction Engine</h1>
            <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
              Autonomous Real-time Scoring
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Production ML inference feeds across credit, treasury, macroeconomic shocks, and supply chains.
          </p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" onClick={() => navigate('/prediction')} className="gap-1.5 text-xs">
            <Sparkles className="h-3.5 w-3.5" /> New Model Run
          </Button>
        </div>
      </div>

      {/* Hero AI Confidence Gauges Strip */}
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 via-transparent to-indigo-500/5">
        <CardContent className="p-4 grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-slate-100 dark:divide-slate-800">
          <ConfidenceGauge value={96.4} label="Prediction Confidence" />
          <ConfidenceGauge value={94.8} label="Model Benchmark Reliability" />
          <ConfidenceGauge value={98.1} label="Data Pipeline Integrity" />
        </CardContent>
      </Card>

      {/* Category Pills */}
      <div className="flex gap-1.5 flex-wrap">
        {['All', 'Credit Risk', 'Market Risk', 'Operations', 'Treasury', 'Commodities'].map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
              activeCategory === cat
                ? 'bg-primary text-white shadow-sm'
                : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Prediction Cards Grid */}
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((item) => (
          <Card 
            key={item.id} 
            className="flex flex-col justify-between hover:shadow-lg hover:border-primary/40 transition-all duration-200 bg-white/80 dark:bg-slate-900/80 backdrop-blur"
          >
            <div>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[10px] font-mono">
                    {item.category}
                  </Badge>
                  <div className="flex items-center gap-1 text-[11px] text-slate-400 font-mono">
                    {item.lastUpdated}
                  </div>
                </div>
                <CardTitle className="text-base mt-2 text-slate-900 dark:text-slate-50 leading-snug">
                  {item.title}
                </CardTitle>
                <CardDescription className="text-xs font-mono">{item.id}</CardDescription>
              </CardHeader>

              <CardContent className="space-y-3.5 pb-2">
                <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-950/60 border border-slate-100 dark:border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500 font-medium">Outcome</span>
                    <Badge 
                      variant="outline" 
                      className={`text-[10px] ${
                        item.riskLevel === 'High' ? 'border-rose-500 text-rose-600 bg-rose-50 dark:bg-rose-950/40' :
                        item.riskLevel === 'Medium' ? 'border-amber-500 text-amber-600 bg-amber-50 dark:bg-amber-950/40' :
                        'border-emerald-500 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40'
                      }`}
                    >
                      {item.riskLevel} Risk
                    </Badge>
                  </div>
                  <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                    {item.predictedOutcome}
                  </div>
                </div>

                {/* Probability Meter */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-500">Loss / Stress Probability</span>
                    <span className="font-bold text-slate-900 dark:text-slate-100">{item.probability}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-700 ${
                        item.riskLevel === 'High' ? 'bg-rose-500' :
                        item.riskLevel === 'Medium' ? 'bg-amber-500' :
                        'bg-emerald-500'
                      }`}
                      style={{ width: `${item.probability}%` }}
                    />
                  </div>
                </div>

                {/* Contributing Features */}
                <div className="flex flex-wrap gap-1 pt-1">
                  {item.factors.map((f, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-mono">
                      {f}
                    </span>
                  ))}
                </div>
              </CardContent>
            </div>

            <CardFooter className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-2">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-mono font-bold text-primary">{item.confidence}%</span>
                <span className="text-[10px] text-slate-400">Confidence</span>
              </div>
              <div className="flex gap-1.5">
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="h-7 text-[11px] gap-1 px-2.5"
                  onClick={() => navigate('/decisions')}
                >
                  Action
                </Button>
                <Button 
                  size="sm" 
                  className="h-7 text-[11px] gap-1 px-2.5"
                  onClick={() => navigate('/prediction')}
                >
                  Explain <ArrowRight className="h-3 w-3" />
                </Button>
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
