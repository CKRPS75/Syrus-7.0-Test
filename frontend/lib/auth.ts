export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface RegistrationDetails {
  fullName: string;
  email: string;
  password: string;
}

export interface AuthenticatedUser {
  name?: string;
  email?: string;
}

type AuthOperation = 'LOGIN' | 'REGISTER' | 'RESET' | 'LOGOUT';
type AuthErrorCode =
  | 'INVALID_CREDENTIALS'
  | 'ACCOUNT_EXISTS'
  | 'RESET_NOT_CONFIGURED'
  | 'SERVICE_UNAVAILABLE'
  | 'REQUEST_FAILED';

export class AuthServiceError extends Error {
  constructor(readonly code: AuthErrorCode) {
    super(code);
    this.name = 'AuthServiceError';
  }
}

function configuredEndpoint(operation: AuthOperation): string {
  const endpointPaths: Record<AuthOperation, string> = {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    RESET: '/auth/reset',
    LOGOUT: '/auth/logout',
  };
  const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');
  return `${apiBaseUrl}${endpointPaths[operation]}`;
}

async function post(endpoint: string, payload: object): Promise<Response> {
  try {
    return await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      cache: 'no-store',
      body: JSON.stringify(payload),
    });
  } catch {
    throw new AuthServiceError('REQUEST_FAILED');
  }
}

function assertAccepted(response: Response, operation: AuthOperation): void {
  if (response.ok) return;
  if (operation === 'LOGIN' && (response.status === 401 || response.status === 403)) {
    throw new AuthServiceError('INVALID_CREDENTIALS');
  }
  if (operation === 'REGISTER' && response.status === 409) throw new AuthServiceError('ACCOUNT_EXISTS');
  if (operation === 'RESET' && response.status === 501) throw new AuthServiceError('RESET_NOT_CONFIGURED');
  if (response.status === 503) throw new AuthServiceError('SERVICE_UNAVAILABLE');
  throw new AuthServiceError('REQUEST_FAILED');
}

export async function login(credentials: LoginCredentials): Promise<AuthenticatedUser> {
  const response = await post(configuredEndpoint('LOGIN'), credentials);
  assertAccepted(response, 'LOGIN');

  let data: { user?: AuthenticatedUser };
  try {
    data = await response.json();
  } catch {
    throw new AuthServiceError('REQUEST_FAILED');
  }
  if (!data || typeof data.user !== 'object' || data.user === null) {
    throw new AuthServiceError('REQUEST_FAILED');
  }

  const name = typeof data.user.name === 'string' ? data.user.name : undefined;
  const email = typeof data.user.email === 'string' ? data.user.email : undefined;
  return { name, email };
}

export async function register(details: RegistrationDetails): Promise<void> {
  const response = await post(configuredEndpoint('REGISTER'), details);
  assertAccepted(response, 'REGISTER');
}

export async function requestPasswordReset(email: string): Promise<void> {
  const response = await post(configuredEndpoint('RESET'), { email });
  assertAccepted(response, 'RESET');
}

export async function logout(): Promise<void> {
  const response = await post(configuredEndpoint('LOGOUT'), {});
  assertAccepted(response, 'LOGOUT');
}
