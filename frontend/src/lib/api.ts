export type Fabricante = { id: string; nome: string };
export type Sorvete = { id: string; nome: string; sabor: string; preco: number; fabricante_id: string; fabricante: string };
export type SorvetePayload = Pick<Sorvete, 'nome' | 'sabor' | 'preco' | 'fabricante_id'>;
export type FabricantePayload = Pick<Fabricante, 'nome'>;

export type AuthUser = { id: string; name: string; email: string; role: 'viewer' | 'admin' };
export type AuthSession = { user: AuthUser | null; csrf_token: string };
export type LoginPayload = { email: string; password: string };
export type RegistrationPayload = LoginPayload & { name: string };

const API_BASE = '/api';
let csrfToken: string | null = null;

function updateCsrf(body: unknown) {
  if (typeof body === 'object' && body !== null && 'csrf_token' in body && typeof body.csrf_token === 'string') {
    csrfToken = body.csrf_token;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const method = (options?.method || 'GET').toUpperCase();
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method) && csrfToken === null) {
    await request<AuthSession>('/auth/session');
  }
  let response: Response;
  try {
    response = await fetch(API_BASE + path, {
      ...options,
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        ...(!['GET', 'HEAD', 'OPTIONS'].includes(method) && csrfToken
          ? { 'X-CSRF-Token': csrfToken } : {}),
        ...options?.headers,
      },
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
  updateCsrf(body);
  return body as T;
}

export const api = {
  auth: {
    session: () => request<AuthSession>('/auth/session'),
    register: (data: RegistrationPayload) =>
      request<AuthSession>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data: LoginPayload) =>
      request<AuthSession>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    logout: () => request<AuthSession>('/auth/logout', { method: 'POST' }),
  },
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
