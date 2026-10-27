import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EmptyState, ErrorState } from './UI';

describe('Reusable UI states', () => {
  it('explains an empty catalog without inventing content', () => {
    render(<EmptyState title="Catálogo vazio" text="Cadastre um sorvete." />);
    expect(screen.getByText('Catálogo vazio')).toBeTruthy();
    expect(screen.getByText('Cadastre um sorvete.')).toBeTruthy();
  });
  it('makes server errors available through alert role', () => {
    render(<ErrorState message="Banco indisponível" />);
    expect(screen.getByRole('alert').textContent).toContain('Banco indisponível');
  });
});
