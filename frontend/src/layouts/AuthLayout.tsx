
import { Outlet } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { motion } from 'framer-motion';

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background dark:bg-background-dark p-4 sm:p-8 relative overflow-hidden">
      
      {/* Decorative background elements for premium feel */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-primary/5 blur-[120px]" />
        <div className="absolute top-[60%] -right-[10%] w-[40%] h-[60%] rounded-full bg-secondary/5 blur-[120px]" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="flex flex-col items-center mb-8"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary shadow-lg mb-4">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">ForesightAI</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 text-center">
            Enterprise prediction and simulation platform
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1, ease: 'easeOut' }}
        >
          <Outlet />
        </motion.div>
        
        <div className="mt-8 text-center text-xs text-slate-500 dark:text-slate-500">
          <p>&copy; {new Date().getFullYear()} ForesightAI Enterprise. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}
