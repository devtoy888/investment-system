import { cn } from '../lib/api';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
}

export function GlassCard({ children, className }: GlassCardProps) {
  return (
    <div className={cn(
      'rounded-xl p-4 backdrop-blur-sm border',
      'bg-brand-card border-white/5',
      className
    )}>
      {children}
    </div>
  );
}
