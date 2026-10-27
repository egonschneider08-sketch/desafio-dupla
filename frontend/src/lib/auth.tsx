/** Authentication state backed by an HttpOnly session cookie. */
import { createContext, useContext, type ReactNode } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api, type AuthSession, type AuthUser, type LoginPayload, type RegistrationPayload } from './api';

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  login: (data: LoginPayload) => Promise<void>;
  register: (data: RegistrationPayload) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const AUTH_KEY = ['auth', 'session'] as const;

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const session = useQuery({ queryKey: AUTH_KEY, queryFn: api.auth.session, retry: false, staleTime: 30_000 });

  async function applyAuthentication(authenticate: () => Promise<AuthSession>) {
    const result = await authenticate();
    queryClient.removeQueries({ queryKey: ['fabricantes'] });
    queryClient.removeQueries({ queryKey: ['sorvetes'] });
    queryClient.setQueryData(AUTH_KEY, result);
  }

  const value: AuthContextValue = {
    user: session.data?.user ?? null,
    loading: session.isLoading,
    error: session.error?.message ?? null,
    login: (data) => applyAuthentication(() => api.auth.login(data)),
    register: (data) => applyAuthentication(() => api.auth.register(data)),
    logout: () => applyAuthentication(api.auth.logout),
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be called within AuthProvider');
  return value;
}
