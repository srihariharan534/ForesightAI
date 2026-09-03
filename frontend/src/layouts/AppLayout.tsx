
import * as React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { CommandPalette } from '../components/ui/CommandPalette';
import { AICopilotModal } from '../components/AICopilotModal';
import { Sparkles } from 'lucide-react';

import { JudgeDemoModal } from '../components/JudgeDemoModal';
import { Play } from 'lucide-react';

export function AppLayout() {
  const [isCopilotOpen, setIsCopilotOpen] = React.useState(false);
  const [isJudgeDemoOpen, setIsJudgeDemoOpen] = React.useState(false);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background dark:bg-background-dark text-text dark:text-text-dark relative">
      <CommandPalette />
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar onOpenCopilot={() => setIsCopilotOpen(true)} />
        <main className="flex-1 overflow-y-auto bg-slate-50/50 dark:bg-slate-900/50 p-6 scrollbar-thin">
          <div className="mx-auto max-w-7xl h-full">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Floating Action Buttons */}
      <div className="fixed bottom-6 right-6 z-40 flex items-center gap-3">
        {/* Judge Demo Trigger */}
        <button
          onClick={() => setIsJudgeDemoOpen(true)}
          className="flex items-center gap-2 rounded-full bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2.5 shadow-xl hover:shadow-2xl transition-all duration-200 text-xs font-bold ring-2 ring-emerald-400/50"
        >
          <Play className="h-4 w-4 fill-white" />
          ▶ Start Judge Demo
        </button>

        {/* Floating Copilot Launcher */}
        <button
          onClick={() => setIsCopilotOpen(true)}
          className="flex items-center gap-2 rounded-full bg-primary hover:bg-primary/90 text-white px-4 py-2.5 shadow-xl hover:shadow-2xl transition-all duration-200 text-xs font-semibold"
        >
          <Sparkles className="h-4 w-4 animate-pulse" />
          Ask Copilot
        </button>
      </div>

      {/* Copilot Drawer */}
      <AICopilotModal isOpen={isCopilotOpen} onClose={() => setIsCopilotOpen(false)} />

      {/* Judge Demo Story Overlay */}
      <JudgeDemoModal isOpen={isJudgeDemoOpen} onClose={() => setIsJudgeDemoOpen(false)} />
    </div>
  );
}
