import { NavLink, Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { BarChart3, Box, ChevronRight, CircleHelp, IceCreamCone, Layers3, LayoutDashboard } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Fabricantes from './pages/Fabricantes';
import Sorvetes from './pages/Sorvetes';

const nav = [
  { to: '/', title: 'Visão geral', icon: LayoutDashboard, end: true },
  { to: '/fabricantes', title: 'Fabricantes', icon: Layers3, end: false },
  { to: '/sorvetes', title: 'Sorvetes', icon: IceCreamCone, end: false },
];

function Shell() {
  return <div className="app-layout">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><IceCreamCone size={25} strokeWidth={2.4}/></div><div><strong>Sorvetes<span>.</span></strong><small>CATALOG MANAGER</small></div></div>
      <div className="sidebar-label">WORKSPACE</div>
      <nav className="sidebar-nav" aria-label="Menu principal">{nav.map(({ to, title, icon: Icon, end }) => <NavLink key={to} to={to} end={end} className={({ isActive }) => 'nav-item' + (isActive ? ' active' : '')}><Icon size={19}/><span>{title}</span><ChevronRight className="nav-arrow" size={15}/></NavLink>)}</nav>
      <div className="sidebar-spacer"/>
      <div className="sidebar-help"><CircleHelp size={18}/><div><strong>Documentação</strong><a href="https://app.notion.com/p/406f69f1ed0681e79d21f2ef6f160db5" target="_blank" rel="noreferrer">Abrir no Notion ↗</a></div></div>
      <div className="sidebar-footer"><span className="status-dot"/> Ambiente de desenvolvimento</div>
    </aside>
    <div className="content-area">
      <header className="topbar"><div className="breadcrumbs"><Box size={16}/> Plataforma <ChevronRight size={14}/><strong>Catálogo</strong></div><div className="topbar-right"><span className="live-status"><span/> Sistema de catálogo</span><div className="avatar">S</div></div></header>
      <main className="page-content"><Outlet/></main>
      <footer className="app-footer"><span>© 2026 Sorvetes · Catálogo de produtos</span><span>Feito com Flask + React <BarChart3 size={14}/></span></footer>
    </div>
  </div>;
}
export default function App() {
  return <Routes><Route element={<Shell/>}><Route index element={<Dashboard/>}/><Route path="fabricantes" element={<Fabricantes/>}/><Route path="sorvetes" element={<Sorvetes/>}/></Route><Route path="*" element={<Navigate to="/" replace/>}/></Routes>;
}
