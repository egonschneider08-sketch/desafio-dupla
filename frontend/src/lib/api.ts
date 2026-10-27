export type Fabricante = { id: string; nome: string };
export type Sorvete = { id: string; nome: string; sabor: string; preco: number; fabricante_id: string; fabricante: string };
export type SorvetePayload = Pick<Sorvete, 'nome' | 'sabor' | 'preco' | 'fabricante_id'>;
export type FabricantePayload = Pick<Fabricante, 'nome'>;

const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(API_BASE + path, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options?.headers },
    });
  } catch {
    throw new Error('Não foi possível conectar à API. Verifique se o servidor Flask está ligado.');
  }
  if (response.status === 204) return undefined as T;
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const message = typeof body === 'object' && body !== null && 'error' in body && typeof body.error === 'string'
      ? body.error : 'Não foi possível concluir sua solicitação.';
    throw new Error(message);
  }
  return body as T;
}

export const api = {
  fabricantes: {
    list: () => request<Fabricante[]>('/fabricantes'),
    create: (data: FabricantePayload) => request<Fabricante>('/fabricantes', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: FabricantePayload) => request<Fabricante>(`/fabricantes/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    remove: (id: string) => request<void>(`/fabricantes/${id}`, { method: 'DELETE' }),
  },
  sorvetes: {
    list: (params?: { q?: string; fabricante_id?: string; sabor?: string }) => {
      const query = new URLSearchParams();
      if (params?.q) query.set('q', params.q);
      if (params?.fabricante_id) query.set('fabricante_id', params.fabricante_id);
      if (params?.sabor) query.set('sabor', params.sabor);
      const qs = query.toString();
      return request<Sorvete[]>(`/sorvetes${qs ? '?' + qs : ''}`);
    },
    create: (data: SorvetePayload) => request<Sorvete>('/sorvetes', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: SorvetePayload) => request<Sorvete>(`/sorvetes/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    remove: (id: string) => request<void>(`/sorvetes/${id}`, { method: 'DELETE' }),
  },
};

export const formatPrice = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2 }).format(value);
