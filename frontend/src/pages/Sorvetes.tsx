import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { IceCreamCone, Pencil, Plus, Search, Trash2 } from 'lucide-react';
import { api, formatPrice, type Fabricante, type Sorvete } from '../lib/api';
import { Button, ConfirmDialog, Dialog, EmptyState, ErrorState, LoadingState, Notice, PageHeading } from '../components/UI';

const schema = z.object({
  nome: z.string().trim().min(1, 'Informe o nome do sorvete.').max(100),
  sabor: z.string().trim().min(1, 'Informe o sabor.').max(100),
  preco: z.number().int('Use valores inteiros.').min(0, 'O preço não pode ser negativo.'),
  fabricante_id: z.string().uuid('Selecione um fabricante válido.'),
});
type Form = z.infer<typeof schema>;

function SorveteForm({ item, fabricantes, onClose, onDone }: { item: Sorvete | null; fabricantes: Fabricante[]; onClose: () => void; onDone: (text: string) => void }) {
  const qc = useQueryClient();
  const { register, handleSubmit, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { nome: item?.nome ?? '', sabor: item?.sabor ?? '', preco: item?.preco ?? 0, fabricante_id: item?.fabricante_id ?? fabricantes[0]?.id ?? '' },
  });
  const mutation = useMutation({
    mutationFn: (values: Form) => item ? api.sorvetes.update(item.id, values) : api.sorvetes.create(values),
    onSuccess: async () => { await qc.invalidateQueries({ queryKey: ['sorvetes'] }); onDone(item ? 'Sorvete atualizado com sucesso.' : 'Sorvete cadastrado com sucesso.'); },
  });
  return <Dialog title={item ? 'Editar sorvete' : 'Novo sorvete'} description="Preencha os campos para atualizar seu catálogo." onClose={onClose}>
    <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="dialog-form">
      <div className="form-grid"><div className="field"><label htmlFor="nome-sorvete">Nome do produto</label><input id="nome-sorvete" autoFocus placeholder="Ex.: Picolé" {...register('nome')} aria-invalid={!!errors.nome}/>{errors.nome && <span className="field-error">{errors.nome.message}</span>}</div>
      <div className="field"><label htmlFor="sabor-sorvete">Sabor</label><input id="sabor-sorvete" placeholder="Ex.: Morango" {...register('sabor')} aria-invalid={!!errors.sabor}/>{errors.sabor && <span className="field-error">{errors.sabor.message}</span>}</div>
      <div className="field"><label htmlFor="preco-sorvete">Preço (R$ inteiros)</label><input id="preco-sorvete" type="number" min="0" step="1" {...register('preco', { valueAsNumber: true })} aria-invalid={!!errors.preco}/>{errors.preco && <span className="field-error">{errors.preco.message}</span>}</div>
      <div className="field"><label htmlFor="fabricante-sorvete">Fabricante</label><select id="fabricante-sorvete" {...register('fabricante_id')} aria-invalid={!!errors.fabricante_id}>{fabricantes.map((fabricante) => <option key={fabricante.id} value={fabricante.id}>{fabricante.nome}</option>)}</select>{errors.fabricante_id && <span className="field-error">{errors.fabricante_id.message}</span>}</div></div>
      <p className="field-hint">Os preços são armazenados como valores inteiros em reais nesta versão. Não há centavos no modelo atual.</p>
      {mutation.error && <ErrorState message={mutation.error.message}/>}
      <div className="dialog-actions"><Button type="button" variant="secondary" onClick={onClose}>Cancelar</Button><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? 'Salvando...' : item ? 'Salvar alterações' : 'Cadastrar sorvete'}</Button></div>
    </form>
  </Dialog>;
}

