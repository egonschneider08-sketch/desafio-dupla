import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, IceCreamCone, Layers3, PlusCircle, Sparkles, TrendingUp } from 'lucide-react';
import { api, formatPrice } from '../lib/api';
import { EmptyState, ErrorState, LoadingState, PageHeading, TextLink } from '../components/UI';

export default function Dashboard() {
  const fabricants = useQuery({ queryKey: ['fabricantes'], queryFn: api.fabricantes.list });
  const products = useQuery({ queryKey: ['sorvetes'], queryFn: () => api.sorvetes.list() });
  const busy = fabricants.isLoading || products.isLoading;
  const error = fabricants.error || products.error;
  const fabricantes = fabricants.data ?? [];
  const sorvetes = products.data ?? [];
  const sabores = new Set(sorvetes.map((item) => item.sabor.toLowerCase())).size;

  return <div className="page-inner">
    <PageHeading eyebrow="PAINEL DE CONTROLE" title="Visão geral" subtitle="Tudo o que você precisa saber sobre o seu catálogo, em um só lugar."/>
    <section className="hero-banner"><div className="hero-copy"><span className="hero-kicker"><Sparkles size={15}/> SEU ESPAÇO DE GESTÃO</span><h2>Um catálogo organizado.<br/><em>Infinitas possibilidades.</em></h2><p>Gerencie fabricantes, sabores e produtos com facilidade.</p><Link className="hero-link" to="/sorvetes">Explorar catálogo <ArrowRight size={17}/></Link></div><div className="hero-graphic" aria-hidden="true"><div className="scoop scoop-one"/><div className="scoop scoop-two"/><div className="scoop scoop-three"/><div className="ice-cone"/></div></section>
    {error && <ErrorState message={error instanceof Error ? error.message : 'Erro ao carregar catálogo'}/>}
    {busy ? <LoadingState/> : <>
      <div className="stat-grid"><div className="stat-card"><div className="stat-icon lavender"><Layers3 size={23}/></div><span>Fabricantes cadastrados</span><strong>{fabricantes.length}</strong><small>Parceiros no catálogo</small></div>
      <div className="stat-card"><div className="stat-icon peach"><IceCreamCone size={23}/></div><span>Sorvetes cadastrados</span><strong>{sorvetes.length}</strong><small>Produtos disponíveis</small></div>
      <div className="stat-card"><div className="stat-icon mint"><TrendingUp size={23}/></div><span>Sabores diferentes</span><strong>{sabores}</strong><small>Variedade no catálogo</small></div></div>
      <div className="dashboard-grid"><section className="surface-card recent-card"><div className="card-head"><div><h3>Produtos recentes</h3><p>Uma visão rápida do seu catálogo</p></div><Link to="/sorvetes"><TextLink>Ver todos</TextLink></Link></div>
        {sorvetes.length === 0 ? <EmptyState title="Seu catálogo começa aqui" text="Cadastre seu primeiro sorvete para começar a organizar seus produtos." action={<Link className="btn btn-primary" to="/sorvetes"><PlusCircle size={17}/> Cadastrar sorvete</Link>}/> :
          <div className="recent-list">{sorvetes.slice(-5).reverse().map((item, index) => <div className="recent-item" key={item.id}><div className={`product-avatar flavor-${index % 3}`}><IceCreamCone size={20}/></div><div><strong>{item.nome}</strong><small>{item.sabor} · {item.fabricante}</small></div><span>{formatPrice(item.preco)}</span></div>)}</div>}
      </section>
      <section className="surface-card quick-actions"><div className="card-head"><div><h3>Acesso rápido</h3><p>O que você deseja fazer?</p></div></div>
        <Link to="/fabricantes" className="quick-link"><div className="quick-icon purple"><Layers3 size={21}/></div><div><strong>Gerenciar fabricantes</strong><small>Cadastre e edite seus parceiros</small></div><ArrowRight size={18}/></Link>
        <Link to="/sorvetes" className="quick-link"><div className="quick-icon green"><IceCreamCone size={21}/></div><div><strong>Gerenciar sorvetes</strong><small>Organize produtos e sabores</small></div><ArrowRight size={18}/></Link>
      </section></div>
    </>}
  </div>;
}
