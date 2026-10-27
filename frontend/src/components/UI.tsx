import type { ReactNode } from 'react';
import { AlertCircle, ArrowRight, Inbox, LoaderCircle, X } from 'lucide-react';

export function PageHeading({ eyebrow, title, subtitle, action }: { eyebrow: string; title: string; subtitle: string; action?: ReactNode }) {
  return <div className="page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{subtitle}</p></div>{action && <div className="heading-action">{action}</div>}</div>;
}

export function Button({ children, variant = 'primary', ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'ghost' | 'danger' }) {
  return <button className={`btn btn-${variant}`} {...props}>{children}</button>;
}

export function EmptyState({ title, text, action }: { title: string; text: string; action?: ReactNode }) {
  return <div className="empty-state"><div className="empty-icon"><Inbox size={26}/></div><h3>{title}</h3><p>{text}</p>{action}</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="error-state" role="alert"><AlertCircle size={20}/><span>{message}</span></div>;
}

export function LoadingState() {
  return <div className="loading-state" role="status"><LoaderCircle className="spin" size={22}/> Carregando informações...</div>;
}

export function Dialog({ title, description, children, onClose }: { title: string; description?: string; children: ReactNode; onClose: () => void }) {
  return <div className="dialog-overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="dialog" role="dialog" aria-modal="true" aria-label={title}>
      <div className="dialog-header"><div><h2>{title}</h2>{description && <p>{description}</p>}</div><button className="icon-button" aria-label="Fechar janela" onClick={onClose}><X size={19}/></button></div>
      {children}
    </section>
  </div>;
}

export function ConfirmDialog({ title, message, busy, onCancel, onConfirm }: { title: string; message: string; busy: boolean; onCancel: () => void; onConfirm: () => void }) {
  return <Dialog title={title} description={message} onClose={onCancel}><div className="dialog-actions"><Button variant="secondary" onClick={onCancel} disabled={busy}>Cancelar</Button><Button variant="danger" disabled={busy} onClick={onConfirm}>{busy ? 'Excluindo...' : 'Sim, excluir'}</Button></div></Dialog>;
}

export function Notice({ text, onClose }: { text: string; onClose: () => void }) {
  return <div className="notice" role="status"><span>{text}</span><button aria-label="Fechar aviso" onClick={onClose}><X size={16}/></button></div>;
}

export function TextLink({ children }: { children: ReactNode }) {
  return <span className="text-link">{children}<ArrowRight size={16}/></span>;
}
