import * as React from 'react';
import { 
  HelpCircle, 
  BookOpen, 
  MessageSquare, 
  ExternalLink, 
  Search, 
  Terminal, 
  ChevronDown, 
  ChevronUp, 
  Send 
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { useToast } from '../components/ui/Toast';

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

const FAQS: FAQItem[] = [
  {
    question: "How does ForesightAI compute Probability of Default (PD)?",
    answer: "ForesightAI runs an ensemble pipeline powered by a tuned XGBoost gradient boosting classifier with StandardScaler and median imputation. Output log-odds are calibrated into probabilities and enriched with local SHAP values for explainability.",
    category: "ML Engine"
  },
  {
    question: "What mathematical methodology backs the Monte Carlo simulations?",
    answer: "We employ a vectorized NumPy Gaussian Copula with antithetic variate variance reduction across 1,000 to 10,000 stochastic paths to compute 95% Value-at-Risk (VaR) and Conditional VaR (CVaR).",
    category: "Simulation"
  },
  {
    question: "How are prescriptive policies formed in the Decision Center?",
    answer: "The Decision Center correlates model-predicted default likelihoods against historical recovery loss distributions to prescribe automated actions (e.g., dynamic DTI threshold caps or reserve capital reallocations).",
    category: "Governance"
  },
  {
    question: "Can I ingest custom CSV or JSON datasets?",
    answer: "Yes! Navigate to the Datasets tab where you can drag-and-drop custom datasets. The feature store validates columns, computes quality health percentages, and previews top records.",
    category: "Datasets"
  }
];

export function HelpCenter() {
  const [search, setSearch] = React.useState('');
  const [expandedIndex, setExpandedIndex] = React.useState<number | null>(0);
  const [contactMessage, setContactMessage] = React.useState('');
  const { toast } = useToast();

  const filteredFaqs = FAQS.filter(
    f => f.question.toLowerCase().includes(search.toLowerCase()) || 
         f.answer.toLowerCase().includes(search.toLowerCase()) ||
         f.category.toLowerCase().includes(search.toLowerCase())
  );

  const handleSendSupport = (e: React.FormEvent) => {
    e.preventDefault();
    if (!contactMessage.trim()) return;
    setContactMessage('');
    toast({
      title: 'Ticket Submitted',
      description: 'Support inquiry dispatched to ForesightAI Quantitative Engineering.',
      type: 'success',
    });
  };

  return (
    <div className="space-y-6 animate-in max-w-5xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Help & Knowledge Center</h1>
            <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
              Docs & Support
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            System documentation, API references, mathematical specifications, and technical support.
          </p>
        </div>
      </div>

      {/* Quick Links Grid */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => window.open('http://127.0.0.1:8000/docs', '_blank')}>
          <CardContent className="p-4 flex items-start gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary shrink-0">
              <Terminal className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold flex items-center gap-1 text-slate-900 dark:text-slate-100">
                Interactive API Docs <ExternalLink className="h-3 w-3" />
              </h4>
              <p className="text-xs text-slate-500 mt-1">FastAPI OpenAPI Swagger UI specification on port 8000</p>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors">
          <CardContent className="p-4 flex items-start gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-600 shrink-0">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Architecture Dossier</h4>
              <p className="text-xs text-slate-500 mt-1">System design diagrams & ML pipeline sequence specs</p>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors">
          <CardContent className="p-4 flex items-start gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-600 shrink-0">
              <HelpCircle className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Model Whitepaper</h4>
              <p className="text-xs text-slate-500 mt-1">XGBoost calibration and Monte Carlo Copula formulation</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search & FAQs */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <CardTitle className="text-base">Frequently Asked Questions</CardTitle>
              <CardDescription className="text-xs">Mathematical, algorithmic, and operational questions answered</CardDescription>
            </div>
            <div className="relative sm:w-72">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search topics..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="text-xs pl-9"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {filteredFaqs.map((faq, idx) => (
            <div 
              key={idx} 
              className="border border-slate-200 dark:border-slate-800 rounded-lg p-3.5 transition-colors"
            >
              <button
                onClick={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                className="w-full flex items-center justify-between text-left text-xs font-semibold text-slate-900 dark:text-slate-100"
              >
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px] font-mono font-normal">
                    {faq.category}
                  </Badge>
                  <span>{faq.question}</span>
                </div>
                {expandedIndex === idx ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
              </button>
              {expandedIndex === idx && (
                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 pt-2 border-t border-slate-100 dark:border-slate-800 leading-relaxed">
                  {faq.answer}
                </p>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Contact Support */}
      <Card>
        <form onSubmit={handleSendSupport}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <MessageSquare className="h-4 w-4 text-primary" /> Contact Quantitative Support
            </CardTitle>
            <CardDescription className="text-xs">
              Direct line to ML platform engineers for audit review or customized stress scenario builds
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Input 
              value={contactMessage}
              onChange={(e) => setContactMessage(e.target.value)}
              placeholder="Describe your technical inquiry, model anomaly, or scenario parameter request..."
              className="text-xs"
            />
          </CardContent>
          <CardFooter className="flex justify-end pt-2">
            <Button type="submit" size="sm" className="gap-1.5 text-xs">
              <Send className="h-3.5 w-3.5" /> Dispatch Inquiry
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
