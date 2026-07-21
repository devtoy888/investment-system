import { cn } from '../lib/api';
import type { HTMLAttributes } from 'react';

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export function GlassCard({ children, className, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        'rounded-xl p-4 backdrop-blur-sm border',
        'bg-brand-card border-white/5',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
