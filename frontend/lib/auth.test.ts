import { afterEach, describe, expect, it, vi } from 'vitest';
import { login, logout, register, requestPasswordReset } from './auth';
import { isValidEmail } from './authValidation';

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe('authentication service', () => {
  it('sends credentials to the backend auth route and requires an accepted user response', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ user: { name: 'Route Planner', email: 'planner@example.com' } }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    vi.stubGlobal('fetch', fetchMock);
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'https://api.example.test/');

    await expect(login({
      email: 'planner@example.com',
      password: 'private-password',
      rememberMe: true,
    })).resolves.toEqual({ name: 'Route Planner', email: 'planner@example.com' });

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.example.test/auth/login',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        cache: 'no-store',
        body: JSON.stringify({
          email: 'planner@example.com',
          password: 'private-password',
          rememberMe: true,
        }),
      }),
    );
  });

  it('maps rejected credentials to a safe authentication error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('internal stack trace', { status: 401 })));
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'https://api.example.test');

    await expect(login({ email: 'person@example.com', password: 'wrong', rememberMe: false }))
      .rejects.toMatchObject({ code: 'INVALID_CREDENTIALS' });
  });

  it('reports registration conflicts and unconfigured reset without exposing server details', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('internal stack trace', { status: 401 })));
    await expect(register({ fullName: 'Route Planner', email: 'person@example.com', password: 'password1' }))
      .rejects.toMatchObject({ code: 'REQUEST_FAILED' });
    await expect(requestPasswordReset('person@example.com'))
      .rejects.toMatchObject({ code: 'REQUEST_FAILED' });

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('internal stack trace', { status: 501 })));
    await expect(requestPasswordReset('person@example.com'))
      .rejects.toMatchObject({ code: 'RESET_NOT_CONFIGURED' });

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('internal stack trace', { status: 409 })));
    await expect(register({ fullName: 'Route Planner', email: 'person@example.com', password: 'password1' }))
      .rejects.toMatchObject({ code: 'ACCOUNT_EXISTS' });
  });

  it('calls the backend logout endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal('fetch', fetchMock);
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'https://api.example.test');

    await expect(logout()).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.example.test/auth/logout',
      expect.objectContaining({ method: 'POST', credentials: 'include', body: '{}' }),
    );

  });

  it('does not expose response details when registration or reset fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('sensitive backend details', { status: 500 })));
    await expect(register({ fullName: 'Route Planner', email: 'person@example.com', password: 'password1' }))
      .rejects.toMatchObject({ code: 'REQUEST_FAILED' });
    await expect(requestPasswordReset('person@example.com'))
      .rejects.toMatchObject({ code: 'REQUEST_FAILED' });
  });
});

describe('email validation', () => {
  it('accepts valid email addresses and rejects empty or malformed values', () => {
    expect(isValidEmail('person@example.com')).toBe(true);
    expect(isValidEmail('')).toBe(false);
    expect(isValidEmail('person.example.com')).toBe(false);
    expect(isValidEmail('person@localhost')).toBe(false);
  });
});
