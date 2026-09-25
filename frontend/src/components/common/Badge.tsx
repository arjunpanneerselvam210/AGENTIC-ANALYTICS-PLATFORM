import React from 'react';

export type BadgeVariant =
  | 'emerald'
  | 'blue'
  | 'purple'
  | 'amber'
  | 'rose'
  | 'slate'
  | 'indigo'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'emerald',
  size = 'md',
  className = '',
}) => {
  // Normalize semantic variants to color styles
  const resolvedVariant = (() => {
    switch (variant) {
      case 'success': return 'emerald';
      case 'warning': return 'amber';
      case 'danger': return 'rose';
      case 'info': return 'blue';
      default: return variant;
    }
  })();

  const variantStyles: Record<string, string> = {
    emerald: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    blue: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    purple: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
    amber: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    rose: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    slate: 'bg-slate-800 text-slate-300 border-slate-700',
    indigo: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
  };

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${variantStyles[resolvedVariant] || variantStyles.slate} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
};
