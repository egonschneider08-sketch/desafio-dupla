import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Eye, EyeOff, IceCreamCone, LockKeyhole, ShieldCheck, UserRound } from 'lucide-react';
import { Button, ErrorState, LoadingState } from '../components/UI';
import { useAuth } from '../lib/auth';

const emailRule = z.email('Informe um e-mail válido.');
const passwordRule = z.string().min(12, 'A senha precisa ter pelo menos 12 caracteres.').max(128);
const loginSchema = z.object({ email: emailRule, password: z.string().min(1, 'Informe sua senha.') });
const registrationSchema = z.object({
  name: z.string().trim().min(1, 'Informe seu nome.').max(80),
  email: emailRule,
  password: passwordRule,
  confirmation: z.string().min(1, 'Confirme sua senha.'),
}).refine((data) => data.password === data.confirmation,
  { path: ['confirmation'], message: 'As senhas não coincidem.' });

type LoginData = z.infer<typeof loginSchema>;
type RegisterData = z.infer<typeof registrationSchema>;

function LoginForm({ redirect }: { redirect: () => void }) {
  const { login } = useAuth();
  const [error, setError] = useState('');
  const [show, setShow] = useState(false);
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<LoginData>({ resolver: zodResolver(loginSchema) });
  const submit = handleSubmit(async (values) => {
    setError('');
    try { await login(values); redirect(); }
    catch (err) { setError(err instanceof Error ? err.message : 'Não foi possível entrar.'); }
  });
  return <form className="auth-form" onSubmit={submit}>
    <label htmlFor="auth-email">E-mail</label>
    <input id="auth-email" type="email" autoComplete="email" placeholder="voce@exemplo.com" {...register('email')} aria-invalid={!!errors.email}/>
    {errors.email && <span className="field-error">{errors.email.message}</span>}
    <label htmlFor="auth-password">Senha</label>
    <div className="password-field"><input id="auth-password" autoComplete="current-password" type={show ? 'text' : 'password'} placeholder="Digite sua senha" {...register('password')} aria-invalid={!!errors.password}/><button type="button" onClick={() => setShow(!show)} aria-label={show ? 'Ocultar senha' : 'Mostrar senha'}>{show ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div>
    {errors.password && <span className="field-error">{errors.password.message}</span>}
    {error && <ErrorState message={error}/>}
    <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Entrando...' : 'Entrar no catálogo'}</Button>
  </form>;
}

function RegisterForm({ redirect }: { redirect: () => void }) {
  const { register: createAccount } = useAuth();
  const [error, setError] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<RegisterData>({ resolver: zodResolver(registrationSchema) });
  const submit = handleSubmit(async (values) => {
    setError('');
    try {
      await createAccount({ name: values.name, email: values.email, password: values.password });
      redirect();
    } catch (err) { setError(err instanceof Error ? err.message : 'Não foi possível criar sua conta.'); }
  });
  return <form className="auth-form" onSubmit={submit}>
    <label htmlFor="auth-name">Seu nome</label>
    <input id="auth-name" autoComplete="name" placeholder="Como podemos chamar você?" {...register('name')} aria-invalid={!!errors.name}/>
    {errors.name && <span className="field-error">{errors.name.message}</span>}
    <label htmlFor="auth-email">E-mail</label>
    <input id="auth-email" type="email" autoComplete="email" placeholder="voce@exemplo.com" {...register('email')} aria-invalid={!!errors.email}/>
    {errors.email && <span className="field-error">{errors.email.message}</span>}
    <label htmlFor="auth-password">Crie uma senha</label>
    <input id="auth-password" type="password" autoComplete="new-password" placeholder="Pelo menos 12 caracteres" {...register('password')} aria-invalid={!!errors.password}/>
    {errors.password && <span className="field-error">{errors.password.message}</span>}
    <label htmlFor="auth-confirmation">Confirme a senha</label>
    <input id="auth-confirmation" type="password" autoComplete="new-password" placeholder="Repita a senha" {...register('confirmation')} aria-invalid={!!errors.confirmation}/>
    {errors.confirmation && <span className="field-error">{errors.confirmation.message}</span>}
    {error && <ErrorState message={error}/>}
    <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Criando conta...' : 'Criar minha conta'}</Button>
  </form>;
}

export default function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const { user, loading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const route = (location.state as { from?: string } | null)?.from;
  const redirect = () => navigate(route && route.startsWith('/') && !route.startsWith('//') ? route : '/sorvetes', { replace: true });
  if (loading) return <LoadingState/>;
  if (user) return <Navigate to="/sorvetes" replace/>;
  return <main className="auth-layout">
    <section className="auth-aside"><Link className="auth-brand" to="/entrar"><span><IceCreamCone size={24}/></span>Sorvetes.</Link>
      <div className="auth-aside-copy"><span className="hero-kicker"><ShieldCheck size={16}/> ACESSO AOS NOSSOS SABORES</span><h1>Um universo<br/>de sabores <em>para você.</em></h1><p>Descubra nosso catálogo, conheça os fabricantes e encontre seus sorvetes favoritos.</p><div className="auth-aside-graphic" aria-hidden="true"><IceCreamCone size={120} strokeWidth={1.2}/></div></div>
      <small>© 2026 Sorvetes · Catálogo de produtos</small></section>
    <section className="auth-panel"><div className="auth-card">
      <div className="auth-panel-icon">{mode === 'register' ? <UserRound size={27}/> : <LockKeyhole size={27}/>}</div>
      <span className="eyebrow">ÁREA DO CLIENTE</span>
      <h2>{mode === 'register' ? 'Crie sua conta' : 'Bem-vindo de volta'}</h2>
      <p>{mode === 'register' ? 'Cadastre-se gratuitamente para explorar os produtos.' : 'Entre com seus dados para acessar nosso catálogo.'}</p>
      {error && <ErrorState message={error}/>}
      {mode === 'register' ? <RegisterForm redirect={redirect}/> : <LoginForm redirect={redirect}/>}
      <div className="auth-switch">{mode === 'register' ? 'Já tem uma conta?' : 'Ainda não tem uma conta?'}{' '}
      <Link to={mode === 'register' ? '/entrar' : '/cadastro'}>{mode === 'register' ? 'Entrar' : 'Cadastre-se'}</Link></div>
      <p className="auth-notice"><ShieldCheck size={15}/> A conta de cliente permite consultar produtos. Apenas administradores podem alterá-los.</p>
    </div></section>
  </main>;
}
