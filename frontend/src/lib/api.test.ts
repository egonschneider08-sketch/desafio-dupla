import { describe, expect, it, vi, afterEach } from 'vitest';

afterEach(() => { vi.unstubAllGlobals(); vi.resetModules(); });

async function freshApi() { return import('./api'); }

describe('Catalog API client and session CSRF', () => {
  it('formats persisted integer prices as whole reais', async () => {
    const { formatPrice } = await freshApi();
    expect(formatPrice(5)).toContain('5,00');
  });

  it('requests the expected REST routes', async () => {
    const mock = vi.fn().mockResolvedValue({ status: 200, ok: true, json: async () => [] });
    vi.stubGlobal('fetch', mock);
    const { api } = await freshApi();
    expect(await api.sorvetes.list({ q: 'Picolé' })).toEqual([]);
    expect(mock.mock.calls[0][0]).toBe('/api/sorvetes?q=Picol%C3%A9');
  });

  it('loads a CSRF token before the first mutation', async () => {
    const mock = vi.fn()
      .mockResolvedValueOnce({ status: 200, ok: true, json: async () => ({ user: null, csrf_token: 'token-123' }) })
      .mockResolvedValueOnce({ status: 201, ok: true, json: async () => ({ id: 'abc', nome: 'Gelados' }) });
    vi.stubGlobal('fetch', mock);
    const { api } = await freshApi();
    expect((await api.fabricantes.create({ nome: 'Gelados' })).nome).toBe('Gelados');
    expect(mock.mock.calls[0][0]).toBe('/api/auth/session');
    expect(mock.mock.calls[1][0]).toBe('/api/fabricantes');
    expect(mock.mock.calls[1][1].headers['X-CSRF-Token']).toBe('token-123');
    expect(mock.mock.calls[1][1].credentials).toBe('same-origin');
  });

  it('updates CSRF token on login and preserves validation errors', async () => {
    const mock = vi.fn()
      .mockResolvedValueOnce({ status: 200, ok: true, json: async () => ({ user: null, csrf_token: 'before' }) })
      .mockResolvedValueOnce({ status: 200, ok: true, json: async () => ({ user: { id:'1', name:'Admin', role:'admin', email:'a@b.co' }, csrf_token: 'after' }) })
      .mockResolvedValueOnce({ status: 409, ok: false, json: async () => ({ error: 'Fabricante já cadastrado.' }) });
    vi.stubGlobal('fetch', mock);
    const { api } = await freshApi();
    await api.auth.login({ email:'a@b.co', password:'UmaSenhaLonga123' });
    await expect(api.fabricantes.create({ nome: 'Teste' })).rejects.toThrow('Fabricante já cadastrado.');
    expect(mock.mock.calls[1][1].headers['X-CSRF-Token']).toBe('before');
    expect(mock.mock.calls[2][1].headers['X-CSRF-Token']).toBe('after');
  });

  it('shows a useful connection error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    const { api } = await freshApi();
    await expect(api.fabricantes.list()).rejects.toThrow('Não foi possível conectar');
  });

  it('handles 204 without parsing a body', async () => {
    const mock = vi.fn()
      .mockResolvedValueOnce({ status: 200, ok: true, json: async () => ({ user: null, csrf_token: 'token' }) })
      .mockResolvedValueOnce({ status: 204, ok: true });
    vi.stubGlobal('fetch', mock);
    const { api } = await freshApi();
    await expect(api.fabricantes.remove('abc')).resolves.toBeUndefined();
    expect(mock.mock.calls[1][1].headers['X-CSRF-Token']).toBe('token');
  });
});
