import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Building2, Pencil, Plus, Search, Trash2 } from 'lucide-react';
import { api, type Fabricante } from '../lib/api';
import { Button, ConfirmDialog, Dialog, EmptyState, ErrorState, LoadingState, Notice, PageHeading } from '../components/UI';

const schema = z.object({ nome: z.string().trim().min(1, 'Informe o nome do fabricante.').max(100, 'Máximo de 100 caracteres.') });
type Form = z.infer<typeof schema>;

function FabricanteForm({ item, onClose, onDone }: { item: Fabricante | null; onClose: () => void; onDone: (text: string) => void }) {
  const qc = useQueryClient();
  const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema), defaultValues: { nome: item?.nome ?? '' } });
  const mutation = useMutation({
    mutationFn: (values: Form) => item ? api.fabricantes.update(item.id, values) : api.fabricantes.create(values),
    onSuccess: async () => { await qc.invalidateQueries({ queryKey: ['fabricantes'] }); onDone(item ? 'Fabricante atualizado com sucesso.' : 'Fabricante cadastrado com sucesso.'); },
  });
  return <Dialog title={item ? 'Editar fabricante' : 'Novo fabricante'} description="Preencha os dados para manter seu catálogo organizado." onClose={onClose}>
    <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="dialog-form">
      <label htmlFor="nome-fabricante">Nome do fabricante</label><input id="nome-fabricante" autoFocus placeholder="Ex.: Gelados da Serra" {...register('nome')} aria-invalid={!!errors.nome}/>
      {errors.nome && <span className="field-error">{errors.nome.message}</span>}
      {mutation.error && <ErrorState message={mutation.error.message}/>}
      <div className="dialog-actions"><Button type="button" variant="secondary" onClick={onClose}>Cancelar</Button><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? 'Salvando...' : item ? 'Salvar alterações' : 'Cadastrar fabricante'}</Button></div>
    </form>
  </Dialog>;
}

export default function Fabricantes() {
  const qc = useQueryClient();
  const query = useQuery({ queryKey: ['fabricantes'], queryFn: api.fabricantes.list });
  const [term, setTerm] = useState('');
  const [formOpen, setFormOpen] = useState(false);
  const [selected, setSelected] = useState<Fabricante | null>(null);
  const [target, setTarget] = useState<Fabricante | null>(null);
  const [notice, setNotice] = useState('');
  const deleteMutation = useMutation({ mutationFn: (id: string) => api.fabricantes.remove(id), onSuccess: async () => { await qc.invalidateQueries({ queryKey: ['fabricantes'] }); setTarget(null); setNotice('Fabricante excluído com sucesso.'); } });
  const visible = (query.data ?? []).filter((item) => item.nome.toLocaleLowerCase('pt-BR').includes(term.toLocaleLowerCase('pt-BR')));
  const openForm = (item: Fabricante | null) => { setSelected(item); setFormOpen(true); };
  return <div className="page-inner">
    <PageHeading eyebrow="GESTÃO DE PARCEIROS" title="Fabricantes" subtitle="Organize os fabricantes que fazem parte do seu catálogo." action={<Button onClick={() => openForm(null)}><Plus size={18}/> Novo fabricante</Button>}/>
    <div className="table-card"><div className="table-top"><div><h2>Todos os fabricantes</h2><p>{query.data?.length ?? 0} fabricante(s) cadastrado(s)</p></div><label className="search-field"><Search size={18}/><input aria-label="Buscar fabricante" placeholder="Buscar fabricante..." value={term} onChange={(event) => setTerm(event.target.value)}/></label></div>
      {query.isLoading ? <LoadingState/> : query.error ? <ErrorState message={query.error.message}/> : visible.length === 0 ? <EmptyState title={term ? 'Nenhum resultado' : 'Nenhum fabricante cadastrado'} text={term ? 'Tente outro termo de busca.' : 'Comece cadastrando o seu primeiro fabricante.'} action={!term && <Button onClick={() => openForm(null)}><Plus size={17}/> Cadastrar fabricante</Button>}/> :
        <div className="table-scroll"><table><thead><tr><th>FABRICANTE</th><th>IDENTIFICADOR</th><th className="col-actions">AÇÕES</th></tr></thead><tbody>{visible.map((item, index) => <tr key={item.id}><td><div className="table-name"><span className={`letter-avatar tone-${index % 3}`}><Building2 size={17}/></span><strong>{item.nome}</strong></div></td><td><code>{item.id.slice(0, 8)}…</code></td><td><div className="action-group"><button title="Editar fabricante" aria-label={`Editar ${item.nome}`} onClick={() => openForm(item)}><Pencil size={17}/></button><button title="Excluir fabricante" aria-label={`Excluir ${item.nome}`} onClick={() => setTarget(item)}><Trash2 size={17}/></button></div></td></tr>)}</tbody></table></div>}
      <div className="table-bottom"><span>Mostrando {visible.length} de {query.data?.length ?? 0} fabricantes</span><Link to="/sorvetes">Explorar sorvetes →</Link></div>
    </div>
    {formOpen && <FabricanteForm key={selected?.id ?? 'new'} item={selected} onClose={() => setFormOpen(false)} onDone={(message) => { setFormOpen(false); setNotice(message); }}/>}
    {target && <ConfirmDialog title="Excluir fabricante?" message={`Você deseja excluir “${target.nome}”? Fabricantes com sorvetes vinculados não podem ser excluídos.`} busy={deleteMutation.isPending} onCancel={() => { setTarget(null); deleteMutation.reset(); }} onConfirm={() => deleteMutation.mutate(target.id)}/>}
    {deleteMutation.error && <ErrorState message={deleteMutation.error.message}/>}
    {notice && <Notice text={notice} onClose={() => setNotice('')}/>}
  </div>;
}
