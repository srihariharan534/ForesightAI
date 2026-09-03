import * as React from 'react';
import { 
  Search, 
  Download,
  Eye,
  Clock
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/Table';
import { useToast } from '../components/ui/Toast';

interface AuditHistoryItem {
  id: string;
  type: 'Inference' | 'Simulation' | 'Model Retrain' | 'Policy Trigger';
  target: string;
  prediction: string;
  confidence: number;
  initiatedBy: string;
  timestamp: string;
  status: 'Completed' | 'Alerted';
  details: string;
}

const HISTORY_DATA: AuditHistoryItem[] = [
  {
    id: 'TXN-9021',
    type: 'Inference',
    target: 'Loan Application #48921 (Age 35, Income $65K)',
    prediction: 'Class 0 (Approve)',
    confidence: 96.2,
    initiatedBy: 'Auto-Underwriter API',
    timestamp: '2026-09-03 13:08:44',
    status: 'Completed',
    details: 'Model: xgboost_v1.0.0, Latency: 4.2ms'
  },
  {
    id: 'TXN-9020',
    type: 'Inference',
    target: 'Batch Inference (sample_data.csv - 1000 records)',
    prediction: '987 Approved / 13 High Risk',
    confidence: 95.8,
    initiatedBy: 'CLI (scripts/inference.py)',
    timestamp: '2026-09-03 13:07:30',
    status: 'Completed',
    details: 'Wrote results to predictions.csv'
  },
  {
    id: 'TXN-9019',
    type: 'Simulation',
    target: 'Macro Financial Crisis Stress Test',
    prediction: 'Portfolio Loss: 0.089 → 0.245',
    confidence: 99.0,
    initiatedBy: 'Risk Officer',
    timestamp: '2026-09-03 12:45:10',
    status: 'Alerted',
    details: '10,000 Monte Carlo draws with antithetic variance reduction'
  },
  {
    id: 'TXN-9018',
    type: 'Model Retrain',
    target: 'XGBoost Full Training Pipeline',
    prediction: '96.0% Acc, 0.8694 ROC-AUC',
    confidence: 100.0,
    initiatedBy: 'Automated ML Engine',
    timestamp: '2026-09-03 12:37:24',
    status: 'Completed',
    details: 'Run ID: 0cabd18f7ff74c7783ca5d93925f2754'
  },
  {
    id: 'TXN-9017',
    type: 'Policy Trigger',
    target: 'Decision Center: DTI Cap Restriction',
    prediction: 'Approved Policy Rule',
    confidence: 94.6,
    initiatedBy: 'Credit Committee',
    timestamp: '2026-09-02 17:15:00',
    status: 'Completed',
    details: 'Lowered maximum DTI threshold from 45% to 38%'
  },
  {
    id: 'TXN-9016',
    type: 'Inference',
    target: 'Loan Application #48915 (Age 23, Income $74K)',
    prediction: 'Class 0 (Approve)',
    confidence: 98.4,
    initiatedBy: 'Web Portal',
    timestamp: '2026-09-02 15:20:12',
    status: 'Completed',
    details: 'Low debt-to-income ratio, no prior default'
  }
];

export function History() {
  const [search, setSearch] = React.useState('');
  const [typeFilter, setTypeFilter] = React.useState('All');
  const [historyItems] = React.useState(HISTORY_DATA);
  const { toast } = useToast();

  const filtered = historyItems.filter((item) => {
    const matchesSearch = 
      item.id.toLowerCase().includes(search.toLowerCase()) ||
      item.target.toLowerCase().includes(search.toLowerCase()) ||
      item.initiatedBy.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'All' || item.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const handleInspect = (item: AuditHistoryItem) => {
    toast({
      title: `Audit Record: ${item.id}`,
      description: `${item.target} • ${item.details}`,
      type: 'default',
    });
  };

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Audit & History</h1>
            <Badge variant="outline" className="border-primary/40 text-primary font-mono text-xs">
              Immutable Ledger
            </Badge>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Complete chronological trail of model predictions, simulation shocks, and administrative overrides.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            className="gap-2 text-xs"
            onClick={() => toast({ title: 'Exporting Audit Ledger', description: 'Generated encrypted audit CSV file.', type: 'success' })}
          >
            <Download className="h-3.5 w-3.5" /> Export Audit Log
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search transaction ID, borrower profile, or initiator..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 text-xs"
              />
            </div>
            <div className="flex gap-1.5 flex-wrap">
              {['All', 'Inference', 'Simulation', 'Model Retrain', 'Policy Trigger'].map((type) => (
                <button
                  key={type}
                  onClick={() => setTypeFilter(type)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    typeFilter === type
                      ? 'bg-primary text-white shadow-sm'
                      : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* History Table */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Transaction Log ({filtered.length} entries)</CardTitle>
          <CardDescription className="text-xs">End-to-end model and governance execution timeline</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Event ID & Type</TableHead>
                <TableHead>Target Description</TableHead>
                <TableHead>Outcome / Result</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Initiator</TableHead>
                <TableHead>Timestamp</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((item) => (
                <TableRow key={item.id} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 text-xs">
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-slate-400 shrink-0" />
                      <div>
                        <div className="font-mono text-slate-900 dark:text-slate-100 font-semibold">{item.id}</div>
                        <Badge variant="outline" className="text-[10px] font-mono mt-0.5">
                          {item.type}
                        </Badge>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-slate-700 dark:text-slate-300 max-w-xs font-medium">
                    <div>{item.target}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{item.details}</div>
                  </TableCell>
                  <TableCell className="font-mono font-semibold text-slate-900 dark:text-slate-100">
                    {item.prediction}
                  </TableCell>
                  <TableCell className="font-mono">
                    <Badge variant="default" className="bg-emerald-600/90 text-white font-mono text-[10px]">
                      {item.confidence}%
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-600 dark:text-slate-400">{item.initiatedBy}</TableCell>
                  <TableCell className="text-slate-500 font-mono whitespace-nowrap">{item.timestamp}</TableCell>
                  <TableCell className="text-right">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-8 text-xs gap-1"
                      onClick={() => handleInspect(item)}
                    >
                      <Eye className="h-3.5 w-3.5" /> View
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
