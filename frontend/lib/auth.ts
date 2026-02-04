// Better Auth configuration for frontend

// Token storage and management utilities
export const AUTH_TOKEN_KEY = "auth_token";
export const AUTH_USER_KEY = "auth_user";
export const AUTH_COOKIE_NAME = "auth_token"; // For middleware to read server-side

export interface AuthUser {
  id: string;
  email: string;
  name?: string;
}

export interface AuthToken {
  token: string;
  expiresAt: number;
}

/**
 * Get stored authentication token
 */
export function getAuthToken(): string | null {
  console.log('[Auth] getAuthToken called');
  if (typeof window === "undefined") {
    console.log('[Auth] getAuthToken: window is undefined (SSR)');
    return null;
  }
  const tokenData = localStorage.getItem(AUTH_TOKEN_KEY);
  console.log('[Auth] getAuthToken: tokenData from localStorage:', tokenData);
  if (!tokenData) {
    console.log('[Auth] getAuthToken: no token data found');
    return null;
  }

  try {
    const token: AuthToken = JSON.parse(tokenData);
    console.log('[Auth] getAuthToken: parsed token:', { expiresAt: token.expiresAt, now: Date.now() });
    // Check if token is expired
    if (token.expiresAt < Date.now()) {
      console.log('[Auth] getAuthToken: token expired');
      removeAuthToken();
      return null;
    }
    console.log('[Auth] getAuthToken: returning valid token');
    return token.token;
  } catch (e) {
    console.error('[Auth] getAuthToken: error parsing token:', e);
    removeAuthToken();
    return null;
  }
}

/**
 * Set authentication token (also sets cookie for middleware)
 */
export function setAuthToken(token: string, expiresIn: number = 604800000): void {
  // Default 7 days in milliseconds
  console.log('[Auth] setAuthToken called with token:', token?.substring(0, 20) + '...');
  if (typeof window === "undefined") {
    console.log('[Auth] setAuthToken: window is undefined (SSR)');
    return;
  }

  const tokenData: AuthToken = {
    token,
    expiresAt: Date.now() + expiresIn,
  };
  console.log('[Auth] setAuthToken: storing token data:', { expiresAt: tokenData.expiresAt, now: Date.now() });
  localStorage.setItem(AUTH_TOKEN_KEY, JSON.stringify(tokenData));
  console.log('[Auth] setAuthToken: token stored in localStorage');

  // Also set cookie for server-side middleware to read
  document.cookie = `${AUTH_COOKIE_NAME}=${token}; path=/; max-age=${Math.floor(expiresIn / 1000)}; SameSite=Lax`;
  console.log('[Auth] setAuthToken: cookie set');
}

/**
 * Remove authentication token
 */
export function removeAuthToken(): void {
  console.log('[Auth] removeAuthToken called');
  if (typeof window === "undefined") {
    console.log('[Auth] removeAuthToken: window is undefined (SSR)');
    return;
  }
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
  console.log('[Auth] removeAuthToken: removed from localStorage');

  // Clear the auth cookie
  document.cookie = `${AUTH_COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax`;
  console.log('[Auth] removeAuthToken: cookie cleared');
}

/**
 * Get stored user information
 */
export function getAuthUser(): AuthUser | null {
  console.log('[Auth] getAuthUser called');
  if (typeof window === "undefined") {
    console.log('[Auth] getAuthUser: window is undefined (SSR)');
    return null;
  }
  const userData = localStorage.getItem(AUTH_USER_KEY);
  console.log('[Auth] getAuthUser: userData from localStorage:', userData);
  if (!userData) {
    console.log('[Auth] getAuthUser: no user data found');
    return null;
  }

  try {
    const user = JSON.parse(userData);
    console.log('[Auth] getAuthUser: parsed user:', user);
    return user;
  } catch (e) {
    console.error('[Auth] getAuthUser: error parsing user data:', e);
    return null;
  }
}

/**
 * Set user information
 */
export function setAuthUser(user: AuthUser): void {
  console.log('[Auth] setAuthUser called with user:', user);
  if (typeof window === "undefined") {
    console.log('[Auth] setAuthUser: window is undefined (SSR)');
    return;
  }
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  console.log('[Auth] setAuthUser: user stored in localStorage');
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}

/**
 * Logout user (clears auth data)
 * Note: Redirect should be handled by the calling component
 */
export function logout(): void {
  removeAuthToken();
}
