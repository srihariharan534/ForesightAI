import * as React from 'react';
import { 
  Sparkles, 
  X, 
  Send, 
  Bot, 
  User 
} from 'lucide-react';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Badge } from './ui/Badge';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  timestamp: string;
  meta?: {
    type: 'metric' | 'action';
    data: string;
  };
}

const KNOWLEDGE_RESPONSES: Record<string, string> = {
  "default": "ForesightAI's champion model is XGBoost v1.0.0 (run_0cabd18f), yielding 96.0% accuracy and 0.8694 ROC-AUC. Would you like me to explain loan approval drivers, run a stress-test scenario, or inspect regional risk?",
  "loan": "Our underwriting pipeline assesses 10 core features: Debt-to-Income (DTI), credit score, employment tenure, and prior defaults. SHAP attributions show DTI > 40% combined with a credit score under 600 is the primary driver for default classification.",
  "risk": "Monte Carlo simulations across 1,000 draws indicate a baseline portfolio default rate of 5.2%. Under the Financial Crisis macro shock (income -30%, credit -80), the simulated default rate jumps to 34.6% with a VaR-95 of 22.4%.",
  "decision": "The Decision Center recommends lowering the maximum DTI threshold from 45% to 38% for tier-2 applicants. This prescriptive action is projected to save $3.04M in capital across the next 2 fiscal quarters.",
  "model": "Models in registry: 1) XGBoost Default Classifier (Production, 96% Acc), 2) LightGBM Risk Frontier (Staging, 94.8% Acc), 3) Vectorized Monte Carlo Copula (Active Live Engine).",
  "why": "Explainable AI (SHAP) analyzes marginal contribution per borrower. For instance, high income (>$60,000) exerts a -0.12 protective effect, while any prior default adds a +0.35 risk spike to the log-odds equation."
};

export function AICopilotModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: 'msg-1',
      sender: 'ai',
      text: "Hello! I am ForesightAI Copilot. Ask me about model predictions, explainable AI (SHAP) insights, Monte Carlo simulations, or Decision Center recommendations.",
      timestamp: 'Just now'
    }
  ]);
  const [input, setInput] = React.useState('');
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userText = input.trim();
    const newMsg: Message = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: 'Just now'
    };

    setMessages((prev) => [...prev, newMsg]);
    setInput('');

    setTimeout(() => {
      const lower = userText.toLowerCase();
      let reply = KNOWLEDGE_RESPONSES["default"];
      if (lower.includes("loan") || lower.includes("credit") || lower.includes("predict")) {
        reply = KNOWLEDGE_RESPONSES["loan"];
      } else if (lower.includes("risk") || lower.includes("simulation") || lower.includes("crisis")) {
        reply = KNOWLEDGE_RESPONSES["risk"];
      } else if (lower.includes("decision") || lower.includes("policy") || lower.includes("recommend")) {
        reply = KNOWLEDGE_RESPONSES["decision"];
      } else if (lower.includes("model") || lower.includes("accuracy") || lower.includes("xgboost")) {
        reply = KNOWLEDGE_RESPONSES["model"];
      } else if (lower.includes("why") || lower.includes("shap") || lower.includes("explain")) {
        reply = KNOWLEDGE_RESPONSES["why"];
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          sender: 'ai',
          text: reply,
          timestamp: 'Just now'
        }
      ]);
    }, 600);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end p-4 bg-slate-950/40 backdrop-blur-sm animate-in">
      <div className="w-full max-w-md h-[580px] flex flex-col rounded-2xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white shadow-sm">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100">Foresight Copilot</h3>
                <Badge variant="outline" className="text-[10px] font-mono px-1.5 py-0 border-emerald-500/40 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40">
                  Online
                </Badge>
              </div>
              <p className="text-[11px] text-slate-400">Natural language analytical assistant</p>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-md"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Quick Suggestion Chips */}
        <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/30 dark:bg-slate-900/30 flex gap-1.5 overflow-x-auto text-[11px] scrollbar-none">
          {["Why loan approval?", "Explain macro risk", "What are active policies?", "Model metrics"].map((chip) => (
            <button
              key={chip}
              onClick={() => { setInput(chip); }}
              className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 shrink-0 transition-colors"
            >
              {chip}
            </button>
          ))}
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3.5 text-xs">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'ai' && (
                <div className="h-7 w-7 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="h-4 w-4" />
                </div>
              )}
              <div
                className={`max-w-[82%] rounded-xl px-3.5 py-2.5 leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-primary text-white font-medium rounded-br-none shadow-sm'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none border border-slate-200/50 dark:border-slate-700/50'
                }`}
              >
                {m.text}
              </div>
              {m.sender === 'user' && (
                <div className="h-7 w-7 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="h-3.5 w-3.5" />
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Footer */}
        <div className="p-3 border-t border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about models, loans, or scenarios..."
              className="text-xs h-9 bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800"
            />
            <Button size="sm" type="submit" className="h-9 px-3 gap-1 shrink-0">
              <Send className="h-3.5 w-3.5" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
