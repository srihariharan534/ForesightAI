import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, LayoutDashboard, Brain, Activity, Map, PieChart, Settings, Users } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const pages = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Prediction Engine', path: '/prediction', icon: Brain },
  { name: 'Simulation', path: '/simulation', icon: Activity },
  { name: 'Risk Maps', path: '/maps', icon: Map },
  { name: 'Analytics', path: '/analytics', icon: PieChart },
  { name: 'User Management', path: '/admin', icon: Users },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export function CommandPalette() {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');
  const navigate = useNavigate();

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const filteredPages = pages.filter(page => page.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            className="relative w-full max-w-lg rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-2xl overflow-hidden"
          >
            <div className="flex items-center border-b border-slate-200 dark:border-slate-800 px-4 py-3">
              <Search className="mr-3 h-5 w-5 text-slate-500" />
              <input
                autoFocus
                className="flex-1 bg-transparent outline-none text-slate-900 dark:text-slate-50 placeholder:text-slate-500"
                placeholder="Search commands... (e.g., 'Predict')"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <span className="text-xs text-slate-500 border border-slate-200 dark:border-slate-700 rounded px-1.5 py-0.5">ESC</span>
            </div>
            <div className="max-h-80 overflow-y-auto p-2">
              {filteredPages.length === 0 ? (
                <div className="py-6 text-center text-sm text-slate-500">No results found.</div>
              ) : (
                filteredPages.map((page) => (
                  <button
                    key={page.path}
                    className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 transition-colors"
                    onClick={() => {
                      navigate(page.path);
                      setOpen(false);
                      setSearch('');
                    }}
                  >
                    <page.icon className="h-4 w-4 text-slate-500" />
                    <span>{page.name}</span>
                  </button>
                ))
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
