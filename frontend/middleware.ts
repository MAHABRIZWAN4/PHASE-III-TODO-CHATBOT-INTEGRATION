import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Define protected routes
const protectedRoutes = ["/dashboard", "/chat"];

// Define public routes
const publicRoutes = ["/login", "/signup", "/"];

// Cookie name for auth token
const AUTH_COOKIE_NAME = "auth_token";

/**
 * Get auth token from cookies (for server-side middleware)
 */
function getTokenFromCookie(request: NextRequest): string | null {
  const cookie = request.cookies.get(AUTH_COOKIE_NAME);
  return cookie?.value || null;
}

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = getTokenFromCookie(request);

  console.log('[Middleware] Request:', pathname);
  console.log('[Middleware] Token exists:', !!token);

  // Check if the current route is protected
  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));
  const isPublicRoute = publicRoutes.includes(pathname);

  console.log('[Middleware] Is protected route:', isProtectedRoute);
  console.log('[Middleware] Is public route:', isPublicRoute);

  // Redirect to login if accessing protected route without token
  if (isProtectedRoute && !token) {
    console.log('[Middleware] Redirecting to /login (no token for protected route)');
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirect to dashboard if accessing public routes with valid token (but not root)
  if (isPublicRoute && token && pathname !== "/") {
    console.log('[Middleware] Redirecting to /dashboard (has token on public route)');
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  console.log('[Middleware] Allowing request to proceed');
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
