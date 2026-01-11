import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Define protected routes
const protectedRoutes = ["/dashboard"];

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

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = getTokenFromCookie(request);

  // Check if the current route is protected
  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route));
  const isPublicRoute = publicRoutes.includes(pathname);

  // Redirect to login if accessing protected route without token
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirect to dashboard if accessing public routes with valid token (but not root)
  if (isPublicRoute && token && pathname !== "/") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
