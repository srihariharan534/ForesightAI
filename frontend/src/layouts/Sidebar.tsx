
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  Activity, 
  Map, 
  Settings, 
  HelpCircle,
  Database,
  Box,
  History,
  Bell,
  Users,
  Shield,
  FileText,
  ChevronLeft,
  ChevronRight,
  BrainCircuit,
  PieChart,
  Target,
  Sparkles
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { cn } from '../utils/cn';
import { Button } from '../components/ui/Button';

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/' },
  { icon: Sparkles, label: 'Prediction Cards', href: '/prediction-cards' },
  { icon: BrainCircuit, label: 'Prediction Engine', href: '/prediction' },
  { icon: Activity, label: 'Simulation', href: '/simulation' },
  { icon: Target, label: 'Decision Center', href: '/decisions' },
  { icon: Shield, label: 'Fairness & Bias', href: '/fairness' },
  { icon: PieChart, label: 'Business Impact', href: '/impact' },
  { icon: Map, label: 'Risk Maps', href: '/maps' },
  { icon: FileText, label: 'Reports', href: '/reports' },
];

const dataItems = [
  { icon: Box, label: 'AutoML & Models', href: '/models' },
  { icon: Activity, label: 'Drift & MLOps', href: '/drift' },
  { icon: Database, label: 'Datasets', href: '/datasets' },
  { icon: History, label: 'History', href: '/history' },
];

const adminItems = [
  { icon: Bell, label: 'Notifications', href: '/notifications' },
  { icon: Users, label: 'Users & Orgs', href: '/admin' },
  { icon: Settings, label: 'Settings', href: '/settings' },
  { icon: HelpCircle, label: 'Help', href: '/help' },
];

const NavGroup = ({ title, items, sidebarOpen }: { title: string, items: typeof sidebarItems, sidebarOpen: boolean }) => (
  <div className="py-2">
    {sidebarOpen && (
      <h4 className="px-4 text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
        {title}
      </h4>
    )}
    <ul className="space-y-1 px-2">
      {items.map((item) => (
        <li key={item.label}>
          <NavLink
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors relative',
                isActive
                  ? 'bg-primary/10 text-primary dark:text-primary-foreground dark:bg-primary/20'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-50'
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-md bg-primary/10 dark:bg-primary/20"
                    initial={false}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
                <item.icon className="h-5 w-5 shrink-0 relative z-10" />
                {sidebarOpen && <span className="relative z-10">{item.label}</span>}
              </>
            )}
          </NavLink>
        </li>
      ))}
    </ul>
  </div>
);

export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  return (
    <motion.aside
      animate={{ width: sidebarOpen ? 260 : 68 }}
      className="flex h-screen flex-col border-r border-slate-200 dark:border-slate-800 bg-sidebar dark:bg-sidebar-dark shadow-sm text-text dark:text-text-dark"
    >
      <div className="flex h-16 items-center justify-between px-4 border-b border-slate-200 dark:border-slate-800">
        {sidebarOpen && (
          <div className="flex items-center gap-2 font-bold text-lg text-primary tracking-tight">
            <Shield className="h-6 w-6" />
            <span>ForesightAI</span>
          </div>
        )}
        {!sidebarOpen && (
           <Shield className="h-6 w-6 text-primary mx-auto" />
        )}
      </div>

      <div className="flex-1 overflow-y-auto py-4 scrollbar-thin">
        <NavGroup title="Main" items={sidebarItems} sidebarOpen={sidebarOpen} />
        <div className="my-2 border-t border-slate-200 dark:border-slate-800" />
        <NavGroup title="Data & Models" items={dataItems} sidebarOpen={sidebarOpen} />
        <div className="my-2 border-t border-slate-200 dark:border-slate-800" />
        <NavGroup title="Administration" items={adminItems} sidebarOpen={sidebarOpen} />
      </div>

      <div className="border-t border-slate-200 dark:border-slate-800 p-2">
        <Button
          variant="ghost"
          size="sm"
          className="w-full flex justify-center"
          onClick={toggleSidebar}
        >
          {sidebarOpen ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
        </Button>
      </div>
    </motion.aside>
  );
}
