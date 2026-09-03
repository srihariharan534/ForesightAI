import * as React from 'react';
import { 
  Play, 
  Pause, 
  ChevronRight, 
  ChevronLeft, 
  X, 
  CheckCircle2, 
  Sparkles
} from 'lucide-react';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { useNavigate, useLocation } from 'react-router-dom';

interface TourStep {
  title: string;
  route: string;
  badge: string;
  description: string;
  highlight: string;
}

const TOUR_STEPS: TourStep[] = [
  {
    title: "1. Dataset Validation & Leakage Check",
    route: "/datasets",
    badge: "Data Health",
    description: "Inspect uploaded borrower dataset. Automated schema validation, missing rate audit, and target leakage checks.",
    highlight: "1,000 credit profiles validated with 98% quality index."
  },
  {
    title: "2. Real Multi-Model AutoML Training",
    route: "/models",
    badge: "AutoML Engine",
    description: "Live simultaneous training of XGBoost, LightGBM, and CatBoost with early stopping and ROC-AUC benchmarking.",
    highlight: "XGBoost achieves 96.0% accuracy & 0.8694 ROC-AUC."
  },
  {
    title: "3. Champion Deployment & Registry",
    route: "/models",
    badge: "MLOps",
    description: "Promote the winning XGBoost pipeline to active Production Champion with zero-downtime serving.",
    highlight: "Model artifact serialized and logged to MLflow tracker."
  },
  {
    title: "4. Live Inference & Explainable AI (SHAP)",
    route: "/prediction",
    badge: "XAI / SHAP",
    description: "Run single-profile scoring with TreeExplainer SHAP attribution breakdown, Partial Dependence, and Calibration curves.",
    highlight: "DTI and credit score proven as dominant risk drivers."
  },
  {
    title: "5. AI Prescriptive Recommendations",
    route: "/prediction",
    badge: "Decision Intelligence",
    description: "Transform raw risk scores into actionable loan mitigations: principal reduction, co-signer mandate, and capital buffer.",
    highlight: "Action: Restructure loan by 20% to prevent default write-off."
  },
  {
    title: "6. Interactive Monte Carlo Simulation",
    route: "/simulation",
    badge: "What-If Shocks",
    description: "Subject loan portfolio to macroeconomic crisis stress tests (income -30%, credit -80pts) with live VaR-95 shifts.",
    highlight: "Simulated default rate jumps to 34.6% under stress."
  },
  {
    title: "7. Population Stability & Drift Detection",
    route: "/drift",
    badge: "Drift Guard",
    description: "Continuously compute Kolmogorov-Smirnov test and PSI on real-time stream; alert when retraining is mandatory.",
    highlight: "Critical alert on DTI drift (PSI: 0.284 > 0.25 threshold)."
  },
  {
    title: "8. Fairness, Bias & Regulatory Audit",
    route: "/fairness",
    badge: "Responsible AI",
    description: "Verify demographic parity and disparate impact ratio across protected classes to satisfy EEOC & ECOA guidelines.",
    highlight: "Disparate Impact ratio 0.88 exceeds 80% legal threshold."
  },
  {
    title: "9. Executive Business Impact & ROI",
    route: "/impact",
    badge: "P&L Value",
    description: "Quantify balance sheet outcomes: $4.28M capital protected, +10.4% higher approval rate, and 318% risk-adjusted ROI.",
    highlight: "Translates ML precision directly into enterprise EBITDA."
  },
  {
    title: "10. Automated Board Audit & Dossier Export",
    route: "/reports",
    badge: "Executive Reporting",
    description: "Export complete compliance dossier and audit trails for regulatory risk committees.",
    highlight: "Full end-to-end AI Decision Support story complete!"
  }
];

export function JudgeDemoModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [currentStepIdx, setCurrentStepIdx] = React.useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = React.useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const currentStep = TOUR_STEPS[currentStepIdx];

  // Navigate when step changes
  React.useEffect(() => {
    if (isOpen && currentStep) {
      if (location.pathname !== currentStep.route) {
        navigate(currentStep.route);
      }
    }
  }, [currentStepIdx, isOpen]);

  // Auto-play timer
  React.useEffect(() => {
    let timer: any;
    if (isOpen && isAutoPlaying) {
      timer = setInterval(() => {
        setCurrentStepIdx((prev) => {
          if (prev < TOUR_STEPS.length - 1) {
            return prev + 1;
          } else {
            setIsAutoPlaying(false);
            return prev;
          }
        });
      }, 7000);
    }
    return () => clearInterval(timer);
  }, [isOpen, isAutoPlaying]);

  if (!isOpen) return null;

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-3xl px-4 animate-in">
      <div className="rounded-2xl border border-primary/40 bg-slate-900/95 backdrop-blur-md shadow-2xl p-5 text-white">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-ping" />
            <span className="font-bold text-sm tracking-wide text-primary-foreground flex items-center gap-1.5">
              <Sparkles className="h-4 w-4 text-primary" />
              Grand Champion Story Mode
            </span>
            <Badge variant="outline" className="text-[10px] border-primary/40 text-primary bg-primary/10">
              Step {currentStepIdx + 1} of {TOUR_STEPS.length}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setIsAutoPlaying(!isAutoPlaying)}
              className="h-7 text-xs gap-1 border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700"
            >
              {isAutoPlaying ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
              {isAutoPlaying ? 'Pause Tour' : 'Auto Play'}
            </Button>
            <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Step Content */}
        <div className="py-3 space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white">{currentStep.title}</h3>
            <Badge className="bg-primary/20 text-primary border border-primary/30 text-xs">
              {currentStep.badge}
            </Badge>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {currentStep.description}
          </p>
          <div className="rounded-lg bg-primary/10 border border-primary/20 p-2.5 text-xs text-primary flex items-center gap-2 font-medium">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>Judge Takeaway: {currentStep.highlight}</span>
          </div>
        </div>

        {/* Navigation Controls */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
          <Button
            size="sm"
            variant="ghost"
            disabled={currentStepIdx === 0}
            onClick={() => setCurrentStepIdx((p) => Math.max(0, p - 1))}
            className="h-8 gap-1 text-slate-400 hover:text-white"
          >
            <ChevronLeft className="h-3.5 w-3.5" /> Previous
          </Button>

          {/* Dots Indicator */}
          <div className="flex gap-1.5">
            {TOUR_STEPS.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentStepIdx(i)}
                className={`h-2 rounded-full transition-all ${
                  i === currentStepIdx ? 'w-6 bg-primary' : 'w-2 bg-slate-700 hover:bg-slate-500'
                }`}
              />
            ))}
          </div>

          <Button
            size="sm"
            variant="default"
            onClick={() => {
              if (currentStepIdx < TOUR_STEPS.length - 1) {
                setCurrentStepIdx((p) => p + 1);
              } else {
                onClose();
              }
            }}
            className="h-8 gap-1 bg-primary hover:bg-primary/90 text-white font-semibold shadow-md"
          >
            {currentStepIdx === TOUR_STEPS.length - 1 ? 'Finish Demo' : 'Next Stage'}
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
