import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GlassCard } from './GlassCard';

describe('GlassCard', () => {
  it('renders children content', () => {
    render(<GlassCard>看板内容</GlassCard>);
    expect(screen.getByText('看板内容')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(<GlassCard className="custom-class">测试</GlassCard>);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('custom-class');
  });

  it('accepts extra props like onClick', () => {
    render(<GlassCard data-testid="card">可点击</GlassCard>);
    expect(screen.getByTestId('card')).toBeInTheDocument();
  });
});
