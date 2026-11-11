const getResolvedApiBaseUrl = (): string => {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  if (envUrl && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  // If running in browser on Vercel or any non-localhost domain without explicit API URL,
  // return empty string for relative /api routing (supported via Next.js rewrites)
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return '';
  }
  return 'http://127.0.0.1:8000';
};

class ApiClient {
  public getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private setTokens(access: string, refresh?: string) {
    if (typeof window === 'undefined') return;
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  }

  public clearTokens() {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
  }

  public getBaseUrl(): string {
    return getResolvedApiBaseUrl();
  }

  public async request<T = unknown>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const baseUrl = this.getBaseUrl();
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = baseUrl ? `${baseUrl}${cleanEndpoint}` : cleanEndpoint;
    const token = this.getAccessToken();

    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    // Don't set Content-Type if sending FormData (browser sets boundary automatically)
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    let response = await fetch(url, config);

    // Handle token expiration & automatic refresh
    if (response.status === 401 && typeof window !== 'undefined') {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken && !endpoint.includes('/token/refresh/')) {
        try {
          const refreshUrl = baseUrl ? `${baseUrl}/api/auth/token/refresh/` : '/api/auth/token/refresh/';
          const refreshRes = await fetch(refreshUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
          });

          if (refreshRes.ok) {
            const data = await refreshRes.json();
            this.setTokens(data.access);
            headers['Authorization'] = `Bearer ${data.access}`;
            response = await fetch(url, { ...config, headers });
          } else {
            this.clearTokens();
          }
        } catch {
          this.clearTokens();
        }
      }
    }

    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (typeof errorData === 'object' && errorData !== null) {
          if (errorData.detail) errorMessage = errorData.detail;
          else if (errorData.error) errorMessage = errorData.error;
          else if (errorData.message) errorMessage = errorData.message;
          else {
            const firstKey = Object.keys(errorData)[0];
            const val = errorData[firstKey];
            errorMessage = Array.isArray(val) ? `${firstKey}: ${val[0]}` : String(val);
          }
        }
      } catch {
        // Not JSON
      }
      throw new Error(errorMessage);
    }

    // Check for empty body / 204
    if (response.status === 204) {
      return {} as T;
    }

    // Check content type
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/pdf') || contentType.includes('application/octet-stream')) {
      const blob = await response.blob();
      return blob as unknown as T;
    }

    return response.json();
  }

  // HTTP Helper Methods
  public get<T>(endpoint: string, options?: RequestInit) {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public post<T>(endpoint: string, body?: unknown, options?: RequestInit) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body),
    });
  }

  public put<T>(endpoint: string, body?: unknown, options?: RequestInit) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body instanceof FormData ? body : JSON.stringify(body),
    });
  }

  public delete<T>(endpoint: string, options?: RequestInit) {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const api = new ApiClient();
