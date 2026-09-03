import * as React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { cn } from '../../utils/cn';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  position?: 'left' | 'right';
}

export function Drawer({
  isOpen,
  onClose,
  title,
  description,
  children,
  className,
  position = 'right',
}: DrawerProps) {
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const slideVariants = {
    left: { initial: { x: '-100%' }, animate: { x: 0 }, exit: { x: '-100%' } },
    right: { initial: { x: '100%' }, animate: { x: 0 }, exit: { x: '100%' } },
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm"
            onClick={onClose}
          />
          <div
            className={cn(
              'fixed inset-y-0 z-50 flex pointer-events-none w-full max-w-md',
              position === 'left' ? 'left-0' : 'right-0'
            )}
          >
            <motion.div
              initial={slideVariants[position].initial}
              animate={slideVariants[position].animate}
              exit={slideVariants[position].exit}
              transition={{ type: 'spring', bounce: 0, duration: 0.3 }}
              className={cn(
                'pointer-events-auto w-full h-full border-slate-200 dark:border-slate-800 bg-card dark:bg-card-dark shadow-2xl flex flex-col',
                position === 'left' ? 'border-r' : 'border-l',
                className
              )}
            >
              <div className="flex flex-col space-y-1.5 p-6 border-b border-slate-100 dark:border-slate-800 relative">
                {title && <h2 className="text-lg font-semibold leading-none tracking-tight">{title}</h2>}
                {description && <p className="text-sm text-text-muted">{description}</p>}
                <button
                  onClick={onClose}
                  className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:pointer-events-none"
                >
                  <X className="h-4 w-4" />
                  <span className="sr-only">Close</span>
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6">{children}</div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
