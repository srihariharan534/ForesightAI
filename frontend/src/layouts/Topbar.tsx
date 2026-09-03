
import { Bell, Search, Sun, Moon, Laptop, User, Sparkles } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';

export function Topbar({ onOpenCopilot }: { onOpenCopilot?: () => void }) {
  const { theme, setTheme } = useAppStore();

  const toggleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  const getThemeIcon = () => {
    if (theme === 'light') return <Sun className="h-5 w-5" />;
    if (theme === 'dark') return <Moon className="h-5 w-5" />;
    return <Laptop className="h-5 w-5" />;
  };

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-slate-200 dark:border-slate-800 bg-card dark:bg-card-dark px-6 shadow-sm z-10">
      <div className="flex flex-1 items-center gap-4 md:w-2/3 lg:w-1/3">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
          <Input
            type="search"
            placeholder="Search resources, models, reports... (Ctrl+K)"
            className="w-full bg-background dark:bg-slate-900 pl-9 border-slate-200 dark:border-slate-700 h-9 focus-visible:ring-1 focus-visible:ring-primary shadow-inner"
          />
        </div>
      </div>
      <div className="flex items-center gap-3">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onOpenCopilot} 
          className="gap-1.5 text-xs border-primary/40 text-primary hover:bg-primary/10 h-8"
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">AI Copilot</span>
        </Button>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-danger ring-2 ring-card dark:ring-card-dark" />
        </Button>
        <Button variant="ghost" size="icon" onClick={toggleTheme} title={`Theme: ${theme}`}>
          {getThemeIcon()}
        </Button>
        <div className="h-8 w-px bg-slate-200 dark:bg-slate-800 mx-1" />
        <Button variant="ghost" className="gap-2 pl-2 border border-transparent hover:border-slate-200 dark:hover:border-slate-700">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-primary">
            <User className="h-4 w-4" />
          </div>
          <div className="flex flex-col items-start text-left">
            <span className="text-xs font-semibold leading-none">Admin User</span>
            <span className="text-[10px] text-slate-500 mt-1">Enterprise Plan</span>
          </div>
        </Button>
      </div>
    </header>
  );
}
