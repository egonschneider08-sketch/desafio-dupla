import { useState } from 'react';
import { NavLink, Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom';
import { BarChart3, Box, ChevronRight, CircleHelp, IceCreamCone, Layers3, LayoutDashboard, LogOut } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Fabricantes from './pages/Fabricantes';
import Sorvetes from './pages/Sorvetes';
import AuthPage from './pages/Auth';
import { LoadingState, ErrorState } from './components/UI';
import { useAuth } from './lib/auth';

const baseNav = [
  { to: '/', title: 'Visão geral', icon: LayoutDashboard, end: true },
  { to: '/sorvetes', title: 'Sorvetes', icon: IceCreamCone, end: false },
];
const adminNav = { to: '/fabricantes', title: 'Fabricantes', icon: Layers3, end: false };

function RequireSession() {
  const { user, loading, error } = useAuth();
  const location = useLocation();
  if (loading) return <LoadingState />;
  if (error) return <main className="auth-loading"><ErrorState message={error}/><button onClick={() => window.location.reload()}>Tentar novamente</button></main>;
  if (!user) return <Navigate to="/entrar" replace state={{ from: location.pathname }} />;
  return <Outlet />;
}

function RequireAdmin() {
  const { user } = useAuth();
  return user?.role === 'admin' ? <Outlet/> : <Navigate to="/sorvetes" replace/>;
}

function Shell() {
  const { user, logout } = useAuth();
  const [error, setError] = useState('');
  const menu = user?.role === 'admin' ? [baseNav[0], adminNav, baseNav[1]] : baseNav;
  return <div className="app-layout">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><IceCreamCone size={25} strokeWidth={2.4}/></div><div><strong>Sorvetes<span>.</span></strong><small>CATÁLOGO ONLINE</small></div></div>
      <div className="sidebar-label">MENU PRINCIPAL</div>
      <nav className="sidebar-nav" aria-label="Menu principal">{menu.map(({ to, title, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => 'nav-item' + (isActive ? ' active' : '')}><Icon size={19}/><span>{title}</span><ChevronRight className="nav-arrow" size={15}/></NavLink>)}</nav>
      <div className="sidebar-spacer"/>
      <div className="sidebar-help"><CircleHelp size={18}/><div><strong>Documentação</strong><a href="https://app.notion.com/p/406f69f1ed0681e79d21f2ef6f160db5" target="_blank" rel="noreferrer">Abrir no Notion ↗</a></div></div>
      <div className="sidebar-footer"><span className="status-dot"/>{user?.role === 'admin' ? 'Administrador' : 'Área do cliente'}</div>
    </aside>
    <div className="content-area">
      <header className="topbar"><div className="breadcrumbs"><Box size={16}/> Plataforma <ChevronRight size={14}/><strong>Catálogo</strong></div>
        <div className="topbar-right"><span className="live-status"><span/> {user?.name}</span><div className="avatar" aria-hidden="true">{user?.name.charAt(0).toUpperCase()}</div>
          <button className="logout-button" onClick={() => logout().catch((err) => setError(err instanceof Error ? err.message : 'Erro ao sair.'))}><LogOut size={17}/> Sair</button>
        </div></header>
      {error && <ErrorState message={error}/>}
      <main className="page-content"><Outlet/></main>
      <footer className="app-footer"><span>© 2026 Sorvetes · Catálogo de produtos</span><span>Feito com Flask + React <BarChart3 size={14}/></span></footer>
    </div>
  </div>;
}

export default function App() {
  return <Routes>
    <Route path="/entrar" element={<AuthPage mode="login"/>}/>
    <Route path="/cadastro" element={<AuthPage mode="register"/>}/>
    <Route element={<RequireSession/>}>
      <Route element={<Shell/>}>
        <Route index element={<Dashboard/>}/>
        <Route path="sorvetes" element={<Sorvetes/>}/>
        <Route element={<RequireAdmin/>}>
          <Route path="fabricantes" element={<Fabricantes/>}/>
        </Route>
      </Route>
    </Route>
    <Route path="*" element={<Navigate to="/" replace/>}/>
  </Routes>;
}
