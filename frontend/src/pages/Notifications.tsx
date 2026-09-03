import * as React from 'react';
import { 
  CheckCheck, 
  Trash2, 
  AlertTriangle, 
  Info, 
  CheckCircle2, 
  ShieldAlert, 
  Clock 
} from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useToast } from '../components/ui/Toast';

interface NotificationItem {
  id: string;
  title: string;
  description: string;
  type: 'critical' | 'warning' | 'info' | 'success';
  time: string;
  read: boolean;
  source: string;
}

const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: 'notif-1',
    title: 'Macro Stress Limit Exceeded',
    description: 'Portfolio simulated default probability reached 34.6% under Financial Crisis stress testing.',
    type: 'critical',
    time: '12 mins ago',
    read: false,
    source: 'Monte Carlo Engine'
  },
  {
    id: 'notif-2',
    title: 'Model Retraining Checkpoint Ready',
    description: 'XGBoost v1.0.0 finished 100-estimator cross validation with 0.8694 ROC-AUC.',
    type: 'success',
    time: '45 mins ago',
    read: false,
    source: 'ML Engine Pipeline'
  },
  {
    id: 'notif-3',
    title: 'Prescriptive Policy Execution Pending',
    description: 'Decision Center flagged 14 loan applications requiring DTI threshold adjustment review.',
    type: 'warning',
    time: '2 hours ago',
    read: true,
    source: 'Decision Center'
  },
  {
    id: 'notif-4',
    title: 'Daily Data Hygiene Verification',
    description: 'Sample credit dataset passed null-check and schema validation with 98.4% quality score.',
    type: 'info',
    time: '5 hours ago',
    read: true,
    source: 'Dataset Store'
  }
];

export function Notifications() {
  const [notifications, setNotifications] = React.useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);
  const [filter, setFilter] = React.useState<'all' | 'unread'>('all');
  const { toast } = useToast();

  const handleMarkAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
    toast({
      title: 'All Notifications Read',
      description: 'Cleared all unread notification badges.',
      type: 'success'
    });
  };

  const handleDelete = (id: string) => {
    setNotifications(notifications.filter(n => n.id !== id));
    toast({
      title: 'Notification Dismissed',
      description: 'Removed item from activity feed.',
      type: 'default'
    });
  };

  const handleToggleRead = (id: string) => {
    setNotifications(notifications.map(n => n.id === id ? { ...n, read: !n.read } : n));
  };

  const filtered = filter === 'all' 
    ? notifications 
    : notifications.filter(n => !n.read);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50">Notifications</h1>
            {unreadCount > 0 && (
              <Badge className="bg-primary text-white font-mono text-xs">
                {unreadCount} Unread
              </Badge>
            )}
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time telemetry, model drift alerts, policy execution prompts, and audit events.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="text-xs gap-1.5"
            onClick={handleMarkAllRead}
            disabled={unreadCount === 0}
          >
            <CheckCheck className="h-4 w-4" /> Mark all read
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 dark:border-slate-800 pb-3 text-xs font-medium">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1.5 rounded-md transition-colors ${
            filter === 'all' 
              ? 'bg-primary text-white' 
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
        >
          All Alerts ({notifications.length})
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={`px-3 py-1.5 rounded-md transition-colors ${
            filter === 'unread' 
              ? 'bg-primary text-white' 
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
        >
          Unread ({unreadCount})
        </button>
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center text-slate-500 text-sm">
              No notifications matching your filter.
            </CardContent>
          </Card>
        ) : (
          filtered.map((item) => (
            <Card 
              key={item.id} 
              className={`transition-all hover:border-slate-300 dark:hover:border-slate-700 ${
                !item.read ? 'border-l-4 border-l-primary bg-primary/[0.02]' : 'opacity-85'
              }`}
            >
              <CardContent className="p-4 flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 shrink-0">
                    {item.type === 'critical' && <ShieldAlert className="h-5 w-5 text-rose-600" />}
                    {item.type === 'warning' && <AlertTriangle className="h-5 w-5 text-amber-500" />}
                    {item.type === 'success' && <CheckCircle2 className="h-5 w-5 text-emerald-600" />}
                    {item.type === 'info' && <Info className="h-5 w-5 text-blue-500" />}
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100">{item.title}</h4>
                      <Badge variant="outline" className="text-[10px] font-mono">
                        {item.source}
                      </Badge>
                      {!item.read && (
                        <span className="h-2 w-2 rounded-full bg-primary" />
                      )}
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {item.description}
                    </p>
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-400 pt-1 font-mono">
                      <Clock className="h-3 w-3" />
                      {item.time}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-8 text-xs text-slate-500"
                    onClick={() => handleToggleRead(item.id)}
                  >
                    {item.read ? 'Mark unread' : 'Mark read'}
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-8 w-8 p-0 text-slate-400 hover:text-rose-600"
                    onClick={() => handleDelete(item.id)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