export default function Sorvetes() {
  const qc = useQueryClient();
  const fabricantes = useQuery({ queryKey: ['fabricantes'], queryFn: api.fabricantes.list });
  const [term, setTerm] = useState('');
  const [manufacturer, setManufacturer] = useState('');
  const [formOpen, setFormOpen] = useState(false);
  const [selected, setSelected] = useState<Sorvete | null>(null);
  const [target, setTarget] = useState<Sorvete | null>(null);
  const [notice, setNotice] = useState('');
  const query = useQuery({ queryKey: ['sorvetes', term, manufacturer], queryFn: () => api.sorvetes.list({ q: term, fabricante_id: manufacturer }) });
  const remove = useMutation({ mutationFn: (id: string) => api.sorvetes.remove(id), onSuccess: async () => { await qc.invalidateQueries({ queryKey: ['sorvetes'] }); setTarget(null); setNotice('Sorvete excluído com sucesso.'); } });
  const openForm = (item: Sorvete | null) => { setSelected(item); setFormOpen(true); };
  const hasManufacturers = (fabricantes.data?.length ?? 0) > 0;
  return <div className="page-inner">
    <PageHeading eyebrow="GESTÃO DE PRODUTOS" title="Sorvetes" subtitle="Explore, cadastre e gerencie os sabores do seu catálogo." action={<Button disabled={!hasManufacturers} title={!hasManufacturers ? 'Cadastre um fabricante primeiro' : ''} onClick={() => openForm(null)}><Plus size={18}/> Novo sorvete</Button>}/>
    <div className="table-card"><div className="table-top"><div><h2>Catálogo de sorvetes</h2><p>Produtos cadastrados na plataforma</p></div><div className="filters"><label className="search-field"><Search size={18}/><input aria-label="Buscar sorvete" placeholder="Buscar por nome..." value={term} onChange={(event) => setTerm(event.target.value)}/></label><select aria-label="Filtrar fabricante" value={manufacturer} onChange={(event) => setManufacturer(event.target.value)}><option value="">Todos os fabricantes</option>{(fabricantes.data ?? []).map((f) => <option key={f.id} value={f.id}>{f.nome}</option>)}</select></div></div>
      {query.isLoading || fabricantes.isLoading ? <LoadingState/> : query.error ? <ErrorState message={query.error.message}/> : fabricantes.error ? <ErrorState message={fabricantes.error.message}/> : query.data?.length === 0 ? <EmptyState title={term || manufacturer ? 'Nenhum resultado encontrado' : 'O catálogo está vazio'} text={term || manufacturer ? 'Altere os filtros para encontrar outros produtos.' : hasManufacturers ? 'Cadastre seu primeiro sorvete para começar.' : 'Cadastre um fabricante antes de criar um sorvete.'} action={!term && !manufacturer && hasManufacturers && <Button onClick={() => openForm(null)}><Plus size={17}/> Novo sorvete</Button>}/> :
        <div className="table-scroll"><table><thead><tr><th>PRODUTO</th><th>SABOR</th><th>FABRICANTE</th><th>PREÇO</th><th className="col-actions">AÇÕES</th></tr></thead><tbody>{(query.data ?? []).map((item, index) => <tr key={item.id}><td><div className="table-name"><span className={`letter-avatar tone-${index % 3}`}><IceCreamCone size={18}/></span><strong>{item.nome}</strong></div></td><td><span className="flavor-pill">{item.sabor}</span></td><td>{item.fabricante}</td><td><strong>{formatPrice(item.preco)}</strong></td><td><div className="action-group"><button title="Editar sorvete" aria-label={`Editar ${item.nome}`} onClick={() => openForm(item)}><Pencil size={17}/></button><button title="Excluir sorvete" aria-label={`Excluir ${item.nome}`} onClick={() => setTarget(item)}><Trash2 size={17}/></button></div></td></tr>)}</tbody></table></div>}
      <div className="table-bottom"><span>{query.data?.length ?? 0} produtos encontrados</span><span>Catálogo em tempo real</span></div>
    </div>
    {formOpen && <SorveteForm key={selected?.id ?? 'new'} item={selected} fabricantes={fabricantes.data ?? []} onClose={() => setFormOpen(false)} onDone={(message) => { setFormOpen(false); setNotice(message); }}/>}
    {target && <ConfirmDialog title="Excluir sorvete?" message={`Você tem certeza de que deseja excluir “${target.nome}”? Esta ação não pode ser desfeita.`} busy={remove.isPending} onCancel={() => { setTarget(null); remove.reset(); }} onConfirm={() => remove.mutate(target.id)}/>}
    {remove.error && <ErrorState message={remove.error.message}/>}
    {notice && <Notice text={notice} onClose={() => setNotice('')}/>}
  </div>;
}
