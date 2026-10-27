import { describe, expect, it, vi, afterEach } from 'vitest';
import { api, formatPrice } from './api';

afterEach(() => { vi.unstubAllGlobals(); });

describe('Catalog API client', () => {
  it('formats persisted integer prices as whole reais', () => {
    expect(formatPrice(5)).toContain('5,00');
  });

  it('requests the right REST routes', async () => {
    const mock = vi.fn().mockResolvedValue({ status: 200, ok: true, json: async () => [] });
    vi.stubGlobal('fetch', mock);
    expect(await api.sorvetes.list({ q: 'Picolé' })).toEqual([]);
    expect(mock.mock.calls[0][0]).toBe('/api/sorvetes?q=Picol%C3%A9');
  });

  it('preserves backend validation messages', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      status: 409, ok: false, json: async () => ({ error: 'Fabricante já cadastrado.' }),
    }));
    await expect(api.fabricantes.create({ nome: 'Teste' })).rejects.toThrow('Fabricante já cadastrado.');
  });

  it('reports connection problems', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
    await expect(api.fabricantes.list()).rejects.toThrow('Não foi possível conectar');
  });

  it('handles 204 without parsing a body', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ status: 204, ok: true }));
    await expect(api.fabricantes.remove('abc')).resolves.toBeUndefined();
  });
});
